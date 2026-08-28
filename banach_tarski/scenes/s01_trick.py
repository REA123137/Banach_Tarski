"""Scene 1 — 00:00-01:15 · The trick.

    "LIVE ACTION THEN ANIMATION – Slow-motion replay of Iasmina's hands.  As
    they close, the image dissolves from the real foam ball into a cloud of
    points.  The cloud splits into five numbered groups, each rotates, and two
    clouds re-form."

The live plates are shot separately; what is coded here is everything that
happens between them, plus the two ideas the script attaches to the shot —
the ghost wireframe, and the squeeze that plants the prohibition.
"""

from __future__ import annotations

import numpy as np
# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from manim import (
    Circle,
    ManimColor,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    RIGHT,
    Scene,
    UP,
    VGroup,
    Write,
    interpolate_color,
)

from banach_tarski import anim, motifs, space, theme
from banach_tarski.rotations import A, B

# The five groups of the opening shot: four batches plus the leftovers.
PIECE_COLORS = [theme.C_A, theme.C_AI, theme.C_B, theme.C_BI, theme.C_E]
PIECE_NAMES = ["1", "2", "3", "4", "5"]

N_POINTS = 26000


def foam_ball(radius: float = 1.0, base: str = "#4A443C", light: str = "#FBF7EF") -> VGroup:
    """The real object: a plain foam stress ball, before anything mathematical.

    Shaded by stacking concentric discs offset towards the key light — manim
    has no gradients that survive on black, and twenty flat circles read as a
    sphere perfectly well at 60 fps.
    """
    layers = 22
    ball = VGroup()
    for i in range(layers):
        t = i / (layers - 1)
        disc = Circle(
            radius=radius * (1.0 - 0.72 * t),
            stroke_width=0,
            fill_color=interpolate_color(ManimColor(base), ManimColor(light), t**0.85),
            fill_opacity=1.0,
        )
        disc.shift(np.array([-0.20, 0.24, 0.0]) * radius * t)
        ball.add(disc)
    spec = Circle(radius=radius * 0.13, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.55)
    spec.shift(np.array([-0.34, 0.40, 0.0]) * radius)
    ball.add(spec)
    return ball


class S01Trick(Scene):
    """The opening shot, and the payoff of the whole film.

    Real ball → cloud → five pieces → rigid motions → two clouds → two balls.
    Nothing is stretched, nothing is copied: every motion played here is an
    actual rotation matrix out of :mod:`banach_tarski.rotations`.
    """

    def construct(self):
        theme.apply_defaults(self)

        # -- 1. the real object ------------------------------------------
        ball = foam_ball(1.35)
        self.play(FadeIn(ball, scale=1.06, run_time=1.2, rate_func=theme.EASE_OUT))
        self.wait(0.6)

        # -- 2. the dissolve into a cloud of points ----------------------
        stage = space.Stage(space.View(yaw=-0.5, pitch=0.28, scale=1.35))
        pts = space.ball_points(N_POINTS, seed=4, shell=0.35)
        cloud = space.Cloud(pts, colors="#EDE6DA", size=2.4, size_far=0.9, fog=0.85, bands=7)
        cloud.opacity = 0.0
        ghost = space.wire_sphere(1.0, 12, 6, color=theme.GHOST, width=1.0)
        for w in ghost:
            w.mobject.set_stroke(opacity=0.0)
        stage.add(cloud, *ghost)
        # the five pieces fly apart later; leave room for them now
        stage.install(self, margin=0.18)
        stage.fit(spread=2.25)
        # No permanent drift here: the two balls must not swap sides while
        # they re-form.  The camera moves only where it is asked to.

        self.play(
            space.fade_cloud(cloud, 1.0, run_time=1.6),
            ball.animate(run_time=1.6, rate_func=theme.EASE).set_opacity(0.0),
        )
        self.remove(ball)
        self.play(stage.orbit(d_yaw=0.55, run_time=2.4))

        # -- 3. the ghost: where the original ball stood -----------------
        self.play(
            *[w.mobject.animate(run_time=1.0).set_stroke(opacity=0.5) for w in ghost],
        )

        # -- 4. five numbered groups -------------------------------------
        labels = space.pseudo_partition(pts, parts=4, seed=1)
        # the fifth group: a thin shell of leftovers, the queue X and the axes
        leftover = np.linalg.norm(pts, axis=1) > 0.985
        labels = np.where(leftover, 4, labels)
        target_colors = space.colors_from_labels(labels, PIECE_COLORS)
        self.play(space.recolor_cloud(cloud, target_colors, run_time=1.8))
        self.wait(0.3)

        tags = VGroup()
        for i, name in enumerate(PIECE_NAMES):
            t = theme.formula(name, size=34, color=PIECE_COLORS[i])
            tags.add(t)
        theme.foot(tags.arrange(RIGHT, buff=0.62))
        self.play(FadeIn(tags, shift=UP * 0.2, run_time=0.8))

        # -- 5. the pieces come apart ------------------------------------
        stage.remove(cloud)
        parts = []
        for i in range(5):
            mask = labels == i
            c = space.Cloud(
                pts[mask], colors=PIECE_COLORS[i], size=2.4, size_far=0.9, fog=0.85, bands=6
            )
            parts.append(c)
            stage.add(c)
        # The pieces must fly apart *on screen*, so the offsets are written in
        # the camera's own basis rather than in world coordinates.
        cam_x, cam_y, cam_z = stage.view.basis()
        offsets = [
            -1.75 * cam_x + 1.15 * cam_y,
            1.75 * cam_x + 1.15 * cam_y,
            -1.75 * cam_x - 1.15 * cam_y,
            1.75 * cam_x - 1.15 * cam_y,
            2.35 * cam_y,
        ]
        self.play(
            *[
                space.move_cloud(p, p.points + o, run_time=1.8)
                for p, o in zip(parts, offsets)
            ],
        )
        self.wait(0.4)

        # -- 6. each piece is moved: a genuine rotation ------------------
        self.play(
            space.rotate_cloud(parts[1], A, run_time=2.0, about=parts[1].points.mean(axis=0)),
            space.rotate_cloud(parts[3], B, run_time=2.0, about=parts[3].points.mean(axis=0)),
            space.rotate_cloud(parts[0], A.T, run_time=2.0, about=parts[0].points.mean(axis=0)),
            space.rotate_cloud(parts[2], B.T, run_time=2.0, about=parts[2].points.mean(axis=0)),
        )
        self.wait(0.3)

        # -- 7. two balls re-form ----------------------------------------
        left_c = -2.15 * cam_x
        right_c = 2.15 * cam_x
        homes = {}
        for i, dest in enumerate([left_c, left_c, right_c, right_c, right_c]):
            n = len(parts[i].points)
            homes[i] = space.ball_points(n, seed=100 + i, shell=0.35) + dest
        self.play(
            *[space.move_cloud(parts[i], homes[i], run_time=2.4, arc=0.10) for i in range(5)],
        )
        self.wait(0.5)

        # -- 8. back to two real objects ---------------------------------
        self.play(FadeOut(tags, run_time=0.6))
        stage.freeze()
        two = VGroup(foam_ball(1.35), foam_ball(1.35))
        s_left, _ = stage.view.project_one(left_c)
        s_right, _ = stage.view.project_one(right_c)
        two[0].move_to(s_left)
        two[1].move_to(s_right)
        self.play(
            *[space.fade_cloud(p, 0.0, run_time=1.5) for p in parts],
            FadeIn(two, run_time=1.5, rate_func=theme.EASE),
            *[w.mobject.animate(run_time=1.5).set_stroke(opacity=0.14) for w in ghost],
        )
        self.wait(1.6)


class S01Squeeze(Scene):
    """ANIMATION IDEA — the squeeze that plants the prohibition.

        "The squeeze at the start is not decoration: it plants, visually, the
        prohibition that governs everything else.  You show what is not
        allowed ten seconds before saying it is not allowed."

    The ball is crushed between two plates; the deformation is held, then
    refused.  Ten seconds, no words.
    """

    def construct(self):
        theme.apply_defaults(self)
        ball = foam_ball(1.5)
        self.play(FadeIn(ball, run_time=0.9))
        self.wait(0.4)

        plate_top = theme.rule(width=4.0, color=theme.INK_DIM, stroke=3).next_to(ball, UP, buff=0.35)
        plate_bot = theme.rule(width=4.0, color=theme.INK_DIM, stroke=3).next_to(ball, DOWN, buff=0.35)
        self.play(Create(plate_top, run_time=0.5), Create(plate_bot, run_time=0.5))

        self.play(
            ball.animate(run_time=1.1, rate_func=theme.EASE).stretch(0.55, 1).stretch(1.34, 0),
            plate_top.animate(run_time=1.1, rate_func=theme.EASE).shift(DOWN * 0.42),
            plate_bot.animate(run_time=1.1, rate_func=theme.EASE).shift(UP * 0.42),
        )
        self.wait(0.7)

        bar = anim.strike(ball, width=6.0)
        self.play(Create(bar, run_time=0.5, rate_func=theme.SNAP))
        caption = theme.body("no stretching", size=32, color=theme.REFUSE)
        caption.next_to(plate_bot, DOWN, buff=0.7)
        self.play(FadeIn(caption, shift=UP * 0.15, run_time=0.6))
        self.wait(1.4)

        self.play(
            FadeOut(VGroup(bar, caption, plate_top, plate_bot), run_time=0.6),
            ball.animate(run_time=0.9, rate_func=theme.EASE).stretch(1 / 0.55, 1).stretch(1 / 1.34, 0),
        )
        self.wait(0.8)


class S01GhostReplay(Scene):
    """ANIMATION IDEA — keep a ghost wireframe where the original ball stood.

        "the second ball is then visibly new."

    Played on its own so the point cannot be missed: one ball leaves the
    wireframe, the wireframe stays empty, and a second ball appears beside it.
    """

    def construct(self):
        theme.apply_defaults(self)
        stage = space.Stage(space.View(yaw=-0.4, pitch=0.26, scale=1.5))
        ghost = space.wire_sphere(1.0, 14, 7, color=theme.GHOST, width=1.1)
        stage.add(*ghost)
        cloud = space.ball_cloud(16000, color=theme.C_E, seed=6)
        stage.add(cloud)
        stage.install(self)
        stage.spin(self, speed=0.14)
        self.wait(1.0)

        tag = theme.caption("the ball that was here", size=24)
        theme.foot(tag)
        self.play(FadeIn(tag, run_time=0.6))

        left = space.ball_points(len(cloud.points), seed=21, shell=0.35) - np.array([1.5, 0, 0])
        self.play(space.move_cloud(cloud, left, run_time=2.0))

        second = space.Cloud(
            space.ball_points(len(cloud.points), seed=22, shell=0.35) + np.array([1.5, 0, 0]),
            colors=theme.GOLD,
            size=2.4,
            size_far=0.9,
            fog=0.85,
            bands=7,
        )
        second.opacity = 0.0
        stage.add(second)
        new_tag = theme.body("new", size=30, color=theme.GOLD)
        s, _ = stage.view.project_one(np.array([1.5, 0, 1.35]))
        new_tag.move_to(s)
        self.play(
            space.fade_cloud(second, 1.0, run_time=1.6),
            FadeIn(new_tag, run_time=1.2),
        )
        self.wait(2.0)


class S01HandOff(Scene):
    """ANIMATION IDEA — the hand-off through the lens, the spine of the film.

        "Shoot it twice, in the same light: once with the balls, once with the
        chocolate, so the last shot rhymes with the first."

    This is the animated match-frame: the same gesture, the same easing, the
    same hold, so that the two live plates can be cut against it.
    """

    def construct(self):
        theme.apply_defaults(self)
        hand = motifs.human_hand(scale=1.5)
        hand.shift(DOWN * 1.5)
        ball_l = foam_ball(0.5).move_to(hand.get_top() + LEFT * 0.55 + UP * 0.1)
        ball_r = foam_ball(0.5).move_to(hand.get_top() + RIGHT * 0.55 + UP * 0.1)
        group = VGroup(hand, ball_l, ball_r)
        self.play(FadeIn(group, run_time=1.0))
        self.wait(0.5)

        note = theme.caption("hold — this gesture returns at 24:30, with a square of chocolate", size=22)
        theme.foot(note)
        self.play(FadeIn(note, run_time=0.6))

        # offered through the lens: scale up and past the camera
        self.play(
            group.animate(run_time=2.2, rate_func=theme.EASE_OUT).scale(2.1).shift(UP * 0.9).set_opacity(0.0),
        )
        self.wait(1.0)
        self.play(FadeOut(note, run_time=0.5))
