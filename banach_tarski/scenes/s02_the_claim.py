"""
02 - The claim, stated precisely.

Before anything can be explained, the statement has to be pinned down: which
operations are allowed, and exactly what is being asserted.  The scene ends on
the equation V = 2V, which is the whole problem in four characters.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *


class TheClaim(BTScene):
    def construct(self):
        self.chapter("01", "The claim", "stated carefully, because the details are the theorem")

        # -- the ball ---------------------------------------------------------
        ball = Circle(radius=1.45, color=GOLD)
        ball.set_stroke(GOLD, 2.6).set_fill(GOLD, opacity=0.07)
        halo = glow(ball, GOLD, layers=12, spread=0.5, opacity=0.045)
        label = T("B", size=H3, color=GOLD, weight=BOLD).move_to(ball)
        vol = T("volume  V", size=SMALL, color=MUTED).next_to(ball, DOWN, buff=0.42)
        unit = VGroup(halo, ball, label, vol).move_to(LEFT * 3.4 + UP * 0.35)

        self.play(
            AnimationGroup(
                Create(ball, run_time=1.1, rate_func=Look.ease_out),
                FadeIn(halo, run_time=1.1),
                lag_ratio=0.1,
            ),
            FadeIn(label, scale=1.3, run_time=0.8),
        )
        self.play(FadeIn(vol, shift=UP * 0.12), run_time=0.6)
        self.say("A", "Start with a solid ball. Any size. Call its volume V.", hold=1.9)

        # -- the allowed moves ------------------------------------------------
        rules_title = T("the rules", size=TINY, color=MUTED).to_edge(UP, buff=1.15)
        rules_title.shift(RIGHT * 2.55)

        def rule_row(icon: Mobject, text: str) -> VGroup:
            t = T(text, size=SMALL, color=PAPER)
            return VGroup(icon, t).arrange(RIGHT, buff=0.42)

        rot_icon = Arc(radius=0.28, start_angle=-PI / 2, angle=1.55 * PI, color=CYAN, stroke_width=3)
        rot_icon.add(Triangle(color=CYAN, fill_opacity=1).set_stroke(width=0)
                     .scale(0.09).rotate(-PI / 2).move_to(rot_icon.get_end()))
        tr_icon = Arrow(LEFT * 0.3, RIGHT * 0.3, buff=0, color=CYAN, stroke_width=3,
                        max_tip_length_to_length_ratio=0.35)
        no_icon = VGroup(
            Line(UL * 0.22, DR * 0.22, color=CORAL, stroke_width=3),
            Line(DL * 0.22, UR * 0.22, color=CORAL, stroke_width=3),
        )
        no_icon2 = no_icon.copy()

        rules = VGroup(
            rule_row(rot_icon, "rotate"),
            rule_row(tr_icon, "translate"),
            rule_row(no_icon, "no stretching"),
            rule_row(no_icon2, "no adding new points"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        for r in rules[2:]:
            r[1].set_color(MUTED)
        rules.next_to(rules_title, DOWN, aligned_edge=LEFT, buff=0.5)

        self.play(FadeIn(rules_title, shift=DOWN * 0.1), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rules],
                              lag_ratio=0.22, run_time=1.8))
        self.say("B", "The only moves allowed are the moves of a rigid body: turn it, "
                      "slide it. Nothing bends, nothing grows.", hold=2.6)

        # -- five pieces ------------------------------------------------------
        self.play(FadeOut(rules_title), FadeOut(rules), run_time=0.6)

        rng = np.random.default_rng(2)
        chips = VGroup()
        for i in range(5):
            c = RoundedRectangle(width=0.92, height=0.92, corner_radius=0.14)
            c.set_stroke(PIECE_COLORS[i], 1.8).set_fill(PIECE_COLORS[i], opacity=0.12)
            dots = VGroup(*[
                Dot(radius=0.017, color=PIECE_COLORS[i]).move_to(
                    c.get_center() + np.array([rng.uniform(-0.34, 0.34),
                                               rng.uniform(-0.34, 0.34), 0]))
                for _ in range(38)
            ])
            chips.add(VGroup(c, dots))
        chips.arrange(RIGHT, buff=0.26).move_to(RIGHT * 3.1 + UP * 0.4)
        chip_cap = T("five pieces", size=TINY, color=MUTED).next_to(chips, DOWN, buff=0.36)

        arrow = Arrow(unit.get_right() + RIGHT * 0.15, chips.get_left() + LEFT * 0.15,
                      buff=0.1, color=FAINT, stroke_width=2.5,
                      max_tip_length_to_length_ratio=0.12)

        self.play(GrowArrow(arrow), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(c, scale=0.7) for c in chips],
                              lag_ratio=0.16, run_time=1.5))
        self.play(FadeIn(chip_cap), run_time=0.4)
        self.say("A", "Cut it into five pieces. Not five slices - five sets of points.",
                 hold=2.4)

        # -- two balls ---------------------------------------------------------
        self.play(FadeOut(VGroup(arrow, chip_cap)), run_time=0.4)

        def make_ball(pos, name):
            c = Circle(radius=1.05, color=GOLD).set_stroke(GOLD, 2.4).set_fill(GOLD, opacity=0.07)
            g = glow(c, GOLD, layers=10, spread=0.4, opacity=0.04)
            lab = T(name, size=BODY, color=GOLD, weight=BOLD).move_to(c)
            v = T("volume  V", size=TINY, color=MUTED).next_to(c, DOWN, buff=0.30)
            return VGroup(g, c, lab, v).move_to(pos)

        b1 = make_ball(RIGHT * 1.55 + UP * 0.4, "B₁")
        b2 = make_ball(RIGHT * 4.65 + UP * 0.4, "B₂")

        self.play(
            LaggedStart(
                *[Transform(chips[i], (b1 if i < 3 else b2).copy().set_opacity(0), remover=True)
                  for i in range(5)],
                lag_ratio=0.08, run_time=1.2,
            ),
            LaggedStart(FadeIn(b1, scale=0.8), FadeIn(b2, scale=0.8),
                        lag_ratio=0.3, run_time=1.4),
        )
        self.say("B", "Move the pieces. Rigidly. They fit together into two balls, "
                      "each the same size as the one you started with.", hold=2.8)

        # -- V = 2V -------------------------------------------------------------
        self.clear_caption()
        eq = T("V  =  2V", size=H2, color=PAPER, weight=BOLD).move_to(DOWN * 1.75)
        self.play(Write(eq), run_time=1.0)
        self.wait(0.6)
        strike = Line(eq.get_left() + LEFT * 0.2, eq.get_right() + RIGHT * 0.2, color=CORAL,
                      stroke_width=4)
        self.play(Create(strike), run_time=0.5)
        self.play(eq.animate.set_color(MUTED), run_time=0.4)

        out = T("so one of our assumptions about \"volume\" has to go",
                size=SMALL, color=CORAL)
        out.next_to(eq, DOWN, buff=0.38)
        self.play(FadeIn(out, shift=UP * 0.12), run_time=0.7)
        self.say("A", "Which sounds like a contradiction. It isn't. It's a warning about "
                      "the word volume.", hold=2.8)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.0)
