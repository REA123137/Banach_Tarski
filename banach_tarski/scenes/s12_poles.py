"""
12 - The snag, and the same old fix.

Every rotation pins two points: the ends of its axis.  Countably many words
means countably many pinned points, and the tree argument cannot touch them.
They are removed, the paradox is run on what is left, and then they are put
back with the hotel trick from chapter two.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustRotate, DustRecolor
from banach_tarski import mathkit as mk

R = 1.95
RHO_ANGLE = 1.0  # radians; irrational multiple of pi, so no power is the identity


def rho(k: int = 1) -> np.ndarray:
    """A rotation about the y-axis by an angle that never closes up."""
    t = RHO_ANGLE * k
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


class PolesAndTheHotelTrick(BT3DScene):
    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-90 * DEGREES, zoom=0.95)

        title = T("the fixed points", size=H3, color=PAPER).move_to(UP * 3.30)
        self.label(title)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)

        shell = Dust(mk.random_sphere(1800, R, seed=5), "#4A443A", size=1.9)
        shell.depth_shade(self, radius=R, floor=0.24)
        self.play(FadeIn(shell), run_time=0.9)

        # -- one axis, two poles ---------------------------------------------------
        axis = Line(LEFT * (R + 0.7), RIGHT * (R + 0.7)).set_stroke(C_A, 2.4, opacity=0.9)
        poles = Dust(np.array([[R, 0, 0], [-R, 0, 0]]), CORAL, size=15.0)
        self.play(Create(axis), run_time=0.8)
        self.play(FadeIn(poles, scale=0.5), run_time=0.7)
        self.say("A", "Every rotation leaves two points exactly where they were: "
                      "the two ends of its axis.", hold=2.8)

        self.play(DustRotate(shell, mk.R_a, about=ORIGIN, run_time=1.8))
        self.say("B", "Spin the sphere, and those two do not move at all.", hold=2.2)

        # -- countably many of them --------------------------------------------------
        self.play(FadeOut(axis), run_time=0.5)
        pole_pts = self.pole_set(depth=4)
        D = Dust(pole_pts, CORAL, size=5.0)
        D.depth_shade(self, radius=R, floor=0.2)
        self.play(FadeOut(poles), FadeIn(D), run_time=1.2)

        d_lbl = T("D   -   the poles of every word", size=SMALL, color=CORAL)
        d_lbl.move_to(DOWN * 2.30)
        self.label(d_lbl)
        self.play(FadeIn(d_lbl, shift=UP * 0.1), run_time=0.6)
        self.say("A", "One word, two poles. Countably many words, countably many "
                      "poles. Call that set D.", hold=3.0)

        self.begin_ambient_camera_rotation(rate=0.11)
        self.say("B", "The tree argument cannot touch them, so we take them out, "
                      "run the paradox on everything else, and put them back "
                      "afterwards.", hold=3.4)
        self.stop_ambient_camera_rotation()

        # -- the hotel trick, again -----------------------------------------------
        self.play(FadeOut(shell), run_time=0.7)
        self.play(FadeOut(d_lbl), run_time=0.3)

        trick = T("pick a rotation ρ whose powers never repeat", size=SMALL, color=MUTED)
        trick.move_to(DOWN * 2.30)
        self.label(trick)
        self.play(FadeIn(trick, shift=UP * 0.1), run_time=0.6)

        copies = []
        for k in range(1, 5):
            c = Dust(pole_pts @ rho(k).T, interpolate_color(ManimColor(CORAL),
                                                            ManimColor(VIOLET), k / 4),
                     size=4.2, opacity=0.85)
            c.depth_shade(self, radius=R, floor=0.2)
            copies.append(c)

        labels = VGroup(*[
            T(t, size=TINY, color=c) for t, c in (
                ("D", CORAL), ("ρD", "#F0708A"), ("ρ²D", "#D96BB0"),
                ("ρ³D", "#B571D8"), ("ρ⁴D", VIOLET))
        ]).arrange(RIGHT, buff=0.55).move_to(UP * 2.55)
        self.label(labels)

        self.play(FadeIn(labels[0]), run_time=0.4)
        for k, c in enumerate(copies):
            self.play(FadeIn(c, run_time=0.5), FadeIn(labels[k + 1], run_time=0.5))

        self.say("A", "Its powers give infinitely many disjoint copies of D, all "
                      "living on the sphere.", hold=2.8)

        self.say("B", "Now shift every copy one step along - exactly like moving "
                      "every guest up one room.", hold=2.8)

        allD = Group(D, *copies)
        self.play(*[DustRotate(c, rho(1), about=ORIGIN, run_time=2.2) for c in allD],
                  labels.animate.shift(RIGHT * 0.0))
        self.play(DustRecolor(D, INK, run_time=0.9), FadeOut(labels[0], run_time=0.9))

        self.say("A", "The copies swallow D, and the sphere comes back whole. "
                      "The exception costs nothing.", hold=3.0)

        self.play(
            *[FadeOut(c) for c in copies], FadeOut(D), FadeOut(labels),
            FadeOut(trick), FadeOut(title), FadeOut(self._caption), run_time=1.1,
        )

    # -- helpers --------------------------------------------------------------
    @staticmethod
    def pole_set(depth: int = 4) -> np.ndarray:
        """
        The two fixed points of every non-trivial word, out to a given length.

        Each word is a rotation; its axis is the eigenvector with eigenvalue 1,
        and the poles are where that axis meets the sphere.
        """
        pts = []
        for w in mk.words_up_to(depth):
            if not w:
                continue
            M = np.eye(3)
            for ch in reversed(w):
                M = mk.ROT[ch] @ M
            vals, vecs = np.linalg.eig(M)
            k = int(np.argmin(np.abs(vals - 1.0)))
            axis = np.real(vecs[:, k])
            axis = axis / np.linalg.norm(axis)
            pts.extend([axis * R, -axis * R])
        return np.array(pts)
