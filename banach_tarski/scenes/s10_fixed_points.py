"""Scene 10 — 14:05-15:25 · The problem: one rotation, and only one.

    "ON SCREEN  L = P₁ ⊔ P₂ ⊔ P₃ ⊔ P₄  with  Pᵢ ∩ Pⱼ = ∅  (i ≠ j)"

    "ANIMATION – A rotation about an axis.  The sphere turns, but the two points
    where the axis pierces it stay perfectly still.  They flash red.  Then
    dozens of axes are superimposed, each with its pair of red points."

    "ANIMATION IDEA – Long exposure.  Film the rotating sphere with light
    trails, like a night photograph.  Every point leaves a streak.  Two points,
    and only two, stay sharp: the fixed points."

The axes are the genuine ones: :func:`banach_tarski.rotations.fixed_point_axes`
returns the eigenvector of eigenvalue 1 of each short word's matrix.
"""

from __future__ import annotations

# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from manim import (
    DOWN,
    FadeIn,
    FadeOut,
    LaggedStart,
    Scene,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, space, theme
from banach_tarski.rotations import A, axis_of, fixed_point_axes, rotation_about


class S10Partition(Scene):
    """What a partition is, and what would break it."""

    def construct(self):
        theme.apply_defaults(self)

        title = theme.head(theme.body("a partition of the ball", size=34, color=theme.INK_DIM))
        formula = theme.formula(
            r"L \;=\; P_1 \sqcup P_2 \sqcup P_3 \sqcup P_4"
            r"\qquad \text{with}\quad P_i \cap P_j = \emptyset \;\; (i \neq j)",
            size=38,
        )
        plain = theme.body("pieces that do not overlap, and that together cover everything",
                           size=30, color=theme.INK_DIM)
        danger = VGroup(
            theme.body("A point must be writable in exactly one way", size=32),
            theme.body("as a rotation applied to a representative.", size=32),
            theme.body("Two rotations giving the same point would put it in two pieces at once.",
                       size=30, color=theme.REFUSE),
        ).arrange(DOWN, buff=0.32)
        # the whole block is laid out before any of it is played, so no line
        # moves once the viewer has read it
        block = theme.stage(VGroup(formula, plain, danger).arrange(DOWN, buff=0.55))

        self.play(FadeIn(title, run_time=0.7), Write(formula, run_time=2.0))
        self.play(FadeIn(plain, run_time=0.8))
        self.wait(0.8)
        anim.write_lines(self, danger, per_line=1.2, lag=0.75)
        self.wait(2.0)
        self.play(FadeOut(VGroup(title, block), run_time=0.8))


class S10FixedPoints(Scene):
    """The sphere turns; two points do not."""

    def construct(self):
        theme.apply_defaults(self)

        stage = space.Stage(space.View(yaw=-0.55, pitch=0.22, scale=2.15))
        stage.view.origin = np.array([0.0, -0.35, 0.0])
        shell = space.sphere_cloud(11000, color="#4C4A45", size=2.2, size_far=0.8)
        stage.add(shell)
        for wire in space.wire_sphere(1.0, 10, 5, color="#171717", width=1.0):
            stage.add(wire)

        axis_vec = np.array([0.0, 0.0, 1.0])
        axis_line = space.Wire(space.axis_segment(axis_vec, 1.12), color=theme.INK_DIM,
                               width=1.6, closed=False)
        axis_line.mobject.set_stroke(opacity=0.45)
        stage.add(axis_line)
        poles = [space.Marker(axis_vec, color=theme.REFUSE, radius=0.085, halo=3.2),
                 space.Marker(-axis_vec, color=theme.REFUSE, radius=0.085, halo=3.2)]
        stage.add(*poles)
        stage.install(self)
        stage.fit(spread=1.12)

        head = theme.body("the sphere turns — the two points on the axis do not",
                          size=30, color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.8))

        # the sphere really turns: the shell's own points are rotated
        for _ in range(2):
            self.play(space.rotate_cloud(shell, A, run_time=2.0))
            self.play(
                *[
                    p.mobject.animate(run_time=0.30).scale(1.35)
                    for p in poles
                ],
            )
            self.play(*[p.mobject.animate(run_time=0.30).scale(1 / 1.35) for p in poles])

        # then dozens of axes, each with its pair of red points
        self.play(FadeOut(head, run_time=0.5))
        head2 = theme.body("and every rotation of G has its own pair", size=30,
                           color=theme.INK_DIM)
        theme.head(head2)
        self.play(FadeIn(head2, run_time=0.6))

        extra = []
        for vec in fixed_point_axes(3)[:22]:
            line = space.Wire(space.axis_segment(vec, 1.10), color=theme.GHOST, width=1.0,
                              closed=False)
            line.mobject.set_stroke(opacity=0.22)
            extra.append(line)
            extra.append(space.Marker(vec, color=theme.REFUSE, radius=0.045))
            extra.append(space.Marker(-vec, color=theme.REFUSE, radius=0.045))
        stage.add(*extra)
        for solid in extra:
            solid.mobject.set_opacity(0.0)
        self.play(
            LaggedStart(
                *[s.mobject.animate(run_time=0.35).set_opacity(1.0) for s in extra],
                lag_ratio=0.02,
            )
        )
        self.play(stage.orbit(d_yaw=1.5, run_time=4.0))
        self.wait(1.2)
        self.play(FadeOut(head2, run_time=0.6))


class S10Removed(Scene):
    """We set them aside — and we promise to get them back."""

    def construct(self):
        theme.apply_defaults(self)

        lines = VGroup(
            theme.formula(r"L \;=\; \{\,(x,y,z) \;:\; x^2 + y^2 + z^2 \leq 1\,\}", size=36),
            theme.formula(r"L_0 \;=\; L \setminus \{(0,0,0)\}", size=36),
            theme.formula(
                r"D \;=\; \{\, p \in L_0 \;:\; \rho(p) = p \text{ for some } "
                r"\rho \in G,\; \rho \neq \mathrm{Id} \,\}",
                size=36,
            ),
        ).arrange(DOWN, buff=0.55)
        work = theme.formula(r"\text{we work on}\quad L_0 \setminus D", size=44,
                             color=theme.GOLD)
        block = theme.stage(VGroup(lines, work).arrange(DOWN, buff=0.75))

        promise = theme.foot(theme.body(
            "and I promise you now: we will get all of it back, "
            "the centre and the axes, before the end.",
            size=28,
            color=theme.INK_DIM,
        ))

        anim.write_lines(self, lines, per_line=1.6, lag=0.85)
        self.wait(1.0)
        self.play(Write(work, run_time=1.2))
        self.play(FadeIn(promise, run_time=1.0))
        self.wait(2.4)
        self.play(FadeOut(VGroup(block, promise), run_time=0.8))


class S10LongExposure(Scene):
    """ANIMATION IDEA — long exposure.

        "Film the rotating sphere with light trails, like a night photograph.
        Every point leaves a streak.  Two points, and only two, stay sharp […]
        Then superimpose twenty different rotations, and the screen becomes a
        sky of star trails with, here and there, perfectly motionless stars."
    """

    def construct(self):
        theme.apply_defaults(self)

        stage = space.Stage(space.View(yaw=-0.5, pitch=0.24, scale=2.35))
        stage.view.origin = np.array([0.0, -0.15, 0.0])

        # one rotation first: the streaks and the two sharp points
        seeds = space.sphere_points(900, seed=13)
        smear, frac = space.trails(seeds, A, samples=30, arc=1.0)
        colours = np.tile(space.rgb_of(theme.INK), (len(smear), 1))
        streaks = space.Cloud(smear, colors=colours, size=1.5, size_far=0.6, fog=0.7, bands=6)
        streaks.alpha = 0.20 + 0.75 * frac  # the head of each streak is the brightest
        stage.add(streaks)

        axis_vec = np.array([0.0, 0.0, 1.0])
        sharp = [space.Marker(axis_vec, color="#FFFFFF", radius=0.075, halo=3.6),
                 space.Marker(-axis_vec, color="#FFFFFF", radius=0.075, halo=3.6)]
        stage.add(*sharp)
        stage.install(self)

        head = theme.caption("one rotation · 30-second exposure", size=24)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.8))
        self.play(stage.orbit(d_yaw=0.8, run_time=3.5))
        self.wait(0.6)

        # then twenty rotations at once: a sky of star trails
        self.play(FadeOut(head, run_time=0.4))
        head2 = theme.caption("twenty rotations · every point streaks, a few stay still", size=24)
        theme.head(head2)
        self.play(FadeIn(head2, run_time=0.6))

        more = []
        for i, vec in enumerate(fixed_point_axes(3)[:20]):
            rot = rotation_about(vec, 1.05)
            pts = space.sphere_points(120, seed=40 + i)
            smear_i, frac_i = space.trails(pts, rot, samples=18, arc=1.0)
            cloud = space.Cloud(smear_i, colors=theme.INK, size=1.2, size_far=0.5, fog=0.7,
                                bands=5)
            cloud.alpha = 0.08 + 0.45 * frac_i
            cloud.opacity = 0.38
            more.append(cloud)
            stage.add(cloud)
            still = space.Marker(vec, color="#FFFFFF", radius=0.075, halo=4.0)
            stage.add(still)
            more.append(still)

        self.play(stage.orbit(d_yaw=1.6, d_pitch=0.18, run_time=6.0))
        self.wait(1.0)

        note = theme.body("the idea of a fixed point, without a word", size=28,
                          color=theme.INK_DIM)
        theme.foot(note)
        self.play(FadeIn(note, run_time=0.9))
        self.wait(2.0)
        self.play(FadeOut(VGroup(head2, note), run_time=0.8))
