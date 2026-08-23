"""
11 - Orbits, and the choice nobody can describe.

The sphere splits into orbits.  To run the tree argument on all of them at
once you need one representative from each - and there are uncountably many
orbits with no rule for picking.  That is the Axiom of Choice, and it is the
only ingredient in the whole proof that anyone objects to.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustRecolor
from banach_tarski import mathkit as mk

R = 1.95
ORBIT_COLORS = [CORAL, CYAN, MINT, VIOLET, GOLD, MAGENTA]


class OrbitsAndChoice(BT3DScene):
    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-90 * DEGREES, zoom=0.95)

        title = T("orbits", size=H3, color=PAPER).move_to(UP * 3.30)
        self.label(title)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)

        shell = Dust(mk.random_sphere(1800, R, seed=5), "#3E3830", size=1.8)
        shell.depth_shade(self, radius=R, floor=0.25)
        self.play(FadeIn(shell), run_time=0.9)

        # -- a handful of orbits -------------------------------------------------
        seeds = mk.random_sphere(len(ORBIT_COLORS), R, seed=31)
        orbits = []
        for k, (seed, color) in enumerate(zip(seeds, ORBIT_COLORS)):
            pts = np.array([mk.apply_word(w, seed) for w in mk.words_up_to(4)])
            cloud = Dust(pts, color, size=5.2)
            cloud.depth_shade(self, radius=R, floor=0.18)
            orbits.append(cloud)

        self.play(FadeIn(orbits[0]), run_time=0.9)
        self.say("A", "Take one point and hit it with every word in the group. "
                      "That spray of points is its orbit.", hold=2.8)

        self.play(LaggedStart(*[FadeIn(o) for o in orbits[1:]], lag_ratio=0.28,
                              run_time=2.2))
        self.say("B", "Start somewhere else and you get a different orbit. "
                      "They never cross.", hold=2.6)

        self.begin_ambient_camera_rotation(rate=0.11)
        self.say("A", "Every point of the sphere sits in exactly one orbit. "
                      "The sphere is the orbits, stacked together.", hold=3.0)

        many = T("uncountably many of them", size=SMALL, color=MUTED).move_to(DOWN * 2.30)
        self.label(many)
        self.play(FadeIn(many, shift=UP * 0.1), run_time=0.6)

        crowd_seeds = mk.random_sphere(26, R, seed=77)
        crowd = []
        for i, seed in enumerate(crowd_seeds):
            pts = np.array([mk.apply_word(w, seed) for w in mk.words_up_to(3)])
            c = Dust(pts, "#6B6F7A", size=2.4)
            c.depth_shade(self, radius=R, floor=0.2)
            crowd.append(c)
        self.play(LaggedStart(*[FadeIn(c) for c in crowd], lag_ratio=0.05, run_time=2.0))
        self.wait(0.8)

        # -- the choice -----------------------------------------------------------
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(c) for c in crowd], FadeOut(many), run_time=0.8)

        self.say("B", "Now the awkward step. From each orbit, pick exactly one point.",
                 hold=2.6)

        picks = np.array([o.pts[len(o.pts) // 3] for o in orbits])
        chosen = Dust(picks, PAPER, size=14.0)
        self.play(
            *[DustRecolor(o, c, opacity=0.26, run_time=0.9)
              for o, c in zip(orbits, ORBIT_COLORS)],
        )
        self.play(FadeIn(chosen, scale=0.5), run_time=1.0)

        m_lbl = T("M   -   one point from every orbit", size=SMALL, color=PAPER)
        m_lbl.move_to(DOWN * 2.30)
        self.label(m_lbl)
        self.play(FadeIn(m_lbl, shift=UP * 0.1), run_time=0.6)
        self.say("A", "Call the collection M. With six orbits that is easy. "
                      "With uncountably many, there is no rule that does it.", hold=3.2)

        # -- the axiom -------------------------------------------------------------
        card = panel(9.2, 1.55)
        head = T("the axiom of choice", size=TINY, color=GOLD)
        body = T("given any family of non-empty sets, there is a set containing\n"
                 "exactly one member of each - even with no rule for choosing",
                 size=SMALL, color=PAPER, line_spacing=0.9)
        stack = VGroup(head, body).arrange(DOWN, buff=0.22).move_to(card)
        card_group = VGroup(card, stack).move_to(DOWN * 0.15)
        self.label(card_group)

        self.play(FadeOut(m_lbl), run_time=0.3)
        self.play(FadeIn(card_group, shift=UP * 0.2), run_time=0.9)
        self.say("B", "You are allowed to assume such a collection exists. That "
                      "assumption is the axiom of choice.", hold=3.0)
        self.say("A", "It sounds harmless. It is where the paradox comes from.",
                 hold=2.6)

        self.play(
            FadeOut(card_group), FadeOut(chosen), FadeOut(shell), FadeOut(title),
            *[FadeOut(o) for o in orbits], FadeOut(self._caption), run_time=1.2,
        )
