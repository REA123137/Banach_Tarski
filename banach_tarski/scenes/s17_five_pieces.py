"""
17 - Five pieces, and not fewer.

The assembly, end to end: the ball comes apart into five sets, each set is
carried by one rigid motion, and the results are two balls.  Robinson showed
in 1947 that five is the smallest possible number.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustMorph, DustRecolor
from banach_tarski import mathkit as mk

N = 4200
R = 1.55
LABELS = ["A₁", "A₂", "A₃", "A₄", "A₅"]


class FivePieces(BT3DScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-90 * DEGREES, zoom=0.95)

        title = T("the assembly", size=H3, color=PAPER).move_to(UP * 3.30)
        self.label(title)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)

        rng = np.random.default_rng(21)
        ball = mk.ball_points(N, R, seed=6)
        # Four pieces from the surface argument, plus the little one that mops up
        # the centre.  The fifth is deliberately tiny.
        labels = rng.integers(0, 4, size=N)
        labels[rng.random(N) < 0.035] = 4
        colors = [PIECE_COLORS[i] for i in labels]

        cloud = Dust(ball, colors, size=2.6)
        cloud.depth_shade(self, radius=R, floor=0.16)
        self.play(FadeIn(cloud), run_time=1.2)
        self.say("A", "One ball. Five pieces, colour-coded.", hold=2.2)

        legend = VGroup()
        for i, name in enumerate(LABELS):
            sw = Square(side_length=0.20).set_fill(PIECE_COLORS[i], opacity=1)
            sw.set_stroke(width=0)
            legend.add(VGroup(sw, T(name, size=TINY, color=PAPER)).arrange(RIGHT, buff=0.16))
        legend.arrange(RIGHT, buff=0.52).move_to(DOWN * 2.30)
        self.label(legend)
        self.play(FadeIn(legend, shift=UP * 0.1), run_time=0.7)

        # -- exploded view -----------------------------------------------------------
        spread_dirs = np.array([
            [-1.9, 0, 1.1], [1.9, 0, 1.1], [-1.9, 0, -1.1], [1.9, 0, -1.1], [0, 0, 0.0]
        ])
        exploded = ball + spread_dirs[labels] * 1.15
        self.play(DustMorph(cloud, exploded, stagger=0.5, swirl=0.4, run_time=2.6))
        self.say("B", "Pull them apart. Each one is a cloud - no surfaces, no edges.",
                 hold=2.8)

        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(1.8)
        self.stop_ambient_camera_rotation()

        # -- the rigid motions --------------------------------------------------------
        moves = T("each piece is then rotated or slid - once, rigidly",
                  size=SMALL, color=MUTED).move_to(DOWN * 2.30)
        self.label(moves)
        self.play(FadeOut(legend), FadeIn(moves), run_time=0.7)
        self.say("A", "Now every piece gets one rigid motion. A turn, or a slide. "
                      "Nothing else.", hold=2.8)

        # -- two balls -----------------------------------------------------------------
        left_ball = mk.ball_points(N, R, seed=41) + np.array([-2.5, 0, 0])
        right_ball = mk.ball_points(N, R, seed=42) + np.array([2.5, 0, 0])
        goes_left = np.isin(labels, [0, 2]) | (labels == 4)
        targets = np.where(goes_left[:, None], left_ball, right_ball)

        self.play(DustMorph(cloud, targets, swirl=1.2, stagger=0.55, run_time=3.2))
        self.wait(0.5)

        eq = T("=", size=H1, color=GOLD, weight=BOLD).move_to(ORIGIN)
        self.label(eq)
        self.play(FadeIn(eq, scale=1.5), run_time=0.5)
        self.say("B", "Two balls. Each one the size of the original. "
                      "No piece was stretched, and no point was used twice.", hold=3.2)

        # -- minimality ------------------------------------------------------------------
        self.play(FadeOut(moves), run_time=0.3)
        minimal = VGroup(
            T("five is the minimum", size=BODY, color=MINT, weight=BOLD),
            T("Raphael Robinson, 1947  -  four pieces provably will not do",
              size=TINY, color=MUTED),
        ).arrange(DOWN, buff=0.22).move_to(DOWN * 2.20)
        self.label(minimal)
        self.play(FadeIn(minimal, shift=UP * 0.12), run_time=0.8)
        self.say("A", "And five is not a rough figure. Robinson proved you cannot "
                      "do it with four.", hold=3.0)

        self.play(FadeOut(cloud), FadeOut(eq), FadeOut(title), FadeOut(minimal),
                  FadeOut(self._caption), run_time=1.2)
