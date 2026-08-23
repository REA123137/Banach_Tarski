"""Scene 7 — 09:00-10:20 · A ball is not a catalogue: it is made of points.

    "ANIMATION – On the left, the neat columns of words.  On the right, the
    ball filled with infinitely many anonymous, identical points."

    "ON SCREEN – [the two matrices A and B]"

    "ANIMATION IDEA – The book that becomes a point.  Split screen. […] Bring a
    magnifier to the book: you read the title.  Bring the same magnifier to the
    point: nothing, it carries no label. […] Then the matrices arrive as
    machines with three input dials and three output dials: feed in (0, 1, 0),
    the dials spin, the output shows."
"""

from __future__ import annotations

# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from manim import (
    Circle,
    Create,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    LEFT,
    Line,
    RIGHT,
    Scene,
    UP,
    UpdateFromAlphaFunc,
    VGroup,
    Write,
)

from banach_tarski import anim, freegroup, motifs, space, theme
from banach_tarski.rotations import COS_THETA, SIN_THETA, MATRICES


def matrix_block(rows: list[list[str]], color: str = theme.INK, size: float = 26) -> VGroup:
    """A matrix, set by hand.  No LaTeX anywhere in this project."""
    grid = VGroup()
    for row in rows:
        line = VGroup(*[theme.mono(entry, size=size, color=color) for entry in row])
        for cell in line:
            cell.width  # force layout
        line.arrange(RIGHT, buff=0.42)
        grid.add(line)
    grid.arrange(DOWN, buff=0.26)
    # align the columns
    for col in range(len(rows[0])):
        xs = [row[col].get_center()[0] for row in grid]
        target = float(np.mean(xs))
        for row in grid:
            row[col].shift(RIGHT * (target - row[col].get_center()[0]))
    height = grid.height + 0.24
    left = VGroup(
        Line(UP * height / 2, DOWN * height / 2, color=color, stroke_width=2),
        Line(ORIGIN := np.zeros(3), RIGHT * 0.16, color=color, stroke_width=2).shift(UP * height / 2),
        Line(np.zeros(3), RIGHT * 0.16, color=color, stroke_width=2).shift(DOWN * height / 2),
    )
    left.next_to(grid, LEFT, buff=0.22)
    right = left.copy().flip(UP)
    right.next_to(grid, RIGHT, buff=0.22)
    return VGroup(left, grid, right)


class S07WordsVsPoints(Scene):
    """A word has a first letter.  A point has nothing at all but its position."""

    def construct(self):
        theme.apply_defaults(self)

        divider = Line(UP * 3.4, DOWN * 3.4, color=theme.GHOST, stroke_width=1.4)
        self.play(Create(divider, run_time=0.8))

        # left: words, filed away
        words = VGroup(
            *[
                theme.word_mobject(w, size=26)
                for w in list(freegroup.words(3, include_empty=False))[:10]
            ]
        ).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        if words.height > 4.6:
            words.scale_to_fit_height(4.6)
        words.move_to(LEFT * 3.6 + DOWN * 0.25)
        left_tag = theme.body("easy to file away", size=28, color=theme.INK_DIM)
        left_tag.next_to(words, UP, buff=0.55)
        self.play(
            FadeIn(left_tag, run_time=0.6),
            FadeIn(words, lag_ratio=0.08, run_time=1.4),
        )

        # right: a ball of anonymous, identical points
        stage = space.Stage(space.View(yaw=-0.6, pitch=0.28, scale=1.45))
        stage.view.origin = np.array([3.6, -0.25, 0.0])
        ball = space.ball_cloud(24000, color=theme.INK, seed=8)
        stage.add(ball)
        stage.install(self)
        stage.spin(self, speed=0.12)
        right_tag = theme.body("no label at all", size=28, color=theme.INK_DIM)
        right_tag.move_to(np.array([3.6, 2.55, 0.0]))
        self.play(FadeIn(right_tag, run_time=0.8))
        self.wait(1.4)

        verdict = theme.body(
            "a point has no first letter.  that is the whole difficulty.",
            size=30,
            color=theme.GOLD,
        )
        verdict.to_edge(DOWN, buff=0.45)
        self.play(Write(verdict, run_time=1.8))
        self.wait(2.0)
        self.play(
            FadeOut(VGroup(divider, words, left_tag, right_tag, verdict), run_time=0.8),
            space.fade_cloud(ball, 0.0, run_time=0.8),
        )


class S07Matrices(Scene):
    """For handling rotations there is a tool built for the job: matrices."""

    def construct(self):
        theme.apply_defaults(self)

        head = theme.body("A rotation about the vertical axis, through an angle θ:",
                          size=30, color=theme.INK_DIM)
        head.to_edge(UP, buff=0.8)
        self.play(FadeIn(head, run_time=0.8))

        a = matrix_block(
            [["cos θ", "− sin θ", "0"], ["sin θ", "cos θ", "0"], ["0", "0", "1"]],
            color=theme.C_A,
        )
        b = matrix_block(
            [["1", "0", "0"], ["0", "cos θ", "− sin θ"], ["0", "sin θ", "cos θ"]],
            color=theme.C_B,
        )
        label_a = theme.mono("A", size=40, color=theme.C_A)
        label_b = theme.mono("B", size=40, color=theme.C_B)
        block_a = VGroup(label_a, a).arrange(RIGHT, buff=0.35)
        block_b = VGroup(label_b, b).arrange(RIGHT, buff=0.35)
        pair = VGroup(block_a, block_b).arrange(RIGHT, buff=1.5).shift(UP * 0.3)
        self.play(FadeIn(block_a, run_time=1.0))
        self.play(FadeIn(block_b, run_time=1.0))
        self.wait(0.8)

        gloss = VGroup(
            theme.body("A turns about the vertical axis, B about a horizontal one.", size=30),
            theme.body("From now on, our letters are these matrices:", size=30,
                       color=theme.INK_DIM),
            theme.formula("a b   becomes   A B", size=36, color=theme.GOLD),
        ).arrange(DOWN, buff=0.34)
        gloss.next_to(pair, DOWN, buff=0.9)
        anim.write_lines(self, gloss, per_line=1.1, lag=0.75)
        self.wait(2.0)
        self.play(FadeOut(VGroup(head, pair, gloss), run_time=0.8))


class S07Magnifier(Scene):
    """ANIMATION IDEA — the book that becomes a point.

    The same lens over a spine and over a point.  One carries a title; the
    other enlarges a white dot and gives you nothing.
    """

    def construct(self):
        theme.apply_defaults(self)

        divider = Line(UP * 3.4, DOWN * 3.4, color=theme.GHOST, stroke_width=1.4)
        self.add(divider)

        spine = motifs.book("abA", height=2.6, width=0.85)
        spine.move_to(LEFT * 3.6)
        point = Dot(radius=0.035, color=theme.INK).move_to(RIGHT * 3.6)
        self.play(FadeIn(spine, run_time=0.7), FadeIn(point, run_time=0.7))

        lens_ring = Circle(radius=1.15, color=theme.INK_DIM, stroke_width=3.0)
        handle = Line(np.array([0.8, -0.8, 0]), np.array([1.7, -1.7, 0]),
                      color=theme.INK_DIM, stroke_width=6.0)
        lens = VGroup(lens_ring, handle)
        lens.move_to(LEFT * 3.6 + UP * 2.6)
        self.play(FadeIn(lens, run_time=0.6))
        self.play(lens.animate(run_time=1.2, rate_func=theme.EASE).move_to(spine.get_center()))

        title = theme.serif("a b a⁻¹", size=44, color=theme.C_A)
        title.move_to(spine.get_center() + UP * 2.1)
        self.play(FadeIn(title, scale=1.3, run_time=0.8))
        self.wait(1.0)

        self.play(
            FadeOut(title, run_time=0.4),
            lens.animate(run_time=1.6, rate_func=theme.EASE).move_to(point.get_center()),
        )
        big_dot = Dot(radius=0.16, color=theme.INK).move_to(point)
        self.play(FadeIn(big_dot, run_time=0.5))
        nothing = theme.body("nothing", size=34, color=theme.INK_DIM)
        nothing.move_to(point.get_center() + UP * 2.1)
        self.play(FadeIn(nothing, run_time=0.8))
        self.wait(1.8)
        self.play(FadeOut(VGroup(divider, spine, point, big_dot, lens, nothing), run_time=0.8))


class S07DialMachine(Scene):
    """ANIMATION IDEA — the matrix as a machine with three dials in and three out.

    Feed in (0, 1, 0); the dials spin; the output shows.  The numbers are the
    real ones: ``MATRICES["a"] @ (0, 1, 0)``.
    """

    def construct(self):
        theme.apply_defaults(self)

        vector = np.array([0.0, 1.0, 0.0])
        result = MATRICES["a"] @ vector

        ins = VGroup(
            *[motifs.Dial(v, label=n) for v, n in zip(vector, ("x", "y", "z"))]
        ).arrange(DOWN, buff=0.55)
        outs = VGroup(
            *[motifs.Dial(0.0, label=n) for n in ("x′", "y′", "z′")]
        ).arrange(DOWN, buff=0.55)

        box = theme.panel(3.6, 4.4)
        inner = matrix_block(
            [["1/3", "−2√2/3", "0"], ["2√2/3", "1/3", "0"], ["0", "0", "1"]],
            color=theme.C_A,
            size=22,
        )
        inner.scale_to_fit_width(3.0).move_to(box)
        machine = VGroup(box, inner)

        row = VGroup(ins, machine, outs).arrange(RIGHT, buff=1.1).shift(UP * 0.62)
        wires = VGroup()
        for dial, side, target in [(d, RIGHT, box.get_left()) for d in ins] + [
            (d, LEFT, box.get_right()) for d in outs
        ]:
            start = dial.get_right() if side is RIGHT else dial.get_left()
            end = np.array([target[0], start[1], 0.0])
            wires.add(Line(start, end, color=theme.GHOST, stroke_width=1.4))

        self.play(FadeIn(machine, run_time=0.9))
        self.play(FadeIn(ins, run_time=0.7), FadeIn(outs, run_time=0.7), Create(wires, run_time=0.8))

        caption = theme.caption("feed in (0, 1, 0) — the dials spin — the output shows", size=24)
        caption.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(caption, run_time=0.6))

        def spin(_m, alpha):
            for i, dial in enumerate(outs):
                if alpha < 0.75:
                    dial.set_value(float(np.sin(alpha * 26 + i * 1.7)))
                else:
                    settle = (alpha - 0.75) / 0.25
                    dial.set_value(
                        float(np.sin(0.75 * 26 + i * 1.7)) * (1 - settle) + result[i] * settle
                    )

        self.play(UpdateFromAlphaFunc(outs, spin, run_time=2.6, rate_func=theme.EASE))
        self.wait(0.5)

        answer = theme.formula(
            f"A · (0, 1, 0)  =  ({result[0]:+.2f},  {result[1]:+.2f},  {result[2]:+.2f})",
            size=32,
            color=theme.GOLD,
        )
        answer.next_to(caption, UP, buff=0.35)
        self.play(Write(answer, run_time=1.4))
        self.wait(2.0)
        self.play(FadeOut(VGroup(machine, ins, outs, wires, caption, answer), run_time=0.8))
