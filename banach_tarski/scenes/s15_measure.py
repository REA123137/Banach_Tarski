"""
15 - Four wishes about volume.

Banach-Tarski is usually filed under "impossible".  It is better read as a
proof that four reasonable demands on the word volume cannot all be met at
once in three dimensions.  This scene puts the four on the table and shows
which one has to go.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *

WISHES = [
    ("every set", "each and every subset\nof space gets a volume", CYAN),
    ("pieces add up", "split a set in two and\nthe volumes add", MINT),
    ("moving is free", "turning or sliding a set\nnever changes its volume", VIOLET),
    ("unit cube = 1", "so the numbers\nmean something", GOLD),
]

CARD_W = 3.05
INNER = CARD_W - 0.4


class FourWishes(BTScene):
    star_seed = 99

    def construct(self):
        self.chapter("09", "Four wishes about volume", "you may have any three")

        cards = VGroup()
        for i, (name, body, color) in enumerate(WISHES):
            card = panel(CARD_W, 2.5, color=color)
            num = T(str(i + 1), size=TINY, color=color, weight=BOLD)
            head = fit(T(name, size=24, color=PAPER, weight=BOLD), INNER)
            text = fit(T(body, size=15, color=MUTED, line_spacing=0.85), INNER)
            stack = VGroup(num, head, text).arrange(DOWN, buff=0.26).move_to(card)
            cards.add(VGroup(card, stack))
        cards.arrange(RIGHT, buff=0.30).move_to(UP * 0.55)

        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.25, scale=0.94) for c in cards],
                              lag_ratio=0.18, run_time=2.0))
        self.say("A", "Write down what you actually want from the word volume. "
                      "Four things, all of them obvious.", hold=3.0)

        for i, c in enumerate(cards):
            self.play(Indicate(c, color=WISHES[i][2], scale_factor=1.04, run_time=0.7))
        self.say("B", "Every set gets one. Pieces add up. Moving changes nothing. "
                      "And the unit cube measures one.", hold=3.2)

        # -- the collision --------------------------------------------------------
        verdict = T("in three dimensions, all four together are impossible",
                    size=BODY, color=CORAL)
        verdict.move_to(DOWN * 1.85)
        self.play(FadeIn(verdict, shift=UP * 0.14), run_time=0.8)
        self.say("A", "Banach and Tarski proved you cannot have all four at once - "
                      "not in three-dimensional space.", hold=3.0)

        # Wish 1 is the one that breaks.
        cross = VGroup(
            Line(cards[0].get_corner(UL), cards[0].get_corner(DR)),
            Line(cards[0].get_corner(DL), cards[0].get_corner(UR)),
        ).set_stroke(CORAL, 5)
        self.play(Create(cross), run_time=0.9)
        self.play(cards[0].animate.set_opacity(0.30), run_time=0.6)
        self.say("B", "The one that has to go is the first. Not every set can have "
                      "a volume.", hold=3.0)

        # -- what we keep -----------------------------------------------------------
        self.play(FadeOut(verdict), run_time=0.4)
        keep = T("Lebesgue measure keeps 2, 3 and 4 - and measures almost everything "
                 "you will ever meet", size=20, color=MINT)
        keep.move_to(DOWN * 1.85)
        self.play(FadeIn(keep, shift=UP * 0.12), run_time=0.8)
        self.say("A", "The measure mathematicians actually use gives up on the "
                      "monsters and keeps everything else.", hold=3.0)

        pieces = T("the five pieces of the ball are exactly those monsters",
                   size=20, color=CORAL)
        pieces.next_to(keep, DOWN, buff=0.34)
        self.play(FadeIn(pieces, shift=UP * 0.1), run_time=0.7)
        self.say("B", "And the five pieces of the ball are precisely the sets it "
                      "refuses to measure. That is why volume does not have to add up.",
                 hold=3.4)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.1)
