"""
16 - What the pieces look like.

They do not look like anything.  This scene is honest about that: it shows a
stand-in cloud with structure at every scale, pushes in on it until the
magnification is in the hundreds, and says out loud that no true picture of
these sets exists.

The zoom is not a crop.  A finite cloud thins out as you magnify it, which
would say the opposite of what the scene means, so each level draws a fresh
cloud of its own: the attractor pushed through the same affine maps that
define the window being entered.  Density on screen therefore stays constant,
which is the honest rendering of "there is no smallest grain".
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust

N = 15000
SPAN = 3.0                       # half-width of the level-0 cloud, in frame units
DIVE = (3, 0, 2, 1)              # which sub-copy we descend into, level by level

# An iterated function system: each map is p -> s·p + t·(1-s), a contraction
# toward its own fixed point.  Purely a stand-in - the real pieces are not
# self-similar, they are simply beyond drawing.  What survives the analogy is
# the part that matters: push in as far as you like, nothing ever resolves.
MAPS = (
    (0.44, np.array([-1.00, -0.58])),
    (0.44, np.array([1.00, -0.58])),
    (0.44, np.array([0.00, 1.06])),
    (0.36, np.array([0.00, -0.02])),
)


def attractor(n: int, seed: int = 3) -> np.ndarray:
    """The chaos game: jump at random between the maps and record where you land."""
    rng = np.random.default_rng(seed)
    p = np.zeros(2)
    out = np.empty((n, 3))
    picks = rng.integers(0, len(MAPS), size=n)
    for i, k in enumerate(picks):
        s, t = MAPS[k]
        p = p * s + t * (1 - s)
        out[i] = (p[0], p[1], 0.0)
    return out


def compose(scale: float, offset: np.ndarray, k: int) -> tuple[float, np.ndarray]:
    """Compose an affine map with MAPS[k], staying in (scale, offset) form."""
    s, t = MAPS[k]
    return scale * s, scale * t * (1 - s) + offset


class WhatThePiecesLookLike(BTMovingScene):
    stars = False

    def construct(self):
        self.chapter("10", "What the pieces look like", "and why you have never seen one")

        base = attractor(N)
        base = base / np.abs(base[:, :2]).max() * SPAN
        rng = np.random.default_rng(1)

        def cloud_at(scale: float, offset: np.ndarray, size: float) -> Dust:
            pts = base.copy()
            pts[:, :2] = pts[:, :2] * scale + offset
            colors = [PIECE_COLORS[i] for i in rng.integers(0, 4, size=len(pts))]
            return Dust(pts, colors, size=size)

        level = cloud_at(1.0, np.zeros(2), 2.0)
        self.play(FadeIn(level, run_time=1.6))
        self.say("A", "A piece is not a lump. It is a cloud of points, scattered "
                      "through the ball.", hold=2.8)

        frame = self.camera.frame
        scale, offset = 1.0, np.zeros(2)
        clouds = [level]

        for step, k in enumerate(DIVE):
            scale, offset = compose(scale, offset, k)
            centre = np.array([offset[0], offset[1], 0.0])
            # A fresh cloud filling the window we are about to enter.
            nxt = cloud_at(scale, offset, 2.0)
            self.add(nxt)
            clouds.append(nxt)
            self.play(
                frame.animate.set(width=config.frame_width * scale).move_to(centre),
                run_time=2.1, rate_func=Look.ease,
            )
            if step == 0:
                self.say("B", "Push in.", hold=1.2)
            elif step == 1:
                self.say("A", "Push in again. It never settles down.", hold=2.2)

        depth = T(f"magnified {round(1 / scale):,}×", size=TINY, color=MUTED)
        depth.scale(scale).move_to(frame.get_center())
        depth.shift(UP * (frame.height / 2 - 0.7 * scale))
        self.play(FadeIn(depth), run_time=0.6)
        self.say("B", "There is no smallest grain, no edge, no surface to point at. "
                      "Nothing a knife could follow.", hold=3.2)

        self.play(FadeOut(depth), run_time=0.4)
        self.play(frame.animate.set(width=config.frame_width).move_to(ORIGIN),
                  run_time=2.4, rate_func=Look.ease)
        self.play(*[FadeOut(c) for c in clouds[1:]], run_time=0.8)

        caveat = T("even this is a stand-in - the real pieces cannot be drawn at all",
                   size=SMALL, color=CORAL).move_to(DOWN * 3.05)
        self.play(FadeIn(caveat, shift=UP * 0.12), run_time=0.8)
        self.say("A", "And to be honest: this is only a stand-in. The real pieces "
                      "come from a choice nobody can write down.", hold=3.2)
        self.say("B", "No formula produces them. No computer can draw them. They are "
                      "proved to exist, and that is all.", hold=3.2)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.2)
