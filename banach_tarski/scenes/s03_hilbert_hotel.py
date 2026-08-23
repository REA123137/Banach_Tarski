"""
03 - Hilbert's hotel.

The cheapest place to meet the real idea: an infinite set can be moved onto a
proper part of itself.  Nothing is created; the room just opens up.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *

ROOMS = 11
W, H = 0.86, 1.0
GAP = 0.12


class HilbertHotel(BTScene):
    star_seed = 12

    def construct(self):
        self.chapter("02", "Hilbert's hotel", "where a full house always has room")

        hotel, rooms, numbers = self.build_hotel()
        hotel.move_to(UP * 0.55)
        self.play(
            LaggedStart(*[FadeIn(r, shift=DOWN * 0.2) for r in rooms],
                        lag_ratio=0.06, run_time=1.6),
            run_time=1.6,
        )
        self.play(LaggedStart(*[FadeIn(n) for n in numbers], lag_ratio=0.05, run_time=0.9))
        self.say("A", "A hotel with one room for every counting number. Room one, "
                      "room two, room three, and so on forever.", hold=2.4)

        # -- fill it ----------------------------------------------------------
        guests = VGroup(*[self.guest(rooms[i], MINT) for i in range(ROOMS)])
        self.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in guests],
                              lag_ratio=0.07, run_time=1.4))
        full = T("every room taken", size=SMALL, color=MINT).next_to(hotel, DOWN, buff=0.55)
        self.play(FadeIn(full, shift=UP * 0.1), run_time=0.5)
        self.say("B", "Tonight it is completely full. Every single room has a guest in it.",
                 hold=2.2)

        # -- one more guest ----------------------------------------------------
        newcomer = self.guest(rooms[0], GOLD)
        newcomer.move_to(rooms[0].get_center() + LEFT * 2.1 + DOWN * 1.9)
        halo = glow(newcomer[0], GOLD, layers=8, spread=0.28, opacity=0.07)
        halo.move_to(newcomer)
        arrive = VGroup(halo, newcomer)
        self.play(FadeIn(arrive, shift=RIGHT * 0.4), run_time=0.8)
        self.say("A", "Then one more traveller walks in.", hold=1.5)

        self.play(FadeOut(full), run_time=0.3)
        shift_lbl = T("everyone moves:   n  →  n + 1", size=SMALL, color=CYAN)
        shift_lbl.next_to(hotel, DOWN, buff=0.55)
        self.play(FadeIn(shift_lbl, shift=UP * 0.1), run_time=0.5)

        # Move each guest one room to the right; the last one walks off frame.
        moves = []
        for i in range(ROOMS - 1, -1, -1):
            if i == ROOMS - 1:
                moves.append(guests[i].animate.shift(RIGHT * (W + GAP) * 1.4).set_opacity(0))
            else:
                moves.append(guests[i].animate.move_to(
                    rooms[i + 1].get_center() + UP * 0.02))
        self.play(LaggedStart(*moves, lag_ratio=0.05, run_time=1.9,
                              rate_func=Look.ease), run_time=1.9)

        free = SurroundingRectangle(rooms[0], color=GOLD, buff=0.03, corner_radius=0.08)
        free.set_stroke(GOLD, 3)
        self.play(Create(free), run_time=0.6)
        self.play(arrive.animate.move_to(rooms[0].get_center() + UP * 0.02), run_time=0.9,
                  rate_func=Look.ease)
        self.play(FadeOut(free), run_time=0.4)
        self.say("B", "Everybody shifts up one room. Room one is empty, and nobody was "
                      "thrown out. The hotel is still full - and it took one more guest.",
                 hold=3.0)

        # -- infinitely many more ---------------------------------------------
        self.play(FadeOut(shift_lbl), run_time=0.3)
        bus_lbl = T("now a bus arrives with infinitely many:   n  →  2n",
                    size=SMALL, color=VIOLET)
        bus_lbl.next_to(hotel, DOWN, buff=0.55)
        self.play(FadeIn(bus_lbl, shift=UP * 0.1), run_time=0.5)
        self.say("A", "Now an infinite bus pulls up. Move the guest in room n to room 2n.",
                 hold=2.4)

        all_guests = VGroup(arrive[1], *guests[:-1])
        moves = []
        for i, g in enumerate(all_guests):
            target = 2 * (i + 1) - 1  # room index for 2n, zero-based
            if target < ROOMS:
                moves.append(g.animate.move_to(rooms[target].get_center() + UP * 0.02))
            else:
                moves.append(g.animate.shift(RIGHT * 3).set_opacity(0))
        self.play(LaggedStart(*reversed(moves), lag_ratio=0.06, run_time=2.2,
                              rate_func=Look.ease), FadeOut(halo, run_time=0.4))

        odd_boxes = VGroup(*[
            SurroundingRectangle(rooms[i], color=VIOLET, buff=0.03, corner_radius=0.08)
            .set_stroke(VIOLET, 2.6)
            for i in range(0, ROOMS, 2)
        ])
        self.play(LaggedStart(*[Create(b) for b in odd_boxes], lag_ratio=0.08, run_time=1.2))
        newbies = VGroup(*[self.guest(rooms[i], VIOLET) for i in range(0, ROOMS, 2)])
        self.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in newbies],
                              lag_ratio=0.08, run_time=1.2))
        self.play(FadeOut(odd_boxes), run_time=0.5)

        self.say("B", "Every odd room is now free - infinitely many of them - and the "
                      "whole bus checks in.", hold=2.6)
        self.say("A", "That is the trick in miniature. An infinite set can be shuffled "
                      "onto a piece of itself, and the leftovers are also infinite.",
                 hold=3.0)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.0)

    # -- pieces ---------------------------------------------------------------
    def build_hotel(self):
        rooms, numbers = VGroup(), VGroup()
        for i in range(ROOMS):
            r = RoundedRectangle(width=W, height=H, corner_radius=0.10)
            r.set_stroke(GRID, 2.0).set_fill(INK_SOFT, opacity=0.9)
            rooms.add(r)
        rooms.arrange(RIGHT, buff=GAP)
        for i, r in enumerate(rooms):
            n = T(str(i + 1), size=TINY, color=FAINT).next_to(r, DOWN, buff=0.16)
            numbers.add(n)
        dots = T("· · ·", size=BODY, color=FAINT).next_to(rooms, RIGHT, buff=0.34)
        hotel = VGroup(rooms, numbers, dots)
        return hotel, rooms, numbers

    @staticmethod
    def guest(room: Mobject, color: str) -> VGroup:
        head = Circle(radius=0.11, color=color).set_fill(color, opacity=1).set_stroke(width=0)
        body = RoundedRectangle(width=0.30, height=0.26, corner_radius=0.12)
        body.set_fill(color, opacity=1).set_stroke(width=0)
        body.next_to(head, DOWN, buff=0.045)
        g = VGroup(head, body)
        g.move_to(room.get_center() + UP * 0.02)
        return g
