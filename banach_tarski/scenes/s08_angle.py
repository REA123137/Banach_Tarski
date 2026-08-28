"""Scene 8 — 10:20-11:15 · The right angle.

    "ON SCREEN – The angle writes itself large, alone: θ = arccos(1/3).  Two
    seconds."

    "ANIMATION IDEA – The gate.  Since we are not doing the proof, we must make
    it felt in ten seconds.  Centre screen, a gate labelled 'divisible by 3?'.
    Words stream past, faster and faster; for each one a number steps up to the
    gate, which shows NO.  Dozens, then hundreds, without exception.  Then the
    gate is shown the one number that would allow a return to the start: it is
    divisible by three, and the gate refuses it too."

The numbers at the gate are not invented.  Take the point (1, 0, 0) — it lies
on the axis of B, so the words that matter are the ones whose first applied
letter is a or a⁻¹.  A reduced word of length n then sends it to a point whose
second coordinate is exactly b·√2 / 3ⁿ with b a whole number, and the induction
of the real proof turns on the fact that b is never divisible by three.
:func:`numerator` computes that b, and the gate simply reports ``b % 3``.
"""

from __future__ import annotations

# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from manim import (
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    Line,
    RIGHT,
    Scene,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, freegroup, theme
from banach_tarski.rotations import THETA, word_matrix


def numerator(word: str) -> int:
    """The whole number the induction watches.

    ``w(1, 0, 0)`` has second coordinate ``b·√2 / 3ⁿ``; this returns ``b``.
    """
    image = word_matrix(word) @ np.array([1.0, 0.0, 0.0])
    return int(round(image[1] * (3.0 ** len(word)) / np.sqrt(2.0)))


def gate_words(max_length: int = 5) -> list[str]:
    """The words the gate is shown: those whose first applied letter is a^{±1}.

    A word ending in b^{±1} would start by turning about the very axis the
    point (1, 0, 0) sits on, and would move nothing at all.
    """
    return [
        w for w in freegroup.words(max_length, include_empty=False) if w[-1] in ("a", "A")
    ]


class S08Angle(Scene):
    """The angle, alone on the screen, for two seconds."""

    def construct(self):
        theme.apply_defaults(self)

        angle = theme.display("θ  =  arccos(1/3)", size=76, color=theme.GOLD)
        self.play(Write(angle, run_time=1.6))
        self.wait(2.0)

        value = theme.caption(
            f"≈ {np.degrees(THETA):.2f}°   ·   cos θ = 1/3,  sin θ = 2√2⁄3", size=26
        )
        value.next_to(angle, DOWN, buff=0.7)
        self.play(FadeIn(value, run_time=0.8))
        self.wait(1.2)

        self.play(
            angle.animate(run_time=1.0, rate_func=theme.EASE).scale(0.6).move_to(
                np.array([0.0, theme.TOP_EDGE - theme.MARGIN - 0.45, 0.0])
            ),
            FadeOut(value, run_time=0.6),
        )

        claim = VGroup(
            theme.body("The two rotations by arccos(1/3) about two", size=36),
            theme.body("perpendicular axes generate a free group.", size=36),
        ).arrange(DOWN, buff=0.30)
        plain = theme.body(
            "every word is a real motion, and two different words are two different motions",
            size=28,
            color=theme.INK_DIM,
        )
        block = theme.stage(VGroup(claim, plain).arrange(DOWN, buff=0.7))

        anim.write_lines(self, claim, per_line=1.3, lag=0.8)
        self.play(FadeIn(plain, run_time=0.9))

        honest = theme.caption(
            "the proof is an induction on the length of the words; we give the result", size=24
        )
        theme.foot(honest)
        self.play(FadeIn(honest, run_time=0.7))
        self.wait(2.4)
        self.play(FadeOut(VGroup(angle, block, honest), run_time=0.8))


class S08Gate(Scene):
    """ANIMATION IDEA — the gate labelled "divisible by 3?".

    Word after word, faster and faster, and the gate never says yes.  Then the
    one number that would let the sphere come home is shown to it: divisible by
    three, and refused all the same.
    """

    def construct(self):
        theme.apply_defaults(self)

        # the gate
        post_l = Line(UP * 1.35, DOWN * 1.35, color=theme.INK_DIM, stroke_width=4)
        post_r = post_l.copy()
        posts = VGroup(post_l, post_r).arrange(RIGHT, buff=3.4)
        lintel = Line(
            post_l.get_top() + LEFT * 0.2, post_r.get_top() + RIGHT * 0.2,
            color=theme.INK_DIM, stroke_width=4,
        )
        sign = theme.body("divisible by 3 ?", size=30, color=theme.INK)
        sign.next_to(lintel, UP, buff=0.28)
        gate = VGroup(posts, lintel, sign)
        theme.stage(gate)
        self.play(Create(posts, run_time=0.7), Create(lintel, run_time=0.5),
                  FadeIn(sign, run_time=0.5))

        verdict_pos = gate.get_bottom() + DOWN * 0.55

        # a stream of words, each with its number, faster and faster
        stream = gate_words(4)
        rng = np.random.default_rng(3)
        rng.shuffle(stream)
        speeds = np.geomspace(0.85, 0.10, 16)
        for i, run_time in enumerate(speeds):
            word = stream[i % len(stream)]
            n = numerator(word)
            tile = theme.word_mobject(word, size=26)
            tile.move_to(LEFT * 6.4 + UP * 0.35)
            number = theme.formula(str(n), size=34, color=theme.INK)
            number.next_to(tile, DOWN, buff=0.25)
            pack = VGroup(tile, number)
            self.add(pack)
            self.play(
                pack.animate(run_time=run_time, rate_func=theme.EASE).move_to(gate.get_center()),
            )
            answer = theme.display("NO", size=40, color=theme.REFUSE)
            answer.move_to(verdict_pos)
            self.add(answer)
            self.play(
                pack.animate(run_time=run_time, rate_func=theme.EASE_IN).move_to(
                    RIGHT * 6.4 + UP * 0.35
                ).set_opacity(0.0),
                run_time=run_time,
            )
            self.remove(pack, answer)

        tally = theme.caption("dozens, then hundreds — without exception", size=24)
        theme.foot(tally)
        self.play(FadeIn(tally, run_time=0.6))
        self.wait(0.8)

        # the one number that would let the sphere come home
        self.play(FadeOut(tally, run_time=0.4))
        special = theme.body("the number that would bring the sphere home", size=28,
                             color=theme.GOLD)
        theme.head(special)
        zero = theme.formula("0", size=56, color=theme.GOLD)
        zero.move_to(LEFT * 6.4 + UP * 0.35)
        self.play(FadeIn(special, run_time=0.7), FadeIn(zero, run_time=0.5))
        self.play(zero.animate(run_time=1.6, rate_func=theme.EASE).move_to(gate.get_center()))
        yes = theme.display("divisible", size=34, color=theme.GOLD).move_to(verdict_pos)
        self.play(FadeIn(yes, run_time=0.5))
        self.wait(0.7)

        refused = theme.display("REFUSED", size=44, color=theme.REFUSE).move_to(verdict_pos)
        self.play(FadeOut(yes, run_time=0.3), FadeIn(refused, run_time=0.4, scale=1.2))
        bar = anim.strike(zero, pad=0.28, width=6.0)
        self.play(Create(bar, run_time=0.35, rate_func=theme.SNAP))
        self.wait(0.8)

        moral = theme.body("no sequence of rotations ever brings the sphere back", size=30)
        theme.foot(moral)
        self.play(Write(moral, run_time=1.6))
        self.wait(2.0)
        self.play(FadeOut(VGroup(gate, zero, bar, refused, special, moral), run_time=0.8))
