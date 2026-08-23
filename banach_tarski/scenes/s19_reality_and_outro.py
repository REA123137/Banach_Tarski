"""
19 - Reality check, and the closing recap.

Why nobody has doubled a gold bar, what the theorem actually establishes, and
the chain of ideas laid out end to end - then back to the two balls the film
opened on.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustMorph, DustRecolor
from banach_tarski import mathkit as mk


class RealityCheck(BTScene):
    star_seed = 144

    def construct(self):
        self.chapter("12", "So why not gold?", "what the theorem does not say")

        # -- matter is grainy ---------------------------------------------------
        grid = VGroup()
        for i in range(-6, 7):
            for j in range(-4, 5):
                d = Dot(np.array([i * 0.42, j * 0.42, 0]), radius=0.075, color=GOLD)
                d.set_opacity(0.85)
                grid.add(d)
        grid.move_to(LEFT * 3.3 + UP * 0.45)
        ring = Circle(radius=2.0, color=GOLD).move_to(grid).set_stroke(GOLD, 2, opacity=0.5)

        self.play(FadeIn(ring), LaggedStart(*[FadeIn(d, scale=0.5) for d in grid],
                                            lag_ratio=0.004, run_time=1.8))
        self.say("A", "A real ball is made of atoms. A finite number of them.", hold=2.4)

        points = VGroup(
            T("a real ball has finitely many atoms", size=SMALL, color=PAPER),
            T("the theorem needs infinitely many points, in every piece",
              size=SMALL, color=MUTED),
            T("the pieces have no volume, so no scissors can find them",
              size=SMALL, color=MUTED),
            T("and no rule describes them - only a proof that they exist",
              size=SMALL, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        points.move_to(RIGHT * 3.2 + UP * 0.45)
        for line in points:
            line.align_to(points, LEFT)

        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.25) for p in points],
                              lag_ratio=0.28, run_time=2.4))
        self.say("B", "Every piece in the proof contains infinitely many points, "
                      "packed infinitely finely. Atoms do not.", hold=3.2)
        self.say("A", "And the pieces have no volume at all, so there is nothing "
                      "for a blade to follow.", hold=2.8)
        self.say("B", "You could not build them if you tried. Their existence is "
                      "proved, never exhibited.", hold=3.0)

        self.play(FadeOut(VGroup(grid, ring, points)), run_time=0.9)

        # -- the chain -------------------------------------------------------------
        chain = [
            ("the axiom of choice", CYAN),
            ("sets with no volume", VIOLET),
            ("a free group inside the rotations", GOLD),
            ("one ball becomes two", CORAL),
        ]
        nodes = VGroup()
        for text, color in chain:
            box = panel(3.05, 1.15, color=color)
            label = T(text, size=16, color=PAPER).scale_to_fit_width(2.65)
            label.move_to(box)
            nodes.add(VGroup(box, label))
        nodes.arrange(RIGHT, buff=0.55).move_to(UP * 0.35)

        arrows = VGroup(*[
            Arrow(nodes[i].get_right(), nodes[i + 1].get_left(), buff=0.10,
                  color=FAINT, stroke_width=2.6, max_tip_length_to_length_ratio=0.28)
            for i in range(len(nodes) - 1)
        ])

        self.play(FadeIn(nodes[0], scale=0.9), run_time=0.7)
        for i in range(1, len(nodes)):
            self.play(GrowArrow(arrows[i - 1], run_time=0.45),
                      FadeIn(nodes[i], scale=0.9, run_time=0.55))
        self.say("A", "The whole chain: assume you can always choose. That gives "
                      "sets with no volume.", hold=2.8)
        self.say("B", "Turns in three dimensions hide a free group. The free group "
                      "doubles itself. The ball follows.", hold=3.2)

        closing = T("nothing was created - the word volume simply stopped applying",
                    size=SMALL, color=MINT).move_to(DOWN * 1.85)
        self.play(FadeIn(closing, shift=UP * 0.12), run_time=0.8)
        self.say("A", "Nothing is created out of nothing. The theorem is about what "
                      "the word volume can mean, and where it gives up.", hold=3.4)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.1)


class Outro(BT3DScene):
    """The closing image: back to the two balls, and the card."""

    N = 3000
    R = 1.6

    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-90 * DEGREES, zoom=1.0)

        shell = mk.random_sphere(self.N, self.R, seed=3)
        cloud = Dust(shell, GOLD, size=3.0)
        cloud.depth_shade(self, radius=self.R)
        self.play(FadeIn(cloud), run_time=1.6)
        self.say("B", "One ball.", hold=1.4)

        half = self.N // 2
        left = mk.random_sphere(half, self.R, seed=11) + np.array([-2.6, 0, 0])
        right = mk.random_sphere(self.N - half, self.R, seed=12) + np.array([2.6, 0, 0])
        targets = np.vstack([left, right])

        self.play(DustMorph(cloud, targets, swirl=1.3, stagger=0.5, run_time=3.0))
        self.say("A", "Two balls. Same size. Same theorem.", hold=2.4)

        head = VGroup(
            T("BANACH", size=44, color=PAPER, weight=BOLD),
            T("–", size=44, color=GOLD, weight=BOLD),
            T("TARSKI", size=44, color=PAPER, weight=BOLD),
        ).arrange(RIGHT, buff=0.18)
        sub = T("1924", size=SMALL, color=MUTED).next_to(head, DOWN, buff=0.26)
        card = VGroup(head, sub).move_to(UP * 2.85)
        self.label(card)
        self.play(FadeIn(card, shift=UP * 0.2), run_time=1.0)

        credit = T("Stefan Banach  ·  Alfred Tarski  ·  Sur la décomposition des "
                   "ensembles de points en parties respectivement congruentes",
                   size=14, color=FAINT)
        credit.scale_to_fit_width(min(credit.width, 11.5)).move_to(DOWN * 2.35)
        self.label(credit)
        self.play(FadeIn(credit), run_time=1.0)
        self.wait(1.4)

        self.play(FadeOut(cloud), FadeOut(card), FadeOut(credit),
                  FadeOut(self._caption), run_time=2.0)
        self.wait(0.8)
