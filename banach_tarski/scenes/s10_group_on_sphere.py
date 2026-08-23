"""
10 - The group, moved onto the sphere.

Everything so far was about words.  This is where the words become rotations:
two turns of about seventy degrees, about two different axes, generate a free
group inside the rotations of the sphere.  From here the tree picture is a
picture of the sphere.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustRotate
from banach_tarski.treekit import BRANCH_COLORS
from banach_tarski import mathkit as mk

R = 1.9
DEPTH = 6


class GroupOnTheSphere(BT3DScene):
    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-90 * DEGREES, zoom=0.95)

        title = T("two turns, one free group", size=H3, color=PAPER).move_to(UP * 3.30)
        self.label(title)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.7)

        # -- the sphere and its two axes ---------------------------------------
        shell = Dust(mk.random_sphere(2200, R, seed=5), "#5A5142", size=2.0)
        shell.depth_shade(self, radius=R, floor=0.22)
        self.play(FadeIn(shell), run_time=1.0)

        axis_a = self.axis(RIGHT, C_A)
        axis_b = self.axis(OUT, C_B)
        lab_a = T("a", size=BODY, color=C_A, weight=BOLD).move_to(RIGHT * 3.15)
        lab_b = T("b", size=BODY, color=C_B, weight=BOLD).move_to(UP * 2.78)
        self.label(lab_a)
        self.label(lab_b)

        self.play(Create(axis_a), FadeIn(lab_a), run_time=0.9)
        self.play(Create(axis_b), FadeIn(lab_b), run_time=0.9)
        self.say("A", "Two axes, at right angles. Turn about each one by the same "
                      "odd angle - the one whose cosine is exactly one third.", hold=3.0)

        angle = T("θ  =  arccos(1/3)  ≈  70.53°", size=SMALL, color=MUTED)
        angle.move_to(DOWN * 2.25)
        self.label(angle)
        self.play(FadeIn(angle, shift=UP * 0.1), run_time=0.6)
        self.say("B", "That angle is chosen so that no combination of the two turns "
                      "ever brings you back to where you started.", hold=3.0)

        # -- one point, one orbit -----------------------------------------------
        seed = mk.random_sphere(1, R, seed=17)[0]
        p0 = Dust(seed.reshape(1, 3), PAPER, size=13.0)
        self.play(FadeIn(p0, scale=0.4), run_time=0.7)
        self.say("A", "Start from a single point.", hold=1.6)

        self.play(DustRotate(shell, mk.R_a, about=ORIGIN, run_time=1.6),
                  DustRotate(p0, mk.R_a, about=ORIGIN, run_time=1.6))
        self.play(DustRotate(shell, mk.R_b, about=ORIGIN, run_time=1.6),
                  DustRotate(p0, mk.R_b, about=ORIGIN, run_time=1.6))
        self.say("B", "Every word in a and b sends it somewhere new.", hold=2.0)

        # -- the whole orbit ------------------------------------------------------
        self.play(FadeOut(p0), FadeOut(axis_a), FadeOut(axis_b),
                  FadeOut(lab_a), FadeOut(lab_b), run_time=0.7)

        by_depth = self.orbit_by_depth(seed)
        for d, cloud in enumerate(by_depth):
            self.play(FadeIn(cloud), run_time=0.55 if d < 3 else 0.42)
        self.say("A", "Do it for every word up to six letters, and the orbit already "
                      "looks like a fine spray across the sphere.", hold=3.0)

        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(2.4)

        counts = T("1 · 4 · 12 · 36 · 108 · 324 · 972   distinct points",
                   size=TINY, color=MUTED).move_to(DOWN * 2.25)
        self.label(counts)
        self.play(FadeOut(angle), FadeIn(counts), run_time=0.6)
        self.say("B", "Distinct. Never a repeat - because different words are "
                      "genuinely different rotations.", hold=2.8)

        self.say("A", "Which means the tree we drew is now drawn on the sphere, "
                      "one orbit at a time.", hold=2.8)
        self.stop_ambient_camera_rotation()

        self.play(
            *[FadeOut(c) for c in by_depth],
            FadeOut(shell), FadeOut(title), FadeOut(counts), FadeOut(self._caption),
            run_time=1.2,
        )

    # -- helpers --------------------------------------------------------------
    @staticmethod
    def axis(direction, color) -> VMobject:
        d = np.asarray(direction, dtype=float)
        line = Line(-d * (R + 0.75), d * (R + 0.75))
        line.set_stroke(color, 2.4, opacity=0.85)
        return line

    def orbit_by_depth(self, seed) -> list[Dust]:
        """One cloud per word length, coloured by which half of the group it's in."""
        clouds = []
        for d in range(DEPTH + 1):
            words = mk.words_of_length(d)
            pts = np.array([mk.apply_word(w, seed) for w in words])
            cols = [BRANCH_COLORS[mk.first_letter(w)] for w in words]
            size = max(11.0 * 0.78**d, 2.6)
            c = Dust(pts, cols, size=size)
            c.depth_shade(self, radius=R, floor=0.18)
            clouds.append(c)
        return clouds
