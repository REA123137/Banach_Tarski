"""Scene 12 — 18:35-20:55 · The circle that closes up, and the poles.

Ranked fifth and sixth in the script's own production order, and described as
"the most carefully made animation in the video".

    "ANIMATION – From the gap, a ghost point departs and settles at one radian.
    Then another at two radians, another at three.  They light up one by one,
    endlessly, never overlapping."

    "ANIMATION – The key moment, played very slowly then looped three times.
    Every point of the queue steps back one place: the one at one radian fills
    the gap, the one at two radians takes the first one's place, and so on.
    The circle is whole.  No point vanished, none was created."

    "ANIMATION – A dartboard riddled with isolated pinpricks, the forbidden
    axes.  Throw a hundred darts at random: not one hits a prick."

    "ANIMATION IDEA – […] pull back, and discover that this circle was one of
    thousands, all drawn about the new axis, all punctured at the same instant,
    all closed by a single motion."

One radian is not a rational multiple of a turn, so the queue never repeats:
:func:`queue_angles` returns the genuine positions and the render relies on
them never colliding.
"""

from __future__ import annotations

# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from manim import (
    Arc,
    Circle,
    Create,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    LEFT,
    LaggedStart,
    RIGHT,
    Scene,
    UP,
    UpdateFromAlphaFunc,
    VGroup,
    Write,
)

from banach_tarski import anim, motifs, space, theme
from banach_tarski.rotations import fixed_point_axes, free_axis, rotation_about

QUEUE_LENGTH = 46
RADIUS = 2.35


def queue_angles(count: int = QUEUE_LENGTH) -> np.ndarray:
    """1, 2, 3, … radians.  Never a whole number of turns, so never a repeat."""
    return np.arange(1, count + 1, dtype=float)


def on_circle(angle, radius: float = RADIUS, centre=None) -> np.ndarray:
    centre = np.zeros(3) if centre is None else centre
    angle = np.atleast_1d(np.asarray(angle, dtype=float))
    pts = np.stack(
        [radius * np.cos(angle), radius * np.sin(angle), np.zeros_like(angle)], axis=1
    )
    return pts + centre


class S12Circle(Scene):
    """A circle with one point missing is equidecomposable with the whole circle."""

    def construct(self):
        theme.apply_defaults(self)

        centre = DOWN * 0.35
        gap_angle = 0.0
        eps = 0.055
        rim = Arc(
            radius=RADIUS,
            start_angle=gap_angle + eps,
            angle=2 * np.pi - 2 * eps,
            color=theme.INK,
            stroke_width=2.6,
        ).move_arc_center_to(centre)
        self.play(Create(rim, run_time=1.6))

        gap = Circle(radius=0.085, color=theme.REFUSE, stroke_width=2.4)
        gap.move_to(on_circle(gap_angle, centre=centre)[0])
        label = theme.body("p", size=30, color=theme.REFUSE)
        label.next_to(gap, RIGHT, buff=0.22)
        self.play(Create(gap, run_time=0.5), FadeIn(label, run_time=0.5))

        head = theme.body("it looks incomplete.  it is not.", size=30, color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.8))
        self.wait(1.0)

        statement = theme.body(
            "A circle with one point removed is equidecomposable with the whole circle.",
            size=30,
        )
        if statement.width > 12.6:
            statement.scale_to_fit_width(12.6)
        theme.foot(statement)
        self.play(Write(statement, run_time=2.0))
        self.wait(0.8)

        # -- the queue, one point at a time, faster and faster -------------
        angles = queue_angles()
        dots = VGroup()
        for i, a in enumerate(angles):
            colour = theme.GOLD if i == 0 else theme.C_B
            d = Dot(on_circle(a, centre=centre)[0], radius=0.062 if i == 0 else 0.055,
                    color=colour)
            dots.add(d)
        self.play(
            LaggedStart(
                *[
                    FadeIn(d, run_time=max(0.30 * (0.86**i), 0.03))
                    for i, d in enumerate(dots)
                ],
                lag_ratio=0.55,
            )
        )
        formula = theme.formula(r"X \;=\; \{\, p \text{ rotated by } 1, 2, 3, \dots \text{ radians} \,\}", size=32,
                                color=theme.C_B)
        formula.move_to(statement)
        self.play(FadeOut(statement, run_time=0.4), FadeIn(formula, run_time=0.6))
        self.wait(0.8)

        counter = theme.formula(rf"{len(dots)} \dots", size=30, color=theme.INK_DIM)
        tail = theme.caption("the queue never ends", size=22)
        meter = VGroup(counter, tail).arrange(DOWN, buff=0.14)
        theme.stage_corner(meter, x_sign=1.0, y_sign=1.0)
        self.play(FadeIn(meter, run_time=0.6))

        # -- the key moment: every point steps back one place --------------
        self.play(FadeOut(head, run_time=0.4))
        move = theme.body("rotate the queue by one radian backwards", size=30, color=theme.C_B)
        theme.head(move)
        self.play(FadeIn(move, run_time=0.7))

        for take, run_time in ((0, 5.5), (1, 2.4), (2, 1.6)):
            self._step_back(dots, angles, centre, gap, run_time=run_time, first=take == 0)
            if take < 2:
                self._reset(dots, angles, centre, gap)

        whole = theme.body("the circle is whole.  no point vanished, none was created.",
                           size=30, color=theme.GOLD)
        whole.move_to(formula)
        self.play(FadeOut(formula, run_time=0.4), Write(whole, run_time=1.6))
        self.wait(2.2)
        self.play(FadeOut(VGroup(rim, dots, gap, label, move, whole, meter), run_time=0.9))

    # ---------------------------------------------------------------- helpers
    def _step_back(self, dots, angles, centre, gap, run_time: float, first: bool):
        """Every point steps back one place — along the rim, never across it.

        A straight interpolation between two positions on a circle cuts the
        chord and the queue visibly collapses inwards, which is precisely the
        thing the shot must not suggest.  So the angle is what moves.
        """

        def travel(_m, alpha):
            for dot, a in zip(dots, angles):
                dot.move_to(on_circle(a - alpha, centre=centre)[0])

        self.play(
            UpdateFromAlphaFunc(dots, travel, run_time=run_time, rate_func=theme.EASE),
            gap.animate(run_time=run_time * 0.45).set_stroke(opacity=0.0),
        )

    def _reset(self, dots, angles, centre, gap):
        for d, a in zip(dots, angles):
            d.move_to(on_circle(a, centre=centre)[0])
        gap.set_stroke(opacity=1.0)


class S12Dartboard(Scene):
    """Why a new axis can always be found: the forbidden ones cannot be hit."""

    def construct(self):
        theme.apply_defaults(self)

        board = motifs.dartboard(radius=2.7, rings=5)
        board.shift(DOWN * 0.25)
        self.play(FadeIn(board, run_time=0.9))

        head = theme.body("the forbidden axes can be put in a list", size=30,
                          color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.7))

        rng = np.random.default_rng(21)
        pricks = VGroup()
        for _ in range(70):
            r = 2.7 * np.sqrt(rng.random())
            a = rng.random() * 2 * np.pi
            pricks.add(
                Dot(board.get_center() + np.array([r * np.cos(a), r * np.sin(a), 0]),
                    radius=0.022, color=theme.REFUSE)
            )
        self.play(FadeIn(pricks, lag_ratio=0.02, run_time=1.2))
        self.wait(0.6)

        head2 = theme.body("the axes of space cannot.  there are strictly more of them.",
                           size=30, color=theme.INK_DIM)
        head2.move_to(head)
        self.play(FadeOut(head, run_time=0.35), FadeIn(head2, run_time=0.5))

        darts = VGroup()
        hits = 0
        prick_points = np.array([p.get_center() for p in pricks])
        for i in range(100):
            r = 2.7 * np.sqrt(rng.random())
            a = rng.random() * 2 * np.pi
            point = board.get_center() + np.array([r * np.cos(a), r * np.sin(a), 0])
            if np.min(np.linalg.norm(prick_points - point, axis=1)) < 0.03:
                hits += 1
            darts.add(Dot(point, radius=0.038, color=theme.C_B))
        self.play(
            LaggedStart(*[FadeIn(d, scale=2.2, run_time=0.16) for d in darts], lag_ratio=0.06)
        )

        verdict = theme.body(f"a hundred darts.  {hits} hits.", size=34, color=theme.GOLD)
        theme.foot(verdict)
        self.play(Write(verdict, run_time=1.2))
        self.wait(2.0)
        self.play(FadeOut(VGroup(board, pricks, darts, head2, verdict), run_time=0.8))


class S12Poles(Scene):
    """ANIMATION IDEA — one gesture becomes a global gesture.

    The circle theorem is applied to every circle about a new axis at once:
    thousands of punctured circles, closed by a single motion.
    """

    def construct(self):
        theme.apply_defaults(self)

        axis = free_axis()
        stage = space.Stage(space.View(yaw=-0.55, pitch=0.22, scale=2.3))
        stage.view.origin = np.array([0.0, -0.30, 0.0])
        for wire in space.wire_sphere(1.0, 10, 5, color="#141414", width=1.0):
            stage.add(wire)
        axis_line = space.Wire(space.axis_segment(axis, 1.12), color=theme.GOLD, width=1.8,
                               closed=False)
        axis_line.mobject.set_stroke(opacity=0.6)
        stage.add(axis_line)

        # one circle first, with its missing pole
        heights = np.linspace(-0.92, 0.92, 37)
        circles = []
        for h in heights:
            ring = space.Wire(
                space.circle_on_axis(axis, float(h), 1.0, 140), color="#2C2C2C", width=1.2
            )
            circles.append(ring)
        stage.add(*circles)

        # the punctures: one missing point per circle, and the queue that fills it
        rot = rotation_about(axis, 1.0)
        gaps = []
        queues = []
        for h in heights:
            base = space.circle_on_axis(axis, float(h), 1.0, 1)[0]
            gaps.append(space.Marker(base, color=theme.REFUSE, radius=0.042))
            pts = [base]
            for _ in range(26):
                pts.append(rot @ pts[-1])
            queues.append(np.array(pts[1:]))
        stage.add(*gaps)

        queue_cloud = space.Cloud(
            np.vstack(queues), colors=theme.C_B, size=2.4, size_far=0.9, fog=0.7, bands=5
        )
        stage.add(queue_cloud)
        stage.install(self)
        stage.fit(spread=1.12)

        head = theme.body("a new axis, avoiding every forbidden one", size=30,
                          color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.8))
        self.wait(1.2)

        head2 = theme.body(
            "every circle about it is the case we have just handled", size=30,
            color=theme.INK_DIM
        )
        head2.move_to(head)
        self.play(FadeOut(head, run_time=0.35), FadeIn(head2, run_time=0.5))
        self.play(stage.orbit(d_yaw=0.9, run_time=3.5))

        # one gesture, everywhere at once
        move = theme.body("one motion — all of them close", size=32, color=theme.GOLD)
        theme.foot(move)
        self.play(FadeIn(move, run_time=0.7))
        self.play(
            space.rotate_cloud(queue_cloud, rot.T, run_time=4.0),
            *[g.mobject.animate(run_time=4.0).set_opacity(0.0) for g in gaps],
        )
        self.wait(0.6)

        results = VGroup(
            theme.body("The sphere with its poles removed is equidecomposable with the whole sphere.",
                       size=28),
            theme.body("The ball without its centre is equidecomposable with the whole ball.",
                       size=28),
        ).arrange(DOWN, buff=0.28)
        if results.width > 12.8:
            results.scale_to_fit_width(12.8)
        theme.foot(results)
        self.play(FadeOut(move, run_time=0.4))
        anim.write_lines(self, results, per_line=1.6, lag=0.8)
        self.wait(2.2)
        self.play(FadeOut(VGroup(head2, results), run_time=0.9))


class S12Centre(Scene):
    """And the centre of the ball?  Exactly the same, on a circle through it."""

    def construct(self):
        theme.apply_defaults(self)

        stage = space.Stage(space.View(yaw=-0.6, pitch=0.26, scale=2.3))
        stage.view.origin = np.array([0.0, -0.20, 0.0])
        ball = space.ball_cloud(15000, color="#38363231"[:7], seed=9)
        ball.colors[:] = space.rgb_of("#3A3833")
        stage.add(ball)
        for wire in space.wire_sphere(1.0, 10, 5, color="#161616", width=1.0):
            stage.add(wire)

        # a circle inside the ball, passing through the centre
        offset = np.array([0.0, 0.0, 0.45])
        ring_pts = space.great_circle([0.35, 0.9, 0.25], radius=0.45) + offset * 0.0
        ring_pts = ring_pts + np.array([0.0, 0.0, 0.0])
        # shift the circle so that it passes through the origin
        ring_pts = ring_pts - ring_pts[0]
        ring = space.Wire(ring_pts, color=theme.C_B, width=2.2)
        stage.add(ring)
        origin_mark = space.Marker(np.zeros(3), color=theme.REFUSE, radius=0.06, halo=3.0)
        stage.add(origin_mark)
        stage.install(self)
        stage.spin(self, speed=0.12)

        head = theme.body("draw a circle inside the ball, through the centre", size=30,
                          color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.8))
        self.wait(1.4)

        # the queue on that circle steps back one place, and the centre returns
        rot_axis = np.cross(ring_pts[1] - ring_pts[0], ring_pts[2] - ring_pts[0])
        centre_of_ring = ring_pts.mean(axis=0)
        rot = rotation_about(rot_axis, 1.0)
        pts = [np.zeros(3)]
        for _ in range(30):
            pts.append(rot @ (pts[-1] - centre_of_ring) + centre_of_ring)
        queue = space.Cloud(np.array(pts[1:]), colors=theme.C_B, size=2.6, size_far=1.0,
                            fog=0.7, bands=4)
        stage.add(queue)
        self.wait(0.8)

        self.play(
            space.rotate_cloud(queue, rot.T, run_time=3.5, about=centre_of_ring),
            origin_mark.mobject.animate(run_time=3.5).set_opacity(0.0),
        )
        verdict = theme.formula(r"L \;\sim\; L_0", size=44, color=theme.GOLD)
        theme.foot(verdict)
        self.play(Write(verdict, run_time=1.2))
        self.wait(2.2)
        self.play(FadeOut(VGroup(head, verdict), run_time=0.8))
