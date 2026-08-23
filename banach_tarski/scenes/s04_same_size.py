"""
04 - What "the same size" means.

A bijection, drawn as a wiring diagram.  The point is to retire counting and
replace it with pairing, so that "as many" survives the jump to infinity.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *

COUNT = 8


class SameSize(BTScene):
    star_seed = 21

    def construct(self):
        self.chapter("03", "The same size", "pairing, not counting")

        top = self.row([str(i) for i in range(1, COUNT + 1)], CYAN)
        bot = self.row([str(2 * i) for i in range(1, COUNT + 1)], VIOLET)
        top.move_to(UP * 1.95)
        bot.move_to(UP * 0.15)

        top_lbl = T(NAT, size=H3, color=CYAN).next_to(top, LEFT, buff=0.55)
        bot_lbl = T("2" + NAT, size=H3, color=VIOLET).next_to(bot, LEFT, buff=0.55)
        VGroup(top_lbl, bot_lbl).align_to(top_lbl, RIGHT)

        self.play(
            LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in top], lag_ratio=0.06,
                        run_time=1.1),
            FadeIn(top_lbl, shift=RIGHT * 0.2, run_time=0.6),
        )
        self.say("A", "Here are the counting numbers.", hold=1.3)

        self.play(
            LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in bot], lag_ratio=0.06,
                        run_time=1.1),
            FadeIn(bot_lbl, shift=RIGHT * 0.2, run_time=0.6),
        )
        self.say("B", "And here are only the even ones. Half as many, surely.", hold=2.0)

        # -- the wiring --------------------------------------------------------
        wires = VGroup(*[
            self.wire(top[i], bot[i], interpolate_color(ManimColor(CYAN), ManimColor(VIOLET),
                                                        i / (COUNT - 1)))
            for i in range(COUNT)
        ])
        self.play(LaggedStart(*[Create(w) for w in wires], lag_ratio=0.12, run_time=2.0))

        rule_lbl = T("n  →  2n", size=BODY, color=PAPER).move_to(DOWN * 1.30)
        self.play(FadeIn(rule_lbl, shift=UP * 0.12), run_time=0.6)
        self.say("A", "But pair them off: one with two, two with four, three with six. "
                      "Nothing on either side is left over.", hold=2.8)

        never = T("no number is skipped   ·   no number is used twice",
                  size=TINY, color=MUTED).next_to(rule_lbl, DOWN, buff=0.30)
        self.play(FadeIn(never), run_time=0.6)
        self.play(
            LaggedStart(*[Indicate(w, color=MINT, scale_factor=1.0) for w in wires],
                        lag_ratio=0.08, run_time=1.6)
        )
        self.say("B", "A perfect pairing is what \"the same size\" means. So there are "
                      "exactly as many even numbers as numbers.", hold=3.0)

        # -- the integers ------------------------------------------------------
        self.clear_caption()
        self.play(
            FadeOut(wires), FadeOut(rule_lbl), FadeOut(never),
            FadeOut(bot), FadeOut(bot_lbl), run_time=0.8,
        )

        z_vals = ["0", "1", "-1", "2", "-2", "3", "-3", "4"]
        zrow = self.row(z_vals, GOLD).move_to(UP * 0.15)
        z_lbl = T(INT, size=H3, color=GOLD).next_to(zrow, LEFT, buff=0.55)
        z_lbl.align_to(top_lbl, RIGHT)
        self.play(
            LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in zrow], lag_ratio=0.06,
                        run_time=1.1),
            FadeIn(z_lbl, shift=RIGHT * 0.2, run_time=0.6),
        )
        wires2 = VGroup(*[
            self.wire(top[i], zrow[i], interpolate_color(ManimColor(CYAN), ManimColor(GOLD),
                                                         i / (COUNT - 1)))
            for i in range(COUNT)
        ])
        self.play(LaggedStart(*[Create(w) for w in wires2], lag_ratio=0.10, run_time=1.8))
        self.say("A", "Same story for the whole integers - positives, negatives and zero. "
                      "Zip them together and they match up one for one.", hold=2.8)

        punch = T("infinite sets can be the same size as their own parts",
                  size=BODY, color=MINT).move_to(DOWN * 1.65)
        self.play(FadeIn(punch, shift=UP * 0.14), run_time=0.8)
        self.play(Circumscribe(punch, color=MINT, buff=0.22, run_time=1.6,
                               stroke_width=1.6))
        self.say("B", "Hold on to that. Everything strange that follows is this fact, "
                      "wearing a costume.", hold=2.8)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.0)

    # -- pieces ---------------------------------------------------------------
    @staticmethod
    def row(values, color) -> VGroup:
        cells = VGroup()
        for v in values:
            box = RoundedRectangle(width=0.82, height=0.72, corner_radius=0.12)
            box.set_stroke(color, 1.8, opacity=0.75).set_fill(color, opacity=0.07)
            txt = T(v, size=SMALL, color=PAPER).move_to(box)
            cells.add(VGroup(box, txt))
        return cells.arrange(RIGHT, buff=0.24)

    @staticmethod
    def wire(a: Mobject, b: Mobject, color) -> CubicBezier:
        start = a.get_bottom() + DOWN * 0.04
        end = b.get_top() + UP * 0.04
        c = CubicBezier(start, start + DOWN * 0.55, end + UP * 0.55, end)
        c.set_stroke(color, 2.2, opacity=0.85)
        return c
