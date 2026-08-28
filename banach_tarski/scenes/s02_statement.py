"""Scene 2 — 01:15-02:00 · What the paradox says.

    "ON SCREEN – The statement writes itself in large type, one line at a
    time."

    "ANIMATION IDEA – The three words defend themselves.  Each key word
    appears with its counter-example, which shows up and is then struck
    through in red. […] The definition becomes a machine that refuses things,
    not a title card."
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
    Ellipse,
    FadeIn,
    FadeOut,
    LEFT,
    RIGHT,
    Group,
    Scene,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, space, theme

STATEMENT = [
    "You can cut a solid ball into finitely many pieces,",
    "then, moving those pieces without ever deforming them,",
    "obtain two solid balls identical to the one you started with.",
]

KEY_WORDS = [
    ("Finitely", "five pieces are enough, and we will know that by the end."),
    ("Moving", "you may rotate and translate.  Nothing else."),
    ("Identical", "the same radius, exactly.  Not smaller, not approximately."),
]


class S02Statement(Scene):
    """The statement writes itself, one line at a time, and nothing else moves."""

    def construct(self):
        theme.apply_defaults(self)

        # Each line isolates the one word that carries weight, so it can be
        # lit where it stands rather than by counting characters.
        keyed = ("finitely", "moving", "identical")
        lines = VGroup(
            *[
                theme.highlighted(line, word, size=36, accent=theme.INK)
                for line, word in zip(STATEMENT, keyed)
            ]
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        theme.stage(lines)

        attribution = theme.head(theme.caption("Banach & Tarski, 1924", size=26))

        self.play(FadeIn(attribution, run_time=0.8))
        anim.write_lines(self, lines, per_line=1.6, lag=0.85)
        self.wait(1.2)

        self.play(
            *[
                line.animate(run_time=1.0).set_color_by_tex(
                    theme.latex_escape(word), theme.GOLD
                )
                for line, word in zip(lines, keyed)
            ],
        )
        self.wait(1.0)

        note = theme.foot(theme.caption("three words do all the work", size=26))
        self.play(FadeIn(note, shift=UP * 0.15, run_time=0.7))
        self.wait(1.6)
        self.play(FadeOut(VGroup(lines, attribution, note), run_time=0.8))


class S02WordsDefend(Scene):
    """ANIMATION IDEA — each word appears with its counter-example, struck out.

    Three refusals, each built the same way: the word, its plain-English
    translation, the thing it forbids, then the red rule.  The definition is a
    machine that refuses things.
    """

    def construct(self):
        theme.apply_defaults(self)

        for index, (word, gloss) in enumerate(KEY_WORDS):
            title = theme.display(word, size=64, color=theme.GOLD)
            theme.head(title)
            sub = theme.body(gloss, size=30, color=theme.INK_DIM)
            sub.next_to(title, DOWN, buff=0.38)
            self.play(Write(title, run_time=0.9), FadeIn(sub, run_time=0.9))

            counter, caption_text = self._counter_example(index)
            counter.move_to(DOWN * 0.7)
            cap = theme.body(caption_text, size=28, color=theme.INK_DIM)
            cap.next_to(counter, DOWN, buff=0.55)
            self.play(FadeIn(counter, run_time=1.0), FadeIn(cap, run_time=0.8))
            self.wait(0.5)

            bar = anim.refuse(self, counter, run_time=0.55, hold=0.4)
            self.play(cap.animate(run_time=0.35).set_opacity(0.35))
            self.wait(0.6)
            self.play(
                FadeOut(Group(title, sub, counter, cap, bar), run_time=0.55),
            )
            self.wait(0.2)

        closing = theme.body("That is all the theorem says, and it is already enormous.", size=34)
        self.play(Write(closing, run_time=1.8))
        self.wait(1.8)
        self.play(FadeOut(closing, run_time=0.7))

    # ---------------------------------------------------------------- helpers
    def _counter_example(self, index: int):
        if index == 0:
            # "Finitely": a cut into infinite dust
            pts = space.ball_points(14000, seed=12, shell=0.1)
            dust = Group()
            proj = space.View(scale=1.35, distance=9).project(pts)[0]
            from manim.mobject.types.point_cloud_mobject import PMobject

            cloud = PMobject(stroke_width=1.4)
            rgbas = np.ones((len(pts), 4))
            rgbas[:, :3] = space.rgb_of(theme.INK)
            rgbas[:, 3] = 0.55
            cloud.add_points(proj, rgbas=rgbas)
            dust.add(cloud)
            return dust, "cut into infinitely many pieces"
        if index == 1:
            # "Moving": a ball being stretched
            ball = Circle(radius=1.0, stroke_width=0, fill_color="#EDE6DA", fill_opacity=0.9)
            stretched = Ellipse(width=3.4, height=1.15, stroke_width=0,
                                fill_color="#EDE6DA", fill_opacity=0.9)
            arrow = theme.rule(width=1.0, color=theme.INK_DIM, stroke=2)
            group = VGroup(ball, arrow, stretched).arrange(RIGHT, buff=0.5)
            return group, "stretched"
        # "Identical": two smaller balls
        big = Circle(radius=1.05, stroke_width=0, fill_color="#EDE6DA", fill_opacity=0.9)
        small_a = Circle(radius=0.62, stroke_width=0, fill_color="#EDE6DA", fill_opacity=0.9)
        small_b = small_a.copy()
        arrow = theme.rule(width=1.0, color=theme.INK_DIM, stroke=2)
        pair = VGroup(small_a, small_b).arrange(RIGHT, buff=0.28)
        group = VGroup(big, arrow, pair).arrange(RIGHT, buff=0.5)
        return group, "two smaller balls"
