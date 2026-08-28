"""Scene 3 — 02:00-03:15 · Translating the statement: "doubleable".

    "ON SCREEN  L = U ⊔ V, U ∼ L, V ∼ L" and "A ∩ B = ∅"

    "ANIMATION – Two overlapping set blobs, the shared region hatched in red:
    rejected.  Then the blobs pull apart, the red vanishes: accepted.  A single
    point wanders and always lights up in one blob only."

    "ANIMATION IDEA, THE RECURRING MOTIF OF THE WHOLE VIDEO – The machine with
    panels."
"""

from __future__ import annotations

# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from manim import (
    Circle,
    Create,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    Intersection,
    LEFT,
    Line,
    MoveAlongPath,
    RIGHT,
    Scene,
    UP,
    VGroup,
    VMobject,
    Write,
)

from banach_tarski import anim, motifs, theme


def blob(seed: int, radius: float = 1.55, wobble: float = 0.16, color: str = theme.C_B) -> VMobject:
    """A set, drawn as a soft closed curve.  Sets are not circles."""
    rng = np.random.default_rng(seed)
    n = 9
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    radii = radius * (1.0 + wobble * rng.normal(size=n) * 0.6)
    pts = [
        np.array([np.cos(a) * r, np.sin(a) * r * 0.86, 0.0]) for a, r in zip(angles, radii)
    ]
    curve = VMobject(stroke_color=color, stroke_width=2.4)
    curve.set_points_smoothly(pts + [pts[0]])
    curve.set_fill(color, opacity=0.10)
    return curve


def hatching(region: VMobject, spacing: float = 0.17, color: str = theme.REFUSE) -> VGroup:
    """Red hatching, clipped to the shared region — the only thing ever red.

    The strokes are thin rectangles rather than segments: manim can only
    intersect closed paths, and an unclipped hatch would spill far outside the
    overlap and say the opposite of what the shot means.
    """
    from manim import Intersection as _Intersection, Rectangle

    left, right = region.get_left()[0], region.get_right()[0]
    bottom, top = region.get_bottom()[1], region.get_top()[1]
    diag = float(np.hypot(right - left, top - bottom)) + 0.4
    centre = region.get_center()
    marks = VGroup()
    offset = -diag / 2
    while offset < diag / 2:
        bar = Rectangle(width=0.028, height=diag, stroke_width=0)
        bar.set_fill(color, opacity=1.0)
        bar.move_to(centre + np.array([offset, 0.0, 0.0]))
        bar.rotate(np.pi / 4, about_point=centre)
        try:
            piece = _Intersection(bar, region)
        except Exception:
            offset += spacing
            continue
        if piece.has_points():
            piece.set_fill(color, opacity=0.9).set_stroke(width=0)
            marks.add(piece)
        offset += spacing
    return marks


class S03Disjoint(Scene):
    """Disjoint, made visible: overlap refused, separation accepted."""

    def construct(self):
        theme.apply_defaults(self)

        formula = theme.formula(r"A \cap B = \emptyset", size=58)
        theme.head(formula)
        gloss = theme.body(
            "no element is in both", size=30, color=theme.INK_DIM
        )
        theme.stage(VGroup(formula, gloss).arrange(DOWN, buff=0.35))
        self.play(Write(formula, run_time=1.1), FadeIn(gloss, run_time=0.9))

        a = blob(1, color=theme.C_B).shift(LEFT * 0.85 + DOWN * 0.6)
        b = blob(2, color=theme.C_BI).shift(RIGHT * 0.85 + DOWN * 0.6)
        label_a = theme.body("A", size=32, color=theme.C_B).next_to(a, LEFT, buff=0.2)
        label_b = theme.body("B", size=32, color=theme.C_BI).next_to(b, RIGHT, buff=0.2)
        self.play(Create(a, run_time=0.9), Create(b, run_time=0.9),
                  FadeIn(label_a, run_time=0.6), FadeIn(label_b, run_time=0.6))

        # -- rejected -----------------------------------------------------
        overlap = Intersection(a, b, color=theme.REFUSE, stroke_width=2.0)
        marks = hatching(overlap)
        self.play(Create(overlap, run_time=0.6), FadeIn(marks, run_time=0.6))
        verdict = theme.body("rejected", size=30, color=theme.REFUSE)
        theme.foot(verdict)
        self.play(FadeIn(verdict, shift=UP * 0.12, run_time=0.5))
        self.wait(1.0)

        # -- accepted -----------------------------------------------------
        ok = theme.body("accepted", size=30, color=theme.C_B).move_to(verdict)
        self.play(
            a.animate(run_time=1.3, rate_func=theme.EASE).shift(LEFT * 1.15),
            b.animate(run_time=1.3, rate_func=theme.EASE).shift(RIGHT * 1.15),
            label_a.animate(run_time=1.3, rate_func=theme.EASE).shift(LEFT * 1.15),
            label_b.animate(run_time=1.3, rate_func=theme.EASE).shift(RIGHT * 1.15),
            FadeOut(overlap, run_time=0.6),
            FadeOut(marks, run_time=0.6),
            FadeOut(verdict, run_time=0.4),
        )
        self.play(FadeIn(ok, run_time=0.5))
        self.wait(0.6)

        # -- a single point, always in exactly one blob -------------------
        point = Dot(radius=0.09, color=theme.INK)
        path = VMobject()
        way = [
            a.get_center() + np.array([-0.4, 0.3, 0]),
            a.get_center() + np.array([0.5, -0.35, 0]),
            (a.get_center() + b.get_center()) / 2 + np.array([0, 0.9, 0]),
            b.get_center() + np.array([-0.4, -0.2, 0]),
            b.get_center() + np.array([0.55, 0.35, 0]),
        ]
        path.set_points_smoothly(way)
        self.play(FadeIn(point, run_time=0.4))

        for target, host, colour in (
            (way[1], a, theme.C_B),
            (way[3], b, theme.C_BI),
        ):
            sub = VMobject()
            sub.set_points_smoothly([point.get_center(), (point.get_center() + target) / 2
                                     + np.array([0, 0.7, 0]), target])
            self.play(MoveAlongPath(point, sub, run_time=1.5, rate_func=theme.EASE))
            self.play(
                host.animate(run_time=0.35).set_fill(opacity=0.28),
                point.animate(run_time=0.35).set_color(colour),
            )
            self.play(host.animate(run_time=0.35).set_fill(opacity=0.10))

        self.wait(1.2)
        self.play(FadeOut(VGroup(a, b, label_a, label_b, point, ok, formula, gloss), run_time=0.8))


class S03Doubleable(Scene):
    """The goal of the whole film, written once, in full."""

    def construct(self):
        theme.apply_defaults(self)

        head = theme.body("Proving the theorem means proving one thing only:", size=32,
                          color=theme.INK_DIM)
        claim = theme.display("the unit ball is doubleable", size=52, color=theme.GOLD)
        block = theme.head(VGroup(head, claim).arrange(DOWN, buff=0.45))
        self.play(FadeIn(head, run_time=0.8), Write(claim, run_time=1.4))
        self.wait(0.8)

        line = theme.formula(r"L \;=\; U \sqcup V \qquad U \sim L \qquad V \sim L", size=46)
        gloss = VGroup(
            theme.body("a union of disjoint sets…", size=28, color=theme.INK_DIM),
            theme.body("…each equidecomposable with the whole ball", size=28, color=theme.INK_DIM),
        ).arrange(DOWN, buff=0.28)
        body_block = theme.stage(VGroup(line, gloss).arrange(DOWN, buff=0.65))

        self.play(Write(line, run_time=1.6))
        anim.write_lines(self, gloss, per_line=1.0, lag=0.7)
        self.wait(0.8)

        promise = theme.caption("both words are explained before minute nine", size=24)
        theme.foot(promise)
        self.play(FadeIn(promise, run_time=0.6))
        self.wait(1.8)
        self.play(FadeOut(VGroup(block, body_block, promise), run_time=0.8))


class S03Machine(Scene):
    """ANIMATION IDEA — the recurring motif: the machine with eight panels.

        "The theorem is drawn as a machine: one ball in on the left, two out on
        the right.  Its mechanism is hidden behind eight numbered panels.  At
        the end of every scene one panel drops and reveals a cog. […]  The
        viewer watches their own understanding being built physically."

    Rendered here as the introduction plus the first drop.  Every later scene
    re-imports :class:`banach_tarski.motifs.Machine` and calls ``drop(n)``.
    """

    def construct(self):
        theme.apply_defaults(self)
        machine = motifs.Machine()
        machine.shift(DOWN * 0.25)
        self.play(Create(machine.body, run_time=1.2))
        self.play(
            Create(machine.chute_in, run_time=0.5),
            Create(machine.chute_out_top, run_time=0.5),
            Create(machine.chute_out_bottom, run_time=0.5),
        )
        self.play(FadeIn(machine.panels, lag_ratio=0.12, run_time=1.4))
        self.add(machine)

        ball_in = Circle(radius=0.30, fill_color="#EDE6DA", fill_opacity=1.0, stroke_width=0)
        ball_in.move_to(machine.chute_in.get_start())
        out_a = ball_in.copy().move_to(machine.chute_out_top.get_end())
        out_b = ball_in.copy().move_to(machine.chute_out_bottom.get_end())
        self.play(FadeIn(ball_in, run_time=0.5))
        self.play(ball_in.animate(run_time=1.1, rate_func=theme.EASE).move_to(machine.body.get_left()))
        self.play(FadeOut(ball_in, run_time=0.35))
        self.play(FadeIn(out_a, run_time=0.6), FadeIn(out_b, run_time=0.6))
        self.wait(0.8)

        note = theme.caption("one panel drops at the end of every scene", size=24)
        theme.foot(note)
        self.play(FadeIn(note, run_time=0.6))
        self.play(machine.drop(0))
        self.wait(1.6)
        self.play(FadeOut(VGroup(note), run_time=0.5),
                  FadeOut(out_a, run_time=0.5), FadeOut(out_b, run_time=0.5))


class S03MachineFull(Scene):
    """The same machine, fully open, running.  Used again in scene 13."""

    def construct(self):
        theme.apply_defaults(self)
        machine = motifs.Machine()
        self.add(machine)
        self.wait(0.4)
        for i in range(8):
            self.play(machine.drop(i, run_time=0.45))
        self.wait(0.4)
        self.play(machine.run(turns=1.5, run_time=4.0))
        self.wait(1.0)
