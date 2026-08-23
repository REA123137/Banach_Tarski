"""
01 - Cold open.

A single ball of light becomes two balls of light, with no explanation offered.
The rest of the film exists to make these thirty seconds believable.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustMorph, DustRecolor
from banach_tarski import mathkit as mk

N = 3000
R = 1.75


class ColdOpen(BT3DScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-90 * DEGREES, zoom=1.05)

        # -- a point of light --------------------------------------------------
        shell = mk.random_sphere(N, radius=R, seed=0)
        cloud = Dust(shell * 0.006, GOLD, size=3.0)
        cloud.depth_shade(self, radius=R)
        self.add(cloud)

        spark = glow_dot(ORIGIN, GOLD, radius=0.045, reach=10)
        self.add_fixed_in_frame_mobjects(spark)
        self.play(FadeIn(spark, run_time=0.7))
        self.play(
            DustMorph(cloud, shell, stagger=0.6, run_time=2.8),
            spark.animate.set_opacity(0.2).scale(1.5),
            run_time=2.8,
        )
        self.play(FadeOut(spark, run_time=0.9))

        # -- the title ---------------------------------------------------------
        head = VGroup(
            T("BANACH", size=52, color=PAPER, weight=BOLD),
            T("–", size=52, color=GOLD, weight=BOLD),
            T("TARSKI", size=52, color=PAPER, weight=BOLD),
        ).arrange(RIGHT, buff=0.20)
        sub = T("how one ball becomes two", size=SMALL, color=MUTED)
        sub.next_to(head, DOWN, buff=0.30)
        card = VGroup(head, sub).move_to(UP * 2.75)
        self.label(card)

        self.play(
            LaggedStart(*[FadeIn(m, shift=UP * 0.22, scale=1.04) for m in head],
                        lag_ratio=0.18, run_time=1.3)
        )
        self.play(FadeIn(sub, shift=UP * 0.12), run_time=0.8)
        self.wait(0.8)

        # -- the cut -----------------------------------------------------------
        # Colour by which half of the free group each particle will belong to.
        rng = np.random.default_rng(4)
        labels = rng.integers(0, 4, size=N)
        self.play(DustRecolor(cloud, [PIECE_COLORS[i] for i in labels], run_time=1.7))
        self.wait(0.3)

        loose = shell * rng.uniform(0.80, 1.30, size=(N, 1))
        self.play(DustMorph(cloud, loose, stagger=0.55, run_time=1.6))

        # -- two balls ---------------------------------------------------------
        goes_left = labels < 2
        nl, nr = int(goes_left.sum()), int((~goes_left).sum())
        left = mk.random_sphere(nl, radius=R, seed=1) + np.array([-2.75, 0, 0])
        right = mk.random_sphere(nr, radius=R, seed=2) + np.array([2.75, 0, 0])
        targets = np.zeros_like(loose)
        targets[goes_left] = left
        targets[~goes_left] = right

        self.play(DustMorph(cloud, targets, swirl=1.4, stagger=0.5, run_time=3.2))
        cloud.remove_updater(cloud.get_updaters()[0])
        self.play(DustRecolor(cloud, GOLD, run_time=1.2))
        self.wait(0.6)

        eq = T("=", size=H1, color=GOLD, weight=BOLD).move_to(ORIGIN)
        self.label(eq)
        self.play(FadeIn(eq, scale=1.6), run_time=0.55)

        self.say("A", "One solid ball. Cut into five pieces. Reassembled into two balls, "
                      "each the size of the original.", hold=2.8)
        self.say("B", "Nothing was stretched. Nothing was filled in. And it is a theorem.",
                 hold=2.8)

        self.play(
            FadeOut(cloud, run_time=1.5),
            FadeOut(eq, run_time=1.0),
            FadeOut(card, run_time=1.2),
            FadeOut(self._caption, run_time=1.0),
        )
        self.wait(0.4)
