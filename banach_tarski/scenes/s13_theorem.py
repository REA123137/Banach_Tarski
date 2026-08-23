"""Scene 13 — 20:55-21:40 · The theorem.

    "ANIMATION – The chain builds left to right, one link at a time, each
    appearing as the voice names it."

    "ON SCREEN  L ∼ L₀ ∼ L₀ ∖ D = (P₁ ∪ P₂) ⊔ (P₃ ∪ P₄)"

    "ANIMATION – An exact replay of the opening shot, but each piece now
    carries its name, P₁ to P₄, and an arrow showing the rotation applied.  At
    the very end, back to the real foam balls in your hands.  The most
    satisfying moment of the video: let it run."

    "ANIMATION IDEA – The last panel drops.  The machine from scene 3 returns.
    The eighth panel falls and, for the first time, the complete mechanism runs
    in the open."
"""

from __future__ import annotations

# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from manim import (
    Arrow,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    RIGHT,
    Scene,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, motifs, space, theme
from banach_tarski.rotations import A, B
from banach_tarski.scenes.s01_trick import PIECE_COLORS, foam_ball

CHAIN = [
    ("L", "the ball", theme.INK),
    ("∼", "", theme.INK_DIM),
    ("L₀", "the ball minus its centre", theme.INK),
    ("∼", "", theme.INK_DIM),
    ("L₀ ∖ D", "…minus the poles", theme.INK),
    ("=", "", theme.INK_DIM),
    ("(P₁ ∪ P₂)  ⊔  (P₃ ∪ P₄)", "two complete copies", theme.GOLD),
]


class S13Chain(Scene):
    """Let us walk back up the chain — one link at a time."""

    def construct(self):
        theme.apply_defaults(self)

        links = VGroup()
        for text, _note, colour in CHAIN:
            links.add(theme.formula(text, size=40, color=colour))
        links.arrange(RIGHT, buff=0.42)
        if links.width > 13.0:
            links.scale_to_fit_width(13.0)
        links.move_to(UP * 0.55)

        # One caption at a time, in one place.  Three glosses stacked under a
        # seven-term chain would simply collide.
        caption_spot = links.get_bottom() + DOWN * 0.75
        current = None
        for link, (_text, note, _colour) in zip(links, CHAIN):
            gloss = theme.caption(note, size=24).move_to(caption_spot) if note else None
            anims = [FadeIn(link, shift=RIGHT * 0.18, run_time=0.55, rate_func=theme.EASE_OUT)]
            if current is not None:
                anims.append(FadeOut(current, run_time=0.35))
            if gloss is not None:
                anims.append(FadeIn(gloss, run_time=0.45))
            self.play(*anims)
            if gloss is not None:
                self.wait(0.45)
                current = gloss
            else:
                current = None
        self.wait(2.0)

        verdict = theme.display("the unit ball is equidecomposable with two copies of itself",
                                size=38, color=theme.GOLD)
        if verdict.width > 12.8:
            verdict.scale_to_fit_width(12.8)
        verdict.to_edge(DOWN, buff=0.9)
        self.play(Write(verdict, run_time=2.4))
        self.wait(1.0)

        name = theme.display("the Banach–Tarski paradox", size=34, color=theme.INK_DIM)
        name.next_to(verdict, DOWN, buff=0.35)
        self.play(FadeIn(name, run_time=0.9))
        self.wait(2.4)
        self.play(FadeOut(VGroup(links, verdict, name), run_time=0.9),
                  *( [FadeOut(current, run_time=0.9)] if current is not None else []))


class S13Replay(Scene):
    """The opening shot again — this time every piece is named, and labelled
    with the rotation it undergoes.  Let it run."""

    def construct(self):
        theme.apply_defaults(self)

        stage = space.Stage(space.View(yaw=-0.45, pitch=0.26, scale=1.35))
        pts = space.ball_points(24000, seed=4, shell=0.35)
        labels = space.pseudo_partition(pts, parts=4, seed=1)
        leftover = np.linalg.norm(pts, axis=1) > 0.985
        labels = np.where(leftover, 4, labels)

        ghost = space.wire_sphere(1.0, 12, 6, color=theme.GHOST, width=1.0)
        stage.add(*ghost)
        parts = []
        for i in range(5):
            cloud = space.Cloud(pts[labels == i], colors=PIECE_COLORS[i], size=2.4,
                                size_far=0.9, fog=0.85, bands=6)
            parts.append(cloud)
            stage.add(cloud)
        stage.install(self)
        self.wait(0.8)

        cam_x, cam_y, _ = stage.view.basis()
        offsets = [
            -1.75 * cam_x + 1.15 * cam_y,
            1.75 * cam_x + 1.15 * cam_y,
            -1.75 * cam_x - 1.15 * cam_y,
            1.75 * cam_x - 1.15 * cam_y,
            2.35 * cam_y,
        ]
        self.play(
            *[space.move_cloud(p, p.points + o, run_time=1.8) for p, o in zip(parts, offsets)]
        )

        # every piece now carries its name and the rotation applied to it
        names = ["P₁", "P₂", "P₃", "P₄", "the rest"]
        rotations = ["", "A", "", "B", ""]
        tags = VGroup()
        for i, (name, rot) in enumerate(zip(names, rotations)):
            centre = parts[i].points.mean(axis=0)
            screen, _ = stage.view.project_one(centre + 1.15 * cam_y)
            label = theme.body(name, size=30, color=PIECE_COLORS[i])
            if rot:
                arrow = Arrow(
                    LEFT * 0.28, RIGHT * 0.28, buff=0, color=PIECE_COLORS[i], stroke_width=3,
                    max_tip_length_to_length_ratio=0.4,
                )
                mark = theme.mono(rot, size=28, color=PIECE_COLORS[i])
                label = VGroup(label, arrow, mark).arrange(RIGHT, buff=0.14)
            label.move_to(screen)
            tags.add(label)
        self.play(FadeIn(tags, lag_ratio=0.15, run_time=1.2))
        self.wait(0.8)

        self.play(
            space.rotate_cloud(parts[1], A, run_time=2.2, about=parts[1].points.mean(axis=0)),
            space.rotate_cloud(parts[3], B, run_time=2.2, about=parts[3].points.mean(axis=0)),
        )
        self.wait(0.4)

        left_c = -2.15 * cam_x
        right_c = 2.15 * cam_x
        homes = {}
        for i, dest in enumerate([left_c, left_c, right_c, right_c, right_c]):
            homes[i] = space.ball_points(len(parts[i].points), seed=200 + i, shell=0.35) + dest
        self.play(
            FadeOut(tags, run_time=0.8),
            *[space.move_cloud(parts[i], homes[i], run_time=2.6, arc=0.10) for i in range(5)],
        )
        self.wait(0.8)

        count = theme.body("five pieces, as promised at the start", size=30, color=theme.GOLD)
        count.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(count, run_time=0.9))
        self.wait(1.2)

        stage.freeze()
        two = VGroup(foam_ball(1.35), foam_ball(1.35))
        two[0].move_to(stage.view.project_one(left_c)[0])
        two[1].move_to(stage.view.project_one(right_c)[0])
        self.play(
            *[space.fade_cloud(p, 0.0, run_time=1.8) for p in parts],
            FadeIn(two, run_time=1.8, rate_func=theme.EASE),
            *[w.mobject.animate(run_time=1.8).set_stroke(opacity=0.12) for w in ghost],
        )
        self.wait(2.6)
        self.play(FadeOut(VGroup(two, count), run_time=1.2))


class S13MachineOpens(Scene):
    """ANIMATION IDEA — the last panel drops, and the machine runs in the open.

        "The ball goes in, the four batches come out, rotate, reassemble.  Then
        the machine dissolves into your hands, holding the two foam balls."
    """

    def construct(self):
        theme.apply_defaults(self)

        machine = motifs.Machine()
        machine.shift(UP * 0.35)
        for i in range(7):
            machine.panels[i].shift(DOWN * 3.2).set_opacity(0.0)
            machine.labels[i].set_opacity(0.7)
        self.add(machine)
        self.wait(0.8)

        last = theme.caption("the eighth panel", size=24)
        last.next_to(machine, DOWN, buff=0.45)
        self.play(FadeIn(last, run_time=0.6))
        self.play(machine.drop(7, run_time=1.1))
        self.wait(0.5)

        ball_in = foam_ball(0.32)
        ball_in.move_to(machine.chute_in.get_start())
        self.play(FadeIn(ball_in, run_time=0.5))
        self.play(
            ball_in.animate(run_time=1.3, rate_func=theme.EASE).move_to(machine.body.get_left()),
        )
        self.play(FadeOut(ball_in, run_time=0.3), machine.run(turns=1.6, run_time=4.0))

        out_a = foam_ball(0.32).move_to(machine.chute_out_top.get_end())
        out_b = foam_ball(0.32).move_to(machine.chute_out_bottom.get_end())
        self.play(FadeIn(out_a, run_time=0.7), FadeIn(out_b, run_time=0.7))
        self.wait(1.0)

        # and the machine dissolves into a pair of hands
        hands = VGroup(motifs.human_hand(scale=1.25), motifs.human_hand(scale=1.25))
        hands.arrange(RIGHT, buff=1.6).shift(DOWN * 1.1)
        big_a = foam_ball(0.62).move_to(hands[0].get_top() + UP * 0.18)
        big_b = foam_ball(0.62).move_to(hands[1].get_top() + UP * 0.18)
        real = VGroup(hands, big_a, big_b)
        real.set_opacity(0.0)
        self.add(real)
        self.play(
            FadeOut(VGroup(machine, last, out_a, out_b), run_time=1.6),
            real.animate(run_time=1.6, rate_func=theme.EASE).set_opacity(1.0),
        )
        self.wait(2.4)
        self.play(FadeOut(real, run_time=1.2))
