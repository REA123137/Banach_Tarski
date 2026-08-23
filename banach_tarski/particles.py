"""
Point-cloud machinery.

The pieces of a paradoxical decomposition are not solids - they are unmeasurable
clouds of points.  The film says so in words and shows it with dust: every time
a set is "cut", it is cut into particles, never into slices of cheese.

``Dust`` is a layered point cloud (a bright core inside two soft bloom layers)
that still renders fast at 60 fps, ``DustMorph`` flows it from one arrangement
to another, and ``depth_shade`` fades the particles on the far side of a solid
so a cloud reads as a ball instead of a disc of confetti.
"""

from __future__ import annotations

import numpy as np
from manim import *

from .style import PAPER

# Bloom layers, as (size multiplier, brightness multiplier), painted back to front.
# Only worth switching on for sparse clouds - a dense one just paints a disc.
_BLOOM = ((4.5, 0.10), (2.2, 0.22))


def px(base: float) -> float:
    """
    Particle size in pixels.

    Manim draws point clouds with a pixel-space thickness, so a fixed number
    would shrink as the render resolution rises.  Sizes in this project are
    quoted against a 720p reference and scaled from there.
    """
    return float(base) * config.pixel_height / 720.0


def _to_rgba(colors, n: int, opacity: float = 1.0) -> np.ndarray:
    """
    One colour, or a per-point sequence, as an (n,4) array.

    Manim's point-cloud renderer writes pixels straight into the frame buffer
    instead of blending them, so a low alpha punches a transparent hole rather
    than dimming the particle.  We therefore carry "opacity" in the RGB channels
    - premultiplied against the black canvas - and keep alpha pinned at 1.
    """
    if isinstance(colors, (str, ManimColor)):
        colors = [colors] * n
    colors = list(colors)
    if len(colors) != n:
        colors = (colors * (n // len(colors) + 1))[:n]
    rgba = np.array([ManimColor(c).to_rgba() for c in colors], dtype=float)
    rgba[:, :3] *= float(opacity)
    rgba[:, 3] = 1.0
    return rgba


class Dust(PGroup):
    """
    A cloud of coloured points with a fake bloom around it.

    The layers all carry the same point array; only their size and opacity
    differ, which is what sells the glow on a black canvas.
    """

    def __init__(self, points, colors=PAPER, size: float = 3.4, opacity: float = 1.0,
                 bloom: bool = False, **kw):
        pts = np.asarray(points, dtype=float).reshape(-1, 3)
        rgba = _to_rgba(colors, len(pts), opacity)

        layers = []
        if bloom:
            for mult, op in _BLOOM:
                layer = PMobject(stroke_width=px(size * mult))
                layer.add_points(pts.copy(), rgbas=rgba * np.array([op, op, op, 1]))
                layers.append(layer)
        core = PMobject(stroke_width=px(size))
        core.add_points(pts.copy(), rgbas=rgba.copy())
        layers.append(core)

        super().__init__(*layers, **kw)
        self.core = core
        self.bloom_layers = layers[:-1]
        self._bloom_ops = [op for _, op in _BLOOM] if bloom else []
        self.base_rgbas = rgba.copy()
        self._shade = None
        self._spec = None

    # -- state -------------------------------------------------------------
    @property
    def pts(self) -> np.ndarray:
        return self.core.points

    @property
    def n(self) -> int:
        return len(self.core.points)

    def write_points(self, pts: np.ndarray) -> "Dust":
        for layer in self.submobjects:
            layer.points = pts
        return self

    def write_rgbas(self, rgba: np.ndarray) -> "Dust":
        self.base_rgbas = rgba
        if self._shade is None:
            shaded = rgba
        else:
            shaded = rgba.copy()
            shaded[:, :3] *= self._shade[:, None]
            if self._spec is not None:
                # A little specular lift on the particles nearest the camera, so
                # the near face of a cloud sparkles instead of flattening.  The
                # lift is multiplicative, which keeps each particle's hue - a
                # blend toward white turns dim colours into grey confetti.
                shaded[:, :3] = np.clip(
                    shaded[:, :3] * (1.0 + 1.7 * self._spec[:, None]), 0.0, 1.0
                )
        self.core.rgbas = shaded
        for layer, op in zip(self.bloom_layers, self._bloom_ops):
            layer.rgbas = shaded * np.array([op, op, op, 1])
        return self

    def recolor(self, colors, opacity: float = 1.0) -> "Dust":
        return self.write_rgbas(_to_rgba(colors, self.n, opacity))

    def mute(self, mask, opacity: float) -> "Dust":
        """
        Push a subset toward black so the rest of the cloud reads as figure.

        (Not called ``dim`` - Mobject already uses that name for the ambient
        dimension, and shadowing it breaks ``.animate``.)
        """
        rgba = self.base_rgbas.copy()
        rgba[np.asarray(mask), :3] *= opacity
        return self.write_rgbas(rgba)

    def subset(self, mask) -> "Dust":
        mask = np.asarray(mask)
        d = Dust(self.pts[mask], PAPER,
                 size=self.core.stroke_width * 720.0 / config.pixel_height)
        d.write_rgbas(self.base_rgbas[mask].copy())
        return d

    # -- depth ------------------------------------------------------------
    def depth_shade(self, scene, radius: float = 1.6, floor: float = 0.12,
                    gamma: float = 1.0, highlight: float = 0.5) -> "Dust":
        """
        Fade whatever is pointing away from the camera.

        Reads the live camera angles each frame, so it keeps working while the
        camera orbits.  Purely cosmetic, and the reason a dust ball reads round.
        """
        cam = scene.camera

        def update(mob: "Dust"):
            phi = cam.get_phi()
            theta = cam.get_theta()
            view = np.array(
                [np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)]
            )
            # Depth is measured from the cloud's own centre, so a cloud parked
            # off to one side is still lit as a ball rather than as a slab.
            depth = (mob.pts - mob.pts.mean(axis=0)) @ view
            t = np.clip((depth + radius) / (2 * radius), 0.0, 1.0) ** gamma
            mob._shade = floor + (1.0 - floor) * t
            mob._spec = np.clip((t - 0.74) / 0.26, 0.0, 1.0) ** 2 * highlight
            mob.write_rgbas(mob.base_rgbas)

        update(self)
        self.add_updater(update)
        return self


class DustMorph(Animation):
    """
    Fly every particle from where it is to a target position.

    ``swirl`` bends the paths into arcs so the motion reads as a flow rather
    than a translation; ``stagger`` gives each particle its own small delay so
    the cloud arrives like a wave instead of a block.
    """

    def __init__(self, dust: Dust, target_points, swirl: float = 0.0,
                 stagger: float = 0.35, rgbas=None, seed: int = 5, **kw):
        kw.setdefault("run_time", 2.4)
        kw.setdefault("rate_func", linear)
        super().__init__(dust, suspend_mobject_updating=False, **kw)
        self.start_points = dust.pts.copy()
        self.target_points = np.asarray(target_points, dtype=float).reshape(-1, 3)
        if len(self.target_points) != len(self.start_points):
            raise ValueError(
                f"point counts must match: {len(self.start_points)} -> {len(self.target_points)}"
            )
        self.start_rgbas = dust.base_rgbas.copy()
        self.target_rgbas = None if rgbas is None else _to_rgba(rgbas, len(self.start_points))
        self.swirl = swirl
        rng = np.random.default_rng(seed)
        self.delay = rng.uniform(0, max(stagger, 1e-9), size=len(self.start_points))
        self.span = max(1.0 - self.delay.max(), 1e-6)

    def interpolate_mobject(self, alpha: float) -> None:
        a = self.rate_func(alpha)
        t = np.clip((a - self.delay) / self.span, 0.0, 1.0)
        s = (t * t * (3 - 2 * t))[:, None]  # smoothstep, per particle
        pts = self.start_points * (1 - s) + self.target_points * s
        if self.swirl:
            travel = self.target_points - self.start_points
            norm = np.linalg.norm(travel, axis=1, keepdims=True) + 1e-9
            perp = np.cross(travel / norm, np.array([0.0, 0.0, 1.0]))
            plen = np.linalg.norm(perp, axis=1, keepdims=True)
            perp = np.where(plen > 1e-6, perp / (plen + 1e-9), np.array([0.0, 1.0, 0.0]))
            pts = pts + perp * np.sin(np.pi * s) * self.swirl
        self.mobject.write_points(pts)
        if self.target_rgbas is not None:
            self.mobject.write_rgbas(self.start_rgbas * (1 - s) + self.target_rgbas * s)


class DustRecolor(Animation):
    """Cross-fade the colours of a cloud without moving it."""

    def __init__(self, dust: Dust, rgbas, opacity: float = 1.0, **kw):
        kw.setdefault("run_time", 1.2)
        super().__init__(dust, suspend_mobject_updating=False, **kw)
        self.start_rgbas = dust.base_rgbas.copy()
        self.target_rgbas = _to_rgba(rgbas, dust.n, opacity)

    def interpolate_mobject(self, alpha: float) -> None:
        a = self.rate_func(alpha)
        self.mobject.write_rgbas(self.start_rgbas * (1 - a) + self.target_rgbas * a)


class DustRotate(Animation):
    """
    Turn a cloud by a rotation matrix - the group acting, made visible.

    The turn happens about ``about`` (by default the cloud's own centre), so a
    cloud parked away from the origin spins in place instead of orbiting.
    The path is the geodesic: the matrix is decomposed to axis and angle, and
    the angle is swept, which is what a real turn looks like.
    """

    def __init__(self, dust: Dust, matrix, about=None, **kw):
        kw.setdefault("run_time", 1.8)
        kw.setdefault("rate_func", rate_functions.ease_in_out_sine)
        super().__init__(dust, suspend_mobject_updating=False, **kw)
        self.start_points = dust.pts.copy()
        self.about = (self.start_points.mean(axis=0) if about is None
                      else np.asarray(about, dtype=float))
        self.axis, self.angle = _axis_angle(np.asarray(matrix, dtype=float))

    def interpolate_mobject(self, alpha: float) -> None:
        R = _rodrigues(self.axis, self.angle * self.rate_func(alpha))
        self.mobject.write_points((self.start_points - self.about) @ R.T + self.about)


def _axis_angle(R: np.ndarray) -> tuple[np.ndarray, float]:
    angle = float(np.arccos(np.clip((np.trace(R) - 1) / 2, -1.0, 1.0)))
    if abs(angle) < 1e-9:
        return np.array([0.0, 0.0, 1.0]), 0.0
    axis = np.array(
        [R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]
    ) / (2 * np.sin(angle))
    return axis, angle


def _rodrigues(axis: np.ndarray, angle: float) -> np.ndarray:
    K = np.array(
        [[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]]
    )
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)

