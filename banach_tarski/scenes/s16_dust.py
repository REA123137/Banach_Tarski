"""
16 - What the pieces look like.

They do not look like anything.  This scene is honest about that: it shows a
stand-in cloud with no smallest scale, pushes in on it four times so the
viewer can see that nothing ever resolves, and says out loud that no true
picture of these sets exists.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust

N = 26000
ZOOMS = 4


def scatter(n: int, seed: int = 3) -> np.ndarray:
    """
    A cloud with structure at every scale.

    Built by an iterated function system, purely as a stand-in: the real pieces
    are not self-similar, they are simply beyond drawing.  What survives the
    analogy is the part that matters - push in as far as you like and there is
    never a smallest feature.
    """
    rng = np.random.default_rng(seed)
    maps = [
        (np.array([0.42, 0.42]), np.array([-1.0, -0.55])),
        (np.array([0.42, 0.42]), np.array([1.0, -0.55])),
        (np.array([0.42, 0.42]), np.array([0.0, 1.05])),
        (np.array([0.34, 0.34]), np.array([0.0, -0.05])),
    ]
    p = np.zeros(2)
    out = np.empty((n, 3))
    for i in range(n):
        s, t = maps[rng.integers(0, len(maps))]
        p = p * s + t * (1 - s)
        p = p + rng.normal(scale=0.004, size=2)
        out[i] = (p[0], p[1], 0.0)
    return out


class WhatThePiecesLookLike(BTMovingScene):
    star_seed = 111
    stars = False

    def construct(self):
        self.chapter("10", "What the pieces look like", "and why you have never seen one")

        pts = scatter(N)
        pts = pts / np.abs(pts).max() * 2.9
        rng = np.random.default_rng(1)
        colors = [PIECE_COLORS[i] for i in rng.integers(0, 4, size=len(pts))]
        cloud = Dust(pts, colors, size=1.5)
        self.play(FadeIn(cloud, run_time=1.6))

        self.say("A", "A piece is not a lump. It is a cloud of points, scattered "
                      "through the ball.", hold=2.8)

        frame = self.camera.frame
        anchor = pts[len(pts) // 2]

        for k in range(ZOOMS):
            self.play(
                frame.animate.set(width=frame.width * 0.34).move_to(anchor),
                run_time=2.0, rate_func=Look.ease,
            )
            if k == 0:
                self.say("B", "Push in.", hold=1.2)
            elif k == 1:
                self.say("A", "Push in again. It never settles down.", hold=2.2)

        depth = T("magnified about a hundred times", size=TINY, color=MUTED)
        depth.scale(frame.width / config.frame_width)
        depth.move_to(frame.get_center()).shift(UP * (frame.height / 2 - 0.55 *
                                                      frame.width / config.frame_width))
        self.play(FadeIn(depth), run_time=0.6)
        self.say("B", "There is no smallest grain, no edge, no surface to point at. "
                      "Nothing to cut with a knife.", hold=3.2)

        self.play(FadeOut(depth), run_time=0.4)
        self.play(frame.animate.set(width=config.frame_width).move_to(ORIGIN),
                  run_time=2.4, rate_func=Look.ease)

        caveat = T("even this is a stand-in - the real pieces cannot be drawn at all",
                   size=SMALL, color=CORAL).move_to(DOWN * 3.0)
        self.play(FadeIn(caveat, shift=UP * 0.12), run_time=0.8)
        self.say("A", "And to be honest: this is only a stand-in. The real pieces "
                      "come from a choice nobody can write down.", hold=3.2)
        self.say("B", "No formula produces them. No computer can draw them. They are "
                      "proved to exist, and that is all.", hold=3.2)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.2)
