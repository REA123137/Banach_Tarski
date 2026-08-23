"""
05 - Doubling the hotel.

The rehearsal for the theorem, with no geometry in the way: split the guests
into two infinite halves, re-index each half, and each half on its own fills a
whole hotel.  One hotel in, two hotels out.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *

N = 12
W, H, GAP = 0.70, 0.84, 0.11


class DoublingTheHotel(BTScene):
    star_seed = 33

    def construct(self):
        self.chapter("04", "Doubling the hotel", "one infinite set, two infinite halves")

        rooms, guests, nums = self.hotel(N)
        block = VGroup(rooms, nums, guests).move_to(UP * 2.15)
        self.play(
            LaggedStart(*[FadeIn(r, shift=DOWN * 0.15) for r in rooms], lag_ratio=0.05,
                        run_time=1.2),
            LaggedStart(*[FadeIn(g, scale=0.5) for g in guests], lag_ratio=0.05,
                        run_time=1.4),
            LaggedStart(*[FadeIn(n) for n in nums], lag_ratio=0.04, run_time=0.9),
        )
        self.say("A", "One full hotel again. Now split the guests in two.", hold=2.0)

        # -- split by parity ---------------------------------------------------
        odd_c, even_c = MINT, CORAL
        self.play(
            *[guests[i].animate.set_color(odd_c if i % 2 == 0 else even_c) for i in range(N)],
            run_time=1.0,
        )
        tag_odd = T("odd rooms", size=TINY, color=odd_c)
        tag_even = T("even rooms", size=TINY, color=even_c)
        VGroup(tag_odd, tag_even).arrange(RIGHT, buff=0.9).next_to(block, DOWN, buff=0.45)
        self.play(FadeIn(tag_odd), FadeIn(tag_even), run_time=0.5)
        self.say("B", "Odd rooms in one group. Even rooms in the other. "
                      "Both groups are infinite.", hold=2.4)

        # -- two hotels --------------------------------------------------------
        self.play(FadeOut(tag_odd), FadeOut(tag_even), run_time=0.4)

        # Each output hotel shows its first half-dozen rooms and trails off, so
        # "completely full" is what the eye actually sees.
        left_rooms, _, left_nums = self.hotel(N // 2, guests=False, tail=True)
        right_rooms, _, right_nums = self.hotel(N // 2, guests=False, tail=True)
        left = VGroup(left_rooms, left_nums).scale(0.86).move_to(LEFT * 3.2 + DOWN * 0.35)
        right = VGroup(right_rooms, right_nums).scale(0.86).move_to(RIGHT * 3.2 + DOWN * 0.35)

        lab_l = T("hotel 1", size=TINY, color=odd_c).next_to(left, DOWN, buff=0.26)
        lab_r = T("hotel 2", size=TINY, color=even_c).next_to(right, DOWN, buff=0.26)

        self.play(
            FadeIn(left, shift=UP * 0.2), FadeIn(right, shift=UP * 0.2),
            FadeIn(lab_l), FadeIn(lab_r), run_time=1.0,
        )
        rule = T("2n − 1  →  n            2n  →  n", size=SMALL, color=MUTED)
        rule.move_to(DOWN * 1.62)
        self.play(FadeIn(rule), run_time=0.5)

        moves = []
        for i, g in enumerate(guests):
            k = i // 2                      # target room index in its own hotel
            dest = (left_rooms if i % 2 == 0 else right_rooms)[k]
            moves.append(g.animate.scale(0.72).move_to(dest.get_center() + UP * 0.015))
        self.play(LaggedStart(*moves, lag_ratio=0.05, run_time=2.6, rate_func=Look.ease))
        self.say("A", "Re-number each half, and each half fills a hotel of its own. "
                      "Every room, in both hotels, occupied.", hold=3.0)

        # -- the tally ---------------------------------------------------------
        self.play(FadeOut(rule), run_time=0.3)
        tally = VGroup(
            T("1 hotel", size=BODY, color=PAPER),
            T("→", size=BODY, color=GOLD),
            T("2 hotels", size=BODY, color=PAPER),
        ).arrange(RIGHT, buff=0.4).move_to(DOWN * 2.10)
        self.play(FadeIn(tally, shift=UP * 0.14), run_time=0.7)
        self.say("B", "Nobody was invented. Nobody was duplicated. The guests were just "
                      "re-labelled - and there are two full hotels.", hold=3.0)

        warn = T("this works because there is no \"total\" to conserve",
                 size=TINY, color=CORAL).move_to(UP * 3.35)
        self.play(FadeIn(warn), run_time=0.6)
        self.say("A", "Banach and Tarski do exactly this - but to points of a ball, "
                      "moved by rotations.", hold=2.8)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.0)

    # -- pieces ---------------------------------------------------------------
    def hotel(self, n: int, guests: bool = True, tail: bool = False):
        rooms = VGroup()
        for _ in range(n):
            r = RoundedRectangle(width=W, height=H, corner_radius=0.09)
            r.set_stroke(GRID, 1.8).set_fill(INK_SOFT, opacity=0.9)
            rooms.add(r)
        rooms.arrange(RIGHT, buff=GAP)
        nums = VGroup(*[
            T(str(i + 1), size=14, color=FAINT).next_to(r, DOWN, buff=0.13)
            for i, r in enumerate(rooms)
        ])
        people = VGroup()
        if guests:
            for r in rooms:
                head = Dot(radius=0.085, color=PAPER)
                body = RoundedRectangle(width=0.24, height=0.20, corner_radius=0.09)
                body.set_fill(PAPER, opacity=1).set_stroke(width=0)
                body.next_to(head, DOWN, buff=0.035)
                g = VGroup(head, body).move_to(r.get_center() + UP * 0.015)
                g.set_color(PAPER)
                people.add(g)
        if tail:
            nums.add(T("· · ·", size=16, color=FAINT).next_to(rooms, RIGHT, buff=0.26))
        return rooms, people, nums
