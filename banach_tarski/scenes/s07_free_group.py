"""
07 - The free group on two letters.

Words in a, b and their inverses, with exactly one rule: a letter cancels its
own inverse, and nothing else ever cancels.  "Free" means no coincidences.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski import mathkit as mk

TOKEN_COLORS = {"a": C_A, "A": C_AI, "b": C_B, "B": C_BI}


def token(letter: str, size: float = BODY) -> VGroup:
    color = TOKEN_COLORS[letter]
    txt = M(mk.PRETTY[letter], size=size, color=color)
    box = RoundedRectangle(width=max(txt.width + 0.36, 0.72), height=0.78,
                           corner_radius=0.14)
    box.set_stroke(color, 1.8, opacity=0.85).set_fill(color, opacity=0.10)
    txt.move_to(box)
    return VGroup(box, txt)


def word_row(letters: str, size: float = BODY, buff: float = 0.14) -> VGroup:
    return VGroup(*[token(c, size) for c in letters]).arrange(RIGHT, buff=buff)


class FreeGroup(BTScene):
    star_seed = 41

    def construct(self):
        self.chapter("05", "The free group", "words with one rule, and no coincidences")

        # -- the alphabet -------------------------------------------------------
        alphabet = VGroup(*[token(c, H3) for c in "aAbB"]).arrange(RIGHT, buff=0.55)
        alphabet.move_to(UP * 1.9)
        names = VGroup(
            T("turn one way", size=TINY, color=MUTED),
            T("turn it back", size=TINY, color=MUTED),
            T("turn the other way", size=TINY, color=MUTED),
            T("turn that back", size=TINY, color=MUTED),
        )
        for n, tok in zip(names, alphabet):
            n.next_to(tok, DOWN, buff=0.22)

        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in alphabet],
                              lag_ratio=0.16, run_time=1.3))
        self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.1) for n in names],
                              lag_ratio=0.12, run_time=1.0))
        self.say("A", "Four moves: two rotations and the two that undo them. "
                      "String them together and you get a word.", hold=2.6)

        # -- a word --------------------------------------------------------------
        self.play(FadeOut(names), run_time=0.4)
        raw = "abaABb"
        row = word_row(raw, H3).move_to(DOWN * 0.15)
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in row],
                              lag_ratio=0.10, run_time=1.2))
        self.say("B", "Read it right to left, like doing the moves one after another.",
                 hold=2.0)

        # -- the one rule --------------------------------------------------------
        rule = T("the only rule:   a letter cancels its own inverse",
                 size=SMALL, color=MUTED).move_to(DOWN * 1.45)
        self.play(FadeIn(rule), run_time=0.6)

        # Cancel a A (positions 2 and 3) then the resulting pair, step by step.
        letters = list(raw)
        tokens = list(row)
        while True:
            hit = next((i for i in range(len(letters) - 1)
                        if letters[i] == mk.inv(letters[i + 1])), None)
            if hit is None:
                break
            pair = VGroup(tokens[hit], tokens[hit + 1])
            ring = SurroundingRectangle(pair, color=CORAL, buff=0.10, corner_radius=0.16)
            ring.set_stroke(CORAL, 2.4)
            self.play(Create(ring), run_time=0.5)
            self.play(
                FadeOut(pair, scale=0.4), FadeOut(ring, scale=0.9), run_time=0.7,
            )
            del letters[hit:hit + 2]
            del tokens[hit:hit + 2]
            if tokens:
                left = VGroup(*tokens)
                self.play(left.animate.arrange(RIGHT, buff=0.14).move_to(DOWN * 0.15),
                          run_time=0.6, rate_func=Look.ease)

        reduced = "".join(letters)
        self.say("A", f"Cancel what cancels, and this word is really just "
                      f"{mk.pretty(reduced)}.", hold=2.4)

        # -- freeness -------------------------------------------------------------
        self.play(FadeOut(rule), run_time=0.3)
        free_txt = T("and nothing else ever cancels", size=BODY, color=MINT)
        free_txt.move_to(DOWN * 1.45)
        self.play(FadeIn(free_txt, shift=UP * 0.12), run_time=0.7)
        self.say("B", "That is what free means. No hidden coincidence, no surprise "
                      "identity. Two different reduced words are two different moves.",
                 hold=3.0)

        # -- how many words -------------------------------------------------------
        self.play(FadeOut(VGroup(*tokens)) if tokens else Wait(0.01),
                  FadeOut(free_txt), FadeOut(alphabet), run_time=0.7)

        counts = [len(mk.words_of_length(k)) for k in range(1, 7)]
        bars = VGroup()
        for k, c in enumerate(counts, start=1):
            h = 0.30 + 2.4 * (np.log(c) / np.log(counts[-1]))
            bar = Rectangle(width=0.62, height=h)
            bar.set_stroke(width=0).set_fill(
                interpolate_color(ManimColor(C_B), ManimColor(C_A), (k - 1) / 5), opacity=0.9)
            cap = T(str(c), size=TINY, color=PAPER).next_to(bar, UP, buff=0.14)
            lab = T(f"length {k}", size=14, color=FAINT).next_to(bar, DOWN, buff=0.16)
            bars.add(VGroup(bar, cap, lab))
        bars.arrange(RIGHT, buff=0.42, aligned_edge=DOWN).move_to(DOWN * 0.55)

        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.14, run_time=1.8))
        growth = T("4 · 3ⁿ⁻¹  distinct words of length n", size=SMALL, color=MUTED)
        growth.next_to(bars, UP, buff=0.55)
        self.play(FadeIn(growth, shift=DOWN * 0.1), run_time=0.6)
        self.say("A", "The number of words explodes. Every extra letter multiplies "
                      "the possibilities by three.", hold=2.8)
        self.say("B", "Draw that explosion, and you get the picture the proof runs on.",
                 hold=2.4)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.0)
