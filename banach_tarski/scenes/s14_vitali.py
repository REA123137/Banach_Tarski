"""
14 - A set with no length.

Banach-Tarski needs sets that no notion of volume can measure.  Vitali built
one on a circle in 1905, and it fits in a single scene: choose one point from
each rational-rotation orbit, and ask how long the result is.  Every possible
answer is absurd.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *

RADIUS = 2.15
STEP = 2 * PI / 9          # the rotation that generates the orbits, on screen
N_CLASSES = 7
CENTER = LEFT * 3.3 + UP * 0.35
CLASS_COLORS = [CORAL, CYAN, MINT, VIOLET, GOLD, MAGENTA, INDIGO]
COLUMN = 6.3          # the right-hand text column, kept inside the frame


def on_circle(angle: float, r: float = RADIUS, center=CENTER) -> np.ndarray:
    return np.array([r * np.cos(angle), r * np.sin(angle), 0.0]) + np.asarray(center)


class ASetWithNoLength(BTScene):
    star_seed = 88

    def construct(self):
        self.chapter("08", "A set with no length", "Vitali, 1905")

        circle = Circle(radius=RADIUS).move_to(CENTER)
        circle.set_stroke(GRID, 2.2)
        halo = glow(circle, GRID, layers=8, spread=0.3, opacity=0.05)
        self.play(FadeIn(halo), Create(circle), run_time=1.2)
        self.say("A", "One circle. Total length: two pi. Nothing controversial yet.",
                 hold=2.4)

        # -- one orbit --------------------------------------------------------------
        start = 0.32
        orbit = VGroup(*[
            Dot(on_circle(start + k * STEP), radius=0.075, color=CLASS_COLORS[0])
            for k in range(9)
        ])
        arrow = CurvedArrow(on_circle(start), on_circle(start + STEP), radius=RADIUS * 1.15)
        arrow.set_stroke(CLASS_COLORS[0], 2.2)

        self.play(FadeIn(orbit[0], scale=0.5), run_time=0.5)
        self.play(Create(arrow), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in orbit[1:]],
                              lag_ratio=0.13, run_time=1.6))
        self.play(FadeOut(arrow), run_time=0.4)
        self.say("B", "Pick a point and keep turning it by the same fixed step. "
                      "The points you land on are its orbit.", hold=2.8)

        # -- many orbits ------------------------------------------------------------
        rng = np.random.default_rng(5)
        offsets = np.sort(rng.uniform(0.02, STEP - 0.02, size=N_CLASSES - 1))
        others = VGroup()
        for j, off in enumerate(offsets, start=1):
            others.add(VGroup(*[
                Dot(on_circle(start + off + k * STEP), radius=0.062,
                    color=CLASS_COLORS[j])
                for k in range(9)
            ]))
        self.play(LaggedStart(*[FadeIn(g, lag_ratio=0.05) for g in others],
                              lag_ratio=0.2, run_time=2.2))
        self.say("A", "Every other point starts an orbit of its own. The circle is "
                      "nothing but orbits, side by side.", hold=2.8)

        # -- choose ------------------------------------------------------------------
        self.say("B", "Choose one point from each orbit. Uncountably many choices, "
                      "no rule - the axiom of choice again.", hold=3.0)

        groups = [orbit] + list(others)
        picks = VGroup()
        for j, g in enumerate(groups):
            d = g[2].copy().set_color(PAPER).scale(1.25)
            picks.add(d)
        self.play(
            *[g.animate.set_opacity(0.20) for g in groups],
            run_time=0.8,
        )
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in picks],
                              lag_ratio=0.10, run_time=1.4))

        v_lbl = T("V", size=H3, color=PAPER, weight=BOLD).move_to(CENTER)
        self.play(FadeIn(v_lbl, scale=1.4), run_time=0.6)

        # -- the impossible sum --------------------------------------------------------
        board = VGroup(
            T("turn V one step, then another, then another…", size=18, color=MUTED),
            T("the copies never overlap", size=18, color=MUTED),
            T("together they cover the whole circle", size=18, color=MUTED),
        )
        for line in board:
            fit(line, COLUMN)
        board.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        board.move_to(RIGHT * 3.45 + UP * 1.70)

        self.play(FadeIn(board[0], shift=RIGHT * 0.2), run_time=0.6)
        copies = VGroup()
        for k in range(1, 4):
            c = picks.copy().set_color(interpolate_color(ManimColor(PAPER),
                                                         ManimColor(CYAN), k / 3))
            for d, src in zip(c, picks):
                ang = np.arctan2(*(src.get_center() - CENTER)[1::-1])
                d.move_to(on_circle(ang + k * STEP))
            copies.add(c)
            self.play(FadeIn(c, run_time=0.55))
        self.play(FadeIn(board[1], shift=RIGHT * 0.2), run_time=0.6)
        self.play(FadeIn(board[2], shift=RIGHT * 0.2), run_time=0.6)
        self.say("A", "Rotations do not change length. So all those copies have the "
                      "same length as V.", hold=2.8)

        sums = VGroup(
            T("if V has length 0   →   the circle has length 0", size=18, color=CORAL),
            T("if V has length > 0   →   the circle has infinite length",
              size=18, color=CORAL),
        )
        for line in sums:
            fit(line, COLUMN)
        sums.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        sums.next_to(board, DOWN, buff=0.70).align_to(board, LEFT)
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in sums],
                              lag_ratio=0.3, run_time=1.4))
        self.say("B", "Countably many copies of the same length. Add them up: "
                      "either nothing, or infinity.", hold=3.0)

        verdict = T("V has no length at all", size=SMALL, color=MINT, weight=BOLD)
        fit(verdict, COLUMN)
        verdict.next_to(sums, DOWN, buff=0.50).align_to(board, LEFT)
        self.play(FadeIn(verdict, shift=UP * 0.12), run_time=0.8)
        self.play(Circumscribe(verdict, color=MINT, buff=0.2, stroke_width=1.6,
                               run_time=1.6))
        self.say("A", "The circle is two pi. So V cannot have a length. Not zero, "
                      "not positive - none.", hold=3.0)
        self.say("B", "Sets like this are what the ball gets cut into.", hold=2.6)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.1)
