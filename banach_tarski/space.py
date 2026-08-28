"""A small hand-rolled 3D stage.

manim's own 3D camera projects every vertex of every bezier, which is both
slow and unstable when a scene holds tens of thousands of points.  The film
needs the opposite: a very large number of *dots*, moving smoothly, with
depth fog, on black.

So the projection is done here, in numpy, and the result is handed to flat 2D
mobjects — ``PMobject`` for clouds (one draw call per depth band, per-point
colour, thousands of points for free) and plain polylines for wireframes.

Everything on a :class:`Stage` is re-projected once per frame from a single
updater, so a camera move is one ``ValueTracker`` away.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from manim import (
    ORIGIN,
    PI,
    Dot,
    Group,
    Mobject,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    rate_functions,
)
from manim.mobject.types.point_cloud_mobject import PMobject

from . import theme

# --------------------------------------------------------------------------
# The camera
# --------------------------------------------------------------------------


@dataclass
class View:
    """Orbit camera: yaw and pitch in radians, ``distance`` in world radii."""

    yaw: float = -0.55
    pitch: float = 0.32
    roll: float = 0.0
    distance: float = 9.0
    scale: float = 2.2
    center: np.ndarray = field(default_factory=lambda: np.zeros(3))
    origin: np.ndarray = field(default_factory=lambda: np.zeros(3))

    def basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        cy, sy = np.cos(self.yaw), np.sin(self.yaw)
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)
        forward = np.array([cp * cy, cp * sy, sp])          # origin -> camera
        right = np.array([-sy, cy, 0.0])
        up = np.cross(forward, right)
        if self.roll:
            cr, sr = np.cos(self.roll), np.sin(self.roll)
            right, up = cr * right + sr * up, -sr * right + cr * up
        return right, up, forward

    def project(self, points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(N,3) world points -> ((N,3) screen points with z=0, (N,) depth)."""
        pts = np.atleast_2d(np.asarray(points, dtype=float)) - self.center
        right, up, forward = self.basis()
        x = pts @ right
        y = pts @ up
        z = pts @ forward
        depth = np.maximum(self.distance - z, 0.25)
        f = self.scale * self.distance / depth
        screen = np.zeros((len(pts), 3))
        screen[:, 0] = x * f
        screen[:, 1] = y * f
        return screen + self.origin, depth

    def project_one(self, point) -> tuple[np.ndarray, float]:
        s, d = self.project(np.asarray(point, dtype=float)[None, :])
        return s[0], float(d[0])

    def copy(self) -> "View":
        return View(
            yaw=self.yaw,
            pitch=self.pitch,
            roll=self.roll,
            distance=self.distance,
            scale=self.scale,
            center=self.center.copy(),
            origin=self.origin.copy(),
        )


# --------------------------------------------------------------------------
# Things that live on the stage
# --------------------------------------------------------------------------


class Solid:
    """Anything that knows how to redraw itself for a given :class:`View`."""

    mobject: Mobject

    def sync(self, view: View) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class Cloud(Solid):
    """A dust of points, drawn as a handful of depth-sorted point clouds.

    ``bands`` slices the cloud front-to-back; each slice gets its own dot size
    and its own fog, which is what gives the ball its volume on black.
    """

    def __init__(
        self,
        points: np.ndarray,
        colors=None,
        bands: int = 5,
        size: float = 2.6,
        size_far: float = 1.1,
        fog: float = 0.62,
        opacity: float = 1.0,
        cull_back: float = 0.0,
    ):
        self.points = np.asarray(points, dtype=float).reshape(-1, 3)
        n = len(self.points)
        self.colors = self._as_rgb(colors, n)
        self.alpha = np.ones(n)
        self.visible = np.ones(n, dtype=bool)
        self.bands = bands
        self.size = size
        self.size_far = size_far
        self.fog = fog
        self.opacity = opacity
        self.cull_back = cull_back
        self.layers = [PMobject(stroke_width=size) for _ in range(bands)]
        self.mobject = Group(*self.layers)

    # -- colour plumbing ---------------------------------------------------
    @staticmethod
    def _as_rgb(colors, n) -> np.ndarray:
        from manim.utils.color import ManimColor

        if colors is None:
            colors = theme.INK
        if isinstance(colors, str):
            rgb = np.array(ManimColor(colors).to_rgb())
            return np.tile(rgb, (n, 1))
        colors = list(colors)
        if len(colors) == n and isinstance(colors[0], str):
            return np.array([ManimColor(c).to_rgb() for c in colors])
        return np.asarray(colors, dtype=float).reshape(n, 3)

    def set_colors(self, colors) -> None:
        self.colors = self._as_rgb(colors, len(self.points))

    def set_color_where(self, mask, color) -> None:
        from manim.utils.color import ManimColor

        self.colors[mask] = np.array(ManimColor(color).to_rgb())

    # -- drawing -----------------------------------------------------------
    def sync(self, view: View) -> None:
        if len(self.points) == 0:
            for layer in self.layers:
                layer.points = np.zeros((0, 3))
                layer.rgbas = np.zeros((0, 4))
            return
        screen, depth = view.project(self.points)
        near, far = depth.min(), depth.max()
        span = max(far - near, 1e-6)
        t = (depth - near) / span                      # 0 near, 1 far
        shade = (1.0 - self.fog * t) ** 1.4
        alpha = np.clip(shade * self.alpha * self.opacity, 0.0, 1.0)
        if self.cull_back:
            alpha = np.where(t > 0.5, alpha * (1.0 - self.cull_back), alpha)
        alpha = np.where(self.visible, alpha, 0.0)

        # The cairo renderer writes point-cloud pixels straight into the frame
        # buffer: it never blends, so an rgba alpha would be dropped on export
        # and a faded point would come out at full brightness.  The film is
        # drawn on pure black, so compositing is just a multiply — premultiply
        # here, and drop the points that have gone dark rather than letting
        # them punch black holes through the dust behind them.
        keep = np.flatnonzero(alpha > 0.015)
        order = keep[np.argsort(-depth[keep])]         # far first, so near draws on top
        chunks = np.array_split(order, self.bands)
        for i, (layer, idx) in enumerate(zip(self.layers, chunks)):
            u = i / max(self.bands - 1, 1)
            layer.stroke_width = self.size_far + (self.size - self.size_far) * u
            layer.points = screen[idx]
            rgba = np.ones((len(idx), 4))
            rgba[:, :3] = self.colors[idx] * alpha[idx][:, None]
            layer.rgbas = rgba


class Wire(Solid):
    """A 3D polyline (great circle, axis, meridian) drawn as a flat VMobject."""

    def __init__(
        self,
        points: np.ndarray,
        color: str = theme.GHOST,
        width: float = 1.6,
        opacity: float = 1.0,
        closed: bool = True,
        depth_fade: float = 0.0,
    ):
        self.points3d = np.asarray(points, dtype=float).reshape(-1, 3)
        self.closed = closed
        self.depth_fade = depth_fade
        self.mobject = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
        self.mobject.set_fill(opacity=0)

    def sync(self, view: View) -> None:
        screen, depth = view.project(self.points3d)
        pts = np.vstack([screen, screen[:1]]) if self.closed else screen
        self.mobject.set_points_as_corners(pts)
        if self.depth_fade:
            near, far = depth.min(), depth.max()
            t = (depth.mean() - near) / max(far - near, 1e-6)
            self.mobject.set_stroke(opacity=1.0 - self.depth_fade * t)


class Marker(Solid):
    """A single named point of space: a pole, a representative, a dart."""

    def __init__(
        self,
        point,
        color: str = theme.INK,
        radius: float = 0.06,
        label: str | None = None,
        label_size: float = 26,
        label_shift=None,
        halo: float = 0.0,
    ):
        self.point3d = np.asarray(point, dtype=float)
        self.radius = radius
        self.dot = Dot(radius=radius, color=color)
        parts = [self.dot]
        self.halo = None
        if halo:
            self.halo = Dot(radius=radius * halo, color=color).set_opacity(0.16)
            parts.insert(0, self.halo)
        self.label = None
        if label:
            self.label = theme.body(label, size=label_size, color=color)
            self.label_shift = label_shift if label_shift is not None else np.array([0.0, 0.3, 0.0])
            parts.append(self.label)
        self.mobject = VGroup(*parts)

    def sync(self, view: View) -> None:
        screen, depth = view.project(self.point3d[None, :])
        p = screen[0]
        self.dot.move_to(p)
        if self.halo is not None:
            self.halo.move_to(p)
        if self.label is not None:
            self.label.move_to(p + self.label_shift)


class Stage:
    """Holds a view and every solid drawn through it.

    Add ``stage.mobject`` to the scene once; a single updater keeps the whole
    3D world in sync, so animating the camera is just moving ``stage.view``.
    """

    def __init__(self, view: View | None = None):
        self.view = view or View()
        self.solids: list[Solid] = []
        self.mobject = Group()
        self._updater_installed = False

    def add(self, *solids: Solid):
        for s in solids:
            self.solids.append(s)
            self.mobject.add(s.mobject)
        self.sync()
        return solids[0] if len(solids) == 1 else solids

    def remove(self, *solids: Solid):
        for s in solids:
            if s in self.solids:
                self.solids.remove(s)
                self.mobject.remove(s.mobject)

    def sync(self, *_):
        for s in self.solids:
            s.sync(self.view)

    def install(self, scene, fit: bool = True, margin: float = 0.14):
        if fit:
            self.fit(margin)
        scene.add(self.mobject)
        if not self._updater_installed:
            self.mobject.add_updater(self.sync)
            self._updater_installed = True
        return self

    def fit(self, margin: float = 0.14, spread: float = 1.0):
        """Shrink and centre the view until the geometry sits inside the band.

        Text lives in the head and foot bands and geometry in the middle one;
        this is what keeps the second from growing into the first.  ``spread``
        declares how much further the contents will travel later in the scene —
        a scene whose pieces fly apart to twice their radius passes ``2.0``.
        """
        self.sync()
        # a Group holds no points of its own, so ask the family
        if not any(m.has_points() for m in self.mobject.get_family()):
            return self
        top, bottom = self.mobject.get_top()[1], self.mobject.get_bottom()[1]
        centre = (top + bottom) / 2.0
        height = (top - bottom) * spread
        limit = theme.STAGE_HEIGHT - 2 * margin
        if height > limit and height > 1e-6:
            self.view.scale *= limit / height
            self.sync()
            top, bottom = self.mobject.get_top()[1], self.mobject.get_bottom()[1]
            centre = (top + bottom) / 2.0
        self.view.origin = self.view.origin + np.array([0.0, -centre, 0.0])
        self.sync()
        return self

    def freeze(self):
        self.mobject.remove_updater(self.sync)
        self._updater_installed = False

    # -- camera moves ------------------------------------------------------
    def orbit(self, d_yaw=0.0, d_pitch=0.0, d_scale=0.0, run_time=3.0, rate=None):
        start = self.view.copy()

        def upd(_m, alpha):
            self.view.yaw = start.yaw + d_yaw * alpha
            self.view.pitch = start.pitch + d_pitch * alpha
            self.view.scale = start.scale + d_scale * alpha
            self.sync()

        return UpdateFromAlphaFunc(
            self.mobject, upd, run_time=run_time, rate_func=rate or theme.EASE
        )

    def move_to_view(self, target: View, run_time=2.0, rate=None):
        start = self.view.copy()

        def upd(_m, alpha):
            self.view.yaw = start.yaw + (target.yaw - start.yaw) * alpha
            self.view.pitch = start.pitch + (target.pitch - start.pitch) * alpha
            self.view.roll = start.roll + (target.roll - start.roll) * alpha
            self.view.scale = start.scale + (target.scale - start.scale) * alpha
            self.view.distance = start.distance + (target.distance - start.distance) * alpha
            self.view.center = start.center + (target.center - start.center) * alpha
            self.view.origin = start.origin + (target.origin - start.origin) * alpha
            self.sync()

        return UpdateFromAlphaFunc(
            self.mobject, upd, run_time=run_time, rate_func=rate or theme.EASE
        )

    def spin(self, scene, speed=0.18):
        """A slow permanent drift, for scenes that must never sit still."""

        def upd(_m, dt):
            self.view.yaw += speed * dt
            self.sync()

        self.mobject.add_updater(upd)
        return upd


# --------------------------------------------------------------------------
# Geometry generators
# --------------------------------------------------------------------------


def sphere_points(n: int, radius: float = 1.0, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, 3))
    v /= np.linalg.norm(v, axis=1)[:, None]
    return v * radius


def ball_points(n: int, radius: float = 1.0, seed: int = 0, shell: float = 0.0) -> np.ndarray:
    """Uniform in the ball.  ``shell`` biases points towards the surface."""
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, 3))
    v /= np.linalg.norm(v, axis=1)[:, None]
    u = rng.random(n) ** (1.0 / 3.0)
    if shell:
        u = u * (1 - shell) + shell
    return v * (u * radius)[:, None]


def great_circle(normal, radius: float = 1.0, samples: int = 180) -> np.ndarray:
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    helper = np.array([0.0, 0.0, 1.0])
    if abs(float(n @ helper)) > 0.9:
        helper = np.array([1.0, 0.0, 0.0])
    u = np.cross(n, helper)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    t = np.linspace(0, 2 * np.pi, samples, endpoint=False)
    return radius * (np.cos(t)[:, None] * u + np.sin(t)[:, None] * v)


def circle_on_axis(axis, height: float, radius: float = 1.0, samples: int = 180) -> np.ndarray:
    """The circle traced by a point at ``height`` along ``axis`` when spun."""
    a = np.asarray(axis, dtype=float)
    a = a / np.linalg.norm(a)
    r = np.sqrt(max(radius**2 - height**2, 0.0))
    helper = np.array([0.0, 0.0, 1.0])
    if abs(float(a @ helper)) > 0.9:
        helper = np.array([1.0, 0.0, 0.0])
    u = np.cross(a, helper)
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    t = np.linspace(0, 2 * np.pi, samples, endpoint=False)
    return a * height + r * (np.cos(t)[:, None] * u + np.sin(t)[:, None] * v)


def wire_sphere(
    radius: float = 1.0,
    meridians: int = 12,
    parallels: int = 7,
    color: str = theme.GHOST,
    width: float = 1.2,
    samples: int = 120,
) -> list[Wire]:
    """The ghost wireframe that marks where the original ball stood."""
    wires: list[Wire] = []
    for k in range(meridians):
        ang = np.pi * k / meridians
        normal = np.array([np.cos(ang), np.sin(ang), 0.0])
        wires.append(Wire(great_circle(normal, radius, samples), color=color, width=width))
    for k in range(1, parallels + 1):
        z = radius * np.cos(np.pi * k / (parallels + 1))
        wires.append(
            Wire(circle_on_axis([0, 0, 1], z, radius, samples), color=color, width=width)
        )
    return wires


def axis_segment(axis, radius: float = 1.25) -> np.ndarray:
    a = np.asarray(axis, dtype=float)
    a = a / np.linalg.norm(a)
    return np.array([-a * radius, a * radius])


def ball_cloud(
    n: int = 20000,
    color: str = theme.C_A,
    radius: float = 1.0,
    seed: int = 2,
    shell: float = 0.35,
    size: float = 2.4,
    size_far: float = 0.9,
    fog: float = 0.85,
) -> Cloud:
    """The house look for a solid ball of dust: a visible rim, real depth."""
    return Cloud(
        ball_points(n, radius=radius, seed=seed, shell=shell),
        colors=color,
        size=size,
        size_far=size_far,
        fog=fog,
        bands=7,
    )


def sphere_cloud(
    n: int = 9000,
    color: str = theme.INK,
    radius: float = 1.0,
    seed: int = 5,
    size: float = 2.6,
    size_far: float = 0.9,
    fog: float = 0.8,
) -> Cloud:
    return Cloud(
        sphere_points(n, radius=radius, seed=seed),
        colors=color,
        size=size,
        size_far=size_far,
        fog=fog,
        bands=7,
    )


# --------------------------------------------------------------------------
# Partitions, and moving clouds about
# --------------------------------------------------------------------------


def pseudo_partition(points: np.ndarray, parts: int = 4, seed: int = 0) -> np.ndarray:
    """Label every point with one of ``parts`` classes, densely interleaved.

    The genuine pieces of the paradox come from the axiom of choice and cannot
    be computed.  What *can* be reproduced honestly is the property that makes
    them impossible to draw as regions: each piece is everywhere present and
    everywhere absent.  Slicing space by an irrational frequency gives exactly
    that — zoom in as far as you like and all four labels are still there.
    """
    pts = np.asarray(points, dtype=float).reshape(-1, 3)
    rng = np.random.default_rng(seed)
    freqs = np.array([37.0, 61.0, 89.0]) * (1.0 + 0.13 * rng.random(3))
    phase = pts @ freqs + 0.5 * np.sin(pts @ (freqs * 2.7))
    return np.floor(phase).astype(int) % parts


def axis_angle(matrix: np.ndarray) -> tuple[np.ndarray, float]:
    """Decompose a rotation into (unit axis, angle) so it can be played out."""
    m = np.asarray(matrix, dtype=float)
    angle = float(np.arccos(np.clip((np.trace(m) - 1.0) / 2.0, -1.0, 1.0)))
    if angle < 1e-9:
        return np.array([0.0, 0.0, 1.0]), 0.0
    axis = np.array([m[2, 1] - m[1, 2], m[0, 2] - m[2, 0], m[1, 0] - m[0, 1]])
    n = np.linalg.norm(axis)
    if n < 1e-9:  # angle == pi
        vals, vecs = np.linalg.eig(m)
        idx = int(np.argmin(np.abs(vals - 1.0)))
        axis = np.real(vecs[:, idx])
        n = np.linalg.norm(axis)
    return axis / n, angle


def rotate_cloud(cloud: Cloud, matrix: np.ndarray, run_time: float = 2.0, rate=None, about=None):
    """Play a rotation as a genuine rigid motion, not as a morph."""
    from .rotations import rotation_about

    axis, angle = axis_angle(matrix)
    start = cloud.points.copy()
    pivot = np.zeros(3) if about is None else np.asarray(about, dtype=float)

    def upd(_m, alpha):
        r = rotation_about(axis, angle * alpha)
        cloud.points = (start - pivot) @ r.T + pivot

    return UpdateFromAlphaFunc(
        cloud.mobject, upd, run_time=run_time, rate_func=rate or theme.EASE
    )


def move_cloud(cloud: Cloud, target: np.ndarray, run_time: float = 2.0, rate=None, arc: float = 0.0):
    """Morph a cloud onto new positions, optionally along a bulging path."""
    start = cloud.points.copy()
    target = np.asarray(target, dtype=float).reshape(-1, 3)

    def upd(_m, alpha):
        pts = start + (target - start) * alpha
        if arc:
            bulge = np.sin(np.pi * alpha) * arc
            normals = start - start.mean(axis=0)
            n = np.linalg.norm(normals, axis=1)[:, None]
            normals = np.divide(normals, np.maximum(n, 1e-9))
            pts = pts + normals * bulge
        cloud.points = pts

    return UpdateFromAlphaFunc(
        cloud.mobject, upd, run_time=run_time, rate_func=rate or theme.EASE
    )


def shift_cloud(cloud: Cloud, vector, run_time: float = 2.0, rate=None):
    return move_cloud(
        cloud, cloud.points + np.asarray(vector, dtype=float), run_time=run_time, rate=rate
    )


def fade_cloud(cloud: Cloud, to: float = 0.0, run_time: float = 1.0, rate=None):
    start = cloud.opacity

    def upd(_m, alpha):
        cloud.opacity = start + (to - start) * alpha

    return UpdateFromAlphaFunc(
        cloud.mobject, upd, run_time=run_time, rate_func=rate or theme.EASE
    )


def recolor_cloud(cloud: Cloud, targets: np.ndarray, run_time: float = 1.5, rate=None):
    """Cross-fade every point to a new colour — the 'ink in water' move."""
    start = cloud.colors.copy()
    targets = np.asarray(targets, dtype=float).reshape(len(start), 3)

    def upd(_m, alpha):
        cloud.colors = start + (targets - start) * alpha

    return UpdateFromAlphaFunc(
        cloud.mobject, upd, run_time=run_time, rate_func=rate or theme.EASE
    )


def rgb_of(color: str) -> np.ndarray:
    from manim.utils.color import ManimColor

    return np.array(ManimColor(color).to_rgb())


def colors_from_labels(labels: np.ndarray, palette: list[str]) -> np.ndarray:
    table = np.array([rgb_of(c) for c in palette])
    return table[np.asarray(labels) % len(palette)]


class TipWire(Wire):
    """A polyline that ends in an arrowhead — the labelled rotations of scene 4."""

    def __init__(self, points, color=theme.INK, width=3.0, tip_size=0.16, **kwargs):
        super().__init__(points, color=color, width=width, closed=False, **kwargs)
        from manim import Triangle

        self.tip = Triangle(color=color, fill_color=color, fill_opacity=1.0, stroke_width=0)
        self.tip.scale_to_fit_height(tip_size)
        self.line = self.mobject
        self.mobject = VGroup(self.line, self.tip)

    def sync(self, view: View) -> None:
        screen, _ = view.project(self.points3d)
        self.line.set_points_as_corners(screen)
        end, prev = screen[-1], screen[-2]
        direction = end - prev
        angle = float(np.arctan2(direction[1], direction[0]))
        self.tip.rotate(angle - PI / 2 - getattr(self, "_tip_angle", 0.0))
        self._tip_angle = angle - PI / 2
        self.tip.move_to(end)


def arc_points(normal, start: float, end: float, radius: float = 1.0, samples: int = 64):
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    helper = np.array([0.0, 0.0, 1.0])
    if abs(float(n @ helper)) > 0.9:
        helper = np.array([1.0, 0.0, 0.0])
    u = np.cross(n, helper)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    t = np.linspace(start, end, samples)
    return radius * (np.cos(t)[:, None] * u + np.sin(t)[:, None] * v)


def reveal_cloud(cloud: Cloud, run_time: float = 3.0, power: float = 3.0, rate=None):
    """Show a cloud point by point, faster and faster — an orbit thickening."""
    n = len(cloud.points)
    cloud.visible = np.zeros(n, dtype=bool)

    def upd(_m, alpha):
        k = int(n * min(alpha, 1.0) ** power)
        cloud.visible = np.arange(n) < max(k, 1)

    from manim import linear

    return UpdateFromAlphaFunc(
        cloud.mobject, upd, run_time=run_time, rate_func=rate or linear
    )


def trails(points: np.ndarray, matrix: np.ndarray, samples: int = 26, arc: float = 1.0):
    """Every point smeared along its own path — the long-exposure look.

    Returns one big array of positions, ready to hand to a :class:`Cloud`,
    together with the fraction along the trail of each position so the tail can
    be faded out.
    """
    axis, angle = axis_angle(matrix)
    from .rotations import rotation_about

    pts = np.asarray(points, dtype=float).reshape(-1, 3)
    out = np.empty((samples * len(pts), 3))
    frac = np.empty(samples * len(pts))
    for i in range(samples):
        t = i / max(samples - 1, 1)
        r = rotation_about(axis, angle * arc * t)
        out[i * len(pts) : (i + 1) * len(pts)] = pts @ r.T
        frac[i * len(pts) : (i + 1) * len(pts)] = t
    return out, frac
