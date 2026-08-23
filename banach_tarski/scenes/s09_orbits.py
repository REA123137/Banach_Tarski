"""Scene 9 — 11:15-14:05 · Orbits, representatives, and the axiom of choice.

    "ANIMATION – A single point.  Its images appear one by one, faster and
    faster, until they form a dust scattered over the sphere."

    "ANIMATION – On the sphere, one point in each dust cloud lights up white.
    The set of white points is M."

    "ANIMATION – Infinitely many shoeboxes: in every one, the left shoe lights
    up, all at once.  Then infinitely many drawers of identical socks: nothing
    lights up."

    "ANIMATION IDEA – The impossible hand. […] A human hand hesitates, reaches,
    withdraws.  Then the HAND OF THE AXIOM OF CHOICE appears: translucent, no
    texture, no cast shadow, duplicated infinitely, touching every shelf at
    once."
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
    LEFT,
    LaggedStart,
    RIGHT,
    Scene,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, motifs, space, theme
from banach_tarski.rotations import many_orbits, orbit

ORBIT_COLORS = [theme.C_A, theme.C_B, theme.C_BI, theme.C_AI, "#7FB3FF", "#FF9BD2"]


class S09Orbit(Scene):
    """The orbit of a point: its complete itinerary, scattered over the sphere."""

    def construct(self):
        theme.apply_defaults(self)

        formulas = VGroup(
            theme.formula("G = ⟨A, B⟩        ρ ∈ G", size=38),
            theme.formula("orbit of p  =  { ρ(p) : ρ ∈ G }", size=38),
        ).arrange(DOWN, buff=0.32)
        formulas.to_edge(UP, buff=0.55)
        self.play(Write(formulas[0], run_time=1.2))

        stage = space.Stage(space.View(yaw=-0.6, pitch=0.26, scale=2.0))
        stage.view.origin = np.array([0.0, -0.7, 0.0])
        shell = space.sphere_cloud(6000, color="#2A2A2A", size=1.6, size_far=0.6)
        stage.add(shell)
        for wire in space.wire_sphere(1.0, 10, 5, color="#161616", width=1.0):
            stage.add(wire)

        seed = np.array([0.42, -0.30, 0.86])
        seed /= np.linalg.norm(seed)
        start = space.Marker(seed, color=theme.INK, radius=0.075, halo=3.4)
        stage.add(start)
        stage.install(self)
        stage.spin(self, speed=0.11)
        self.wait(1.0)

        self.play(Write(formulas[1], run_time=1.4))

        pts, words = orbit(seed, max_length=6)
        dust = space.Cloud(pts, colors=theme.C_B, size=2.6, size_far=1.0, fog=0.8, bands=6)
        stage.add(dust)
        self.play(space.reveal_cloud(dust, run_time=5.0, power=3.2))
        self.wait(0.6)

        gloss = theme.body(
            "every place that point can be sent by our motions", size=30, color=theme.INK_DIM
        )
        gloss.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(gloss, run_time=0.8))
        self.wait(2.2)
        self.play(FadeOut(VGroup(formulas, gloss), run_time=0.8),
                  space.fade_cloud(dust, 0.0, run_time=0.8))


class S09Representatives(Scene):
    """One point per orbit lights up white.  The set of white points is M."""

    def construct(self):
        theme.apply_defaults(self)

        stage = space.Stage(space.View(yaw=-0.5, pitch=0.24, scale=2.1))
        stage.view.origin = np.array([0.0, -0.45, 0.0])
        for wire in space.wire_sphere(1.0, 10, 5, color="#141414", width=1.0):
            stage.add(wire)

        orbits = many_orbits(count=6, max_length=4, seed=6)
        clouds = []
        for (rep, pts, _), colour in zip(orbits, ORBIT_COLORS):
            cloud = space.Cloud(pts, colors=colour, size=2.3, size_far=0.9, fog=0.8, bands=5)
            clouds.append(cloud)
            stage.add(cloud)
        stage.install(self)
        stage.spin(self, speed=0.10)

        head = theme.body("the sphere is divided into orbits, which never touch",
                          size=30, color=theme.INK_DIM)
        head.to_edge(UP, buff=0.55)
        self.play(FadeIn(head, run_time=0.9))
        self.wait(1.6)

        # in each orbit, one point — exactly one — is chosen
        marks = []
        for (rep, _, _) in orbits:
            marks.append(space.Marker(rep, color="#FFFFFF", radius=0.065, halo=3.0))
        stage.add(*marks)
        for m in marks:
            m.mobject.set_opacity(0.0)
        self.play(
            LaggedStart(
                *[m.mobject.animate(run_time=0.5).set_opacity(1.0) for m in marks],
                lag_ratio=0.22,
            ),
            *[space.fade_cloud(c, 0.55, run_time=1.4) for c in clouds],
        )

        label = theme.formula("M  =  the set of all these representatives", size=34)
        label.to_edge(DOWN, buff=1.25)
        self.play(Write(label, run_time=1.4))
        self.wait(1.2)

        key = theme.formula(
            "every point p  is  p = ρ(m)   for a unique m ∈ M  and a unique ρ ∈ G",
            size=30,
            color=theme.GOLD,
        )
        key.to_edge(DOWN, buff=0.5)
        self.play(Write(key, run_time=2.0))
        self.wait(1.0)

        plain = theme.caption("a starting address, and an itinerary", size=24)
        plain.next_to(head, DOWN, buff=0.25)
        self.play(FadeIn(plain, run_time=0.7))
        self.wait(2.2)
        self.play(FadeOut(VGroup(head, plain, label, key), run_time=0.8))


class S09ShoesSocks(Scene):
    """Russell's example: shoes have a rule, socks do not."""

    def construct(self):
        theme.apply_defaults(self)

        head = theme.body("infinitely many pairs of shoes", size=32, color=theme.INK_DIM)
        head.to_edge(UP, buff=0.7)
        self.play(FadeIn(head, run_time=0.7))

        boxes = VGroup()
        lefts = VGroup()
        for i in range(12):
            box = motifs.container(2.05, 1.25)
            left = motifs.shoe(True, scale=0.62, color=theme.INK)
            right = motifs.shoe(False, scale=0.62, color=theme.INK)
            pair = VGroup(left, right).arrange(RIGHT, buff=0.14).move_to(box)
            boxes.add(VGroup(box, pair))
            lefts.add(left)
        boxes.arrange_in_grid(rows=3, cols=4, buff=0.28).scale_to_fit_width(9.6)
        boxes.move_to(UP * 0.25)
        self.play(FadeIn(boxes, lag_ratio=0.06, run_time=1.2))
        self.wait(0.6)

        rule = theme.body("“I take the left one.”", size=34, color=theme.GOLD)
        rule.to_edge(DOWN, buff=0.55)
        self.play(
            Write(rule, run_time=1.0),
            *[
                shoe.animate(run_time=0.8).set_stroke(theme.GOLD, width=3.0).set_fill(
                    theme.GOLD, opacity=0.30
                )
                for shoe in lefts
            ],
        )
        note = theme.caption("one sentence, and the choice is made everywhere at once", size=24)
        note.next_to(rule, UP, buff=0.28)
        self.play(FadeIn(note, run_time=0.7))
        self.wait(2.0)
        self.play(FadeOut(VGroup(boxes, rule, note, head), run_time=0.7))

        # -- socks --------------------------------------------------------
        head2 = theme.body("infinitely many drawers of identical socks", size=32,
                           color=theme.INK_DIM)
        head2.to_edge(UP, buff=0.7)
        self.play(FadeIn(head2, run_time=0.7))

        drawers = VGroup()
        for i in range(12):
            drawer = motifs.container(2.05, 1.25)
            pair = VGroup(motifs.sock(0.72), motifs.sock(0.72)).arrange(RIGHT, buff=0.22)
            pair.move_to(drawer)
            handle = theme.rule(width=0.6, color=theme.GHOST, stroke=3.0)
            handle.move_to(drawer.get_bottom() + UP * 0.14)
            drawers.add(VGroup(drawer, pair, handle))
        drawers.arrange_in_grid(rows=3, cols=4, buff=0.28).scale_to_fit_width(9.6)
        drawers.move_to(UP * 0.25)
        self.play(FadeIn(drawers, lag_ratio=0.06, run_time=1.2))
        self.wait(1.0)

        nothing = theme.body("there is no left one.", size=34, color=theme.REFUSE)
        nothing.to_edge(DOWN, buff=0.55)
        self.play(Write(nothing, run_time=1.0))
        self.wait(1.2)

        verdict = theme.body("our orbits are socks.", size=34, color=theme.GOLD)
        verdict.move_to(nothing)
        self.play(FadeOut(nothing, run_time=0.4), FadeIn(verdict, run_time=0.6))
        self.wait(2.0)
        self.play(FadeOut(VGroup(drawers, verdict, head2), run_time=0.8))


class S09AxiomCard(Scene):
    """The axiom, stated once, and what it does not say."""

    def construct(self):
        theme.apply_defaults(self)

        title = theme.display("the axiom of choice", size=54, color=theme.CHOICE)
        title.to_edge(UP, buff=1.1)
        statement = theme.body(
            "For any family of non-empty sets, there is a function picking one element from each.",
            size=32,
        )
        statement.next_to(title, DOWN, buff=0.75)
        if statement.width > 12.5:
            statement.scale_to_fit_width(12.5)
        self.play(Write(title, run_time=1.0))
        self.play(Write(statement, run_time=2.2))
        self.wait(0.8)

        caveats = VGroup(
            theme.body("It asserts that the choice exists.", size=32, color=theme.INK_DIM),
            theme.body("It does not say how to make it.", size=32, color=theme.INK_DIM),
            theme.body("No recipe will ever exist — that has been proved.", size=32,
                       color=theme.REFUSE),
        ).arrange(DOWN, buff=0.34)
        caveats.next_to(statement, DOWN, buff=0.9)
        anim.write_lines(self, caveats, per_line=1.2, lag=0.8)
        self.wait(2.2)
        self.play(FadeOut(VGroup(title, statement, caveats), run_time=0.8))


class S09ImpossibleHand(Scene):
    """ANIMATION IDEA — the impossible hand.

        "one shelf per orbit, as far as the eye can see, and on every shelf one
        book to designate.  A human hand hesitates, reaches, withdraws.  Then
        the HAND OF THE AXIOM OF CHOICE appears […] duplicated infinitely,
        touching every shelf at once.  Deliberately unreal."

    No spoken commentary.  It returns for one second at the very end of the
    film, over the chocolate.
    """

    def construct(self):
        theme.apply_defaults(self)

        # one shelf per orbit, receding
        shelves = VGroup()
        for row in range(6):
            t = row / 5
            width = 12.0 * (1 - 0.42 * t)
            y = 2.6 - row * 1.02
            bar = theme.rule(width=width, color=theme.GHOST, stroke=1.6)
            bar.move_to(np.array([0.0, y, 0.0]))
            bar.set_opacity(1.0 - 0.55 * t)
            books = VGroup()
            count = int(14 * (1 - 0.35 * t))
            for i in range(count):
                b = motifs.book(
                    "", height=0.55 * (1 - 0.32 * t), width=0.14, color=theme.INK_DIM, label=False
                )
                b.move_to(bar.get_left() + RIGHT * (width * (i + 0.5) / count)
                          + UP * 0.30 * (1 - 0.32 * t))
                b.set_opacity(0.55 - 0.30 * t)
                books.add(b)
            shelves.add(VGroup(bar, books))
        self.play(FadeIn(shelves, lag_ratio=0.12, run_time=1.6))
        self.wait(0.6)

        # the human hand hesitates
        hand = motifs.human_hand(scale=1.05)
        hand.move_to(np.array([-1.2, -3.0, 0.0]))
        self.play(FadeIn(hand, run_time=0.7))
        self.play(hand.animate(run_time=1.1, rate_func=theme.EASE).shift(UP * 1.9))
        self.play(hand.animate(run_time=0.5, rate_func=theme.EASE).shift(UP * 0.28))
        self.wait(0.5)
        self.play(hand.animate(run_time=1.3, rate_func=theme.EASE).shift(DOWN * 2.3))
        self.play(FadeOut(hand, run_time=0.5))
        self.wait(0.4)

        # the hand of the axiom of choice: everywhere at once
        ghosts = VGroup()
        for row, shelf in enumerate(shelves):
            t = row / 5
            for k in range(4):
                g = motifs.ChoiceHand(scale=0.42 * (1 - 0.28 * t))
                g.move_to(
                    shelf[0].get_left()
                    + RIGHT * (shelf[0].width * (k + 0.5) / 4)
                    + DOWN * 0.30
                )
                ghosts.add(g)
        self.play(
            LaggedStart(
                *[FadeIn(g, run_time=0.55) for g in ghosts],
                lag_ratio=0.02,
            )
        )
        self.wait(2.4)

        note = theme.caption("this hand does not exist.  that is exactly the point.", size=24)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note, run_time=0.8))
        self.wait(2.0)
        self.play(FadeOut(VGroup(shelves, ghosts, note), run_time=1.0))
