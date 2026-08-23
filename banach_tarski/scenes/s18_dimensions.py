"""
18 - Why the line and the plane are safe.

The paradox is not about infinity in general, and not about the axiom of
choice alone.  It needs a free group of rotations, and the plane has none:
its rotations all commute.  Below three dimensions there is an invariant,
finitely additive measure on every set, and nothing can be doubled.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *

CENTER_L = LEFT * 3.5 + UP * 0.55
CENTER_R = RIGHT * 3.5 + UP * 0.55


def marked_disc(center, color) -> VGroup:
    disc = Circle(radius=1.25).move_to(center)
    disc.set_stroke(color, 2.2).set_fill(color, opacity=0.06)
    wedge = AnnularSector(inner_radius=0, outer_radius=1.25, angle=32 * DEGREES,
                          start_angle=0)
    wedge.set_fill(color, opacity=0.55).set_stroke(width=0).move_arc_center_to(center)
    pin = Dot(center + RIGHT * 1.25, radius=0.07, color=PAPER)
    return VGroup(disc, wedge, pin)


class WhyNotInThePlane(BTScene):
    star_seed = 123

    def construct(self):
        self.chapter("11", "Why the plane is safe", "the paradox needs room to turn")

        head = T("two turns in the plane", size=H3, color=PAPER).move_to(UP * 2.65)
        self.play(FadeIn(head, shift=DOWN * 0.1), run_time=0.6)

        left = marked_disc(CENTER_L, C_A)
        right = marked_disc(CENTER_R, C_B)
        lab_l = T("first 40°, then 100°", size=SMALL, color=C_A)
        lab_r = T("first 100°, then 40°", size=SMALL, color=C_B)
        lab_l.next_to(left, DOWN, buff=0.55)
        lab_r.next_to(right, DOWN, buff=0.55)

        self.play(FadeIn(left), FadeIn(right), run_time=0.9)
        self.play(FadeIn(lab_l), FadeIn(lab_r), run_time=0.5)
        self.say("A", "The same experiment, in the plane. Two turns, in both orders.",
                 hold=2.4)

        self.play(
            Rotate(left, 40 * DEGREES, about_point=CENTER_L, run_time=1.4,
                   rate_func=Look.ease),
            Rotate(right, 100 * DEGREES, about_point=CENTER_R, run_time=1.4,
                   rate_func=Look.ease),
        )
        self.play(
            Rotate(left, 100 * DEGREES, about_point=CENTER_L, run_time=1.4,
                   rate_func=Look.ease),
            Rotate(right, 40 * DEGREES, about_point=CENTER_R, run_time=1.4,
                   rate_func=Look.ease),
        )

        same = T("=", size=H1, color=MINT, weight=BOLD).move_to(UP * 0.55)
        self.play(FadeIn(same, scale=1.5), run_time=0.6)
        self.say("B", "Identical. In the plane the order never matters - "
                      "the turns simply add.", hold=2.8)

        why = T("a + b  =  b + a       so there is no free group here",
                size=SMALL, color=MUTED).move_to(DOWN * 1.75)
        self.play(FadeIn(why, shift=UP * 0.12), run_time=0.7)
        self.say("A", "Which means no tree, no four pieces, no paradox. The whole "
                      "machine needs turns that refuse to commute.", hold=3.2)

        # -- the ladder -------------------------------------------------------------
        self.play(
            FadeOut(VGroup(left, right, lab_l, lab_r, same, why, head)), run_time=0.8
        )

        rows = [
            ("the line", "ℝ", "rotations and slides commute", "safe", MINT),
            ("the plane", "ℝ²", "rotations about a point commute", "safe", MINT),
            ("space", "ℝ³", "rotations contain a free group", "paradoxical", CORAL),
            ("higher up", "ℝⁿ", "the same reason, in every dimension above three", "paradoxical", CORAL),
        ]
        table = VGroup()
        for name, sym, reason, verdict, color in rows:
            n = T(name, size=SMALL, color=PAPER)
            s = fit(M(sym, size=SMALL, color=color), 1.6)
            r = fit(T(reason, size=16, color=MUTED), 4.3)
            v = T(verdict, size=SMALL, color=color, weight=BOLD)
            n.move_to(LEFT * 5.6, aligned_edge=LEFT)
            s.move_to(LEFT * 2.35, aligned_edge=LEFT)
            r.move_to(LEFT * 0.6, aligned_edge=LEFT)
            v.move_to(RIGHT * 4.05, aligned_edge=LEFT)
            table.add(VGroup(n, s, r, v))
        table.arrange(DOWN, buff=0.62, aligned_edge=LEFT).move_to(UP * 0.55)

        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.25) for r in table],
                              lag_ratio=0.22, run_time=2.0))
        self.say("B", "One and two dimensions are safe. Banach proved it: there "
                      "every set has an area, invariant under every rigid motion.",
                 hold=3.4)
        self.say("A", "From three dimensions up, the rotations are rich enough to "
                      "hide a free group - and the ball comes apart.", hold=3.2)

        note = T("nothing here is about the axiom of choice being wrong - the plane "
                 "has it too", size=TINY, color=MUTED).move_to(DOWN * 2.20)
        self.play(FadeIn(note), run_time=0.7)
        self.say("B", "Note what this is not. The plane has the axiom of choice as "
                      "well. The difference is geometry, not logic.", hold=3.2)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.1)
