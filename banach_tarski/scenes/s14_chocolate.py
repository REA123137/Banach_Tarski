"""Scene 14 — 21:40-24:55 · Chocolate, volume, and non-measurable sets.

    "ANIMATION – The squares number themselves one by one up to twenty-four.
    Then a twenty-fifth square appears, alone, to the side."

    "ANIMATION – Before and after superimposed, then a tenfold magnification at
    the edge.  The offset becomes visible."

    "ANIMATION – Endless continuous zoom into P₁.  At every scale, the same
    riddled texture.  Never an edge, never a stable structure."

    "ANIMATION IDEA – The scale that never settles. […] Leave the needle
    swinging under the closing exchange, and let it still be swinging when the
    picture cuts to black.  It is the last thing the viewer sees move."
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
    FadeIn,
    FadeOut,
    Group,
    LEFT,
    LaggedStart,
    Line,
    Polygon,
    RIGHT,
    Rectangle,
    Scene,
    UP,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    Write,
)
from manim.mobject.types.point_cloud_mobject import PMobject

from banach_tarski import anim, motifs, space, theme

CELL = 0.84
COLS, ROWS = 6, 4
SHRINK = float(np.sqrt(23.0 / 24.0))  # the rebuilt bar is one square short, exactly


class S14Chocolate(Scene):
    """Twenty-four squares.  And one left over."""

    def construct(self):
        theme.apply_defaults(self)

        bar = motifs.chocolate_bar(COLS, ROWS, CELL)
        bar.move_to(UP * 0.35)
        self.play(FadeIn(bar, lag_ratio=0.02, run_time=1.2))
        self.wait(0.5)

        w, h = COLS * CELL, ROWS * CELL
        origin = bar.get_center() + np.array([-w / 2, -h / 2, 0.0])

        def at(x, y):
            return origin + np.array([x * CELL, y * CELL, 0.0])

        # the cuts: two straight, one diagonal
        cuts = VGroup(
            Line(at(1, 0), at(1, 4), color=theme.INK, stroke_width=2.4),
            Line(at(1, 1), at(6, 1), color=theme.INK, stroke_width=2.4),
            Line(at(1, 1), at(6, 4), color=theme.INK, stroke_width=2.4),
        )
        self.play(LaggedStart(*[Create(c, run_time=0.7) for c in cuts], lag_ratio=0.4))
        self.wait(0.4)

        # the four pieces
        def piece(points, colour):
            poly = Polygon(*[at(*p) for p in points], stroke_width=0)
            poly.set_fill(colour, opacity=0.22)
            return poly

        shades = VGroup(
            piece([(0, 0), (1, 0), (1, 4), (0, 4)], theme.C_A),
            piece([(1, 0), (6, 0), (6, 1), (1, 1)], theme.C_AI),
            piece([(1, 1), (6, 4), (1, 4)], theme.C_B),
            piece([(1, 1), (6, 1), (6, 4)], theme.C_BI),
        )
        self.play(FadeIn(shades, run_time=0.8))

        # we cut, we slide, we put it back together
        self.play(
            shades[0].animate(run_time=1.4, rate_func=theme.EASE).shift(LEFT * 0.55 + DOWN * 0.25),
            shades[1].animate(run_time=1.4, rate_func=theme.EASE).shift(DOWN * 0.55),
            shades[2].animate(run_time=1.4, rate_func=theme.EASE).shift(UP * 0.35 + LEFT * 0.2),
            shades[3].animate(run_time=1.4, rate_func=theme.EASE).shift(RIGHT * 0.5),
            bar.animate(run_time=1.4).set_opacity(0.25),
            cuts.animate(run_time=1.4).set_stroke(opacity=0.25),
        )
        self.wait(0.5)

        rebuilt = motifs.chocolate_bar(COLS, ROWS, CELL)
        rebuilt.scale(SHRINK).move_to(bar)
        spare = motifs.chocolate_bar(1, 1, CELL)
        spare.next_to(rebuilt, RIGHT, buff=1.15)
        self.play(
            FadeOut(shades, run_time=0.9),
            FadeOut(cuts, run_time=0.9),
            FadeOut(bar, run_time=0.9),
            FadeIn(rebuilt, run_time=1.2),
        )
        self.wait(0.5)

        # count them
        numbers = VGroup()
        for i, cell in enumerate(rebuilt.squares):
            tag = theme.formula(str(i + 1), size=24, color="#F0E4D8").move_to(cell)
            numbers.add(tag)
        self.play(
            LaggedStart(*[FadeIn(t, run_time=0.16) for t in numbers], lag_ratio=0.55)
        )
        self.wait(0.4)

        self.play(FadeIn(spare, scale=1.4, run_time=0.9))
        tally = theme.body("twenty-four squares.  and one left over.", size=34, color=theme.GOLD)
        theme.foot(tally)
        self.play(Write(tally, run_time=1.4))
        self.wait(2.2)
        self.play(FadeOut(VGroup(rebuilt, numbers, spare, tally), run_time=0.9))


class S14Rigged(Scene):
    """Superimpose the before and the after: the rebuilt bar is shorter."""

    def construct(self):
        theme.apply_defaults(self)

        # the bar takes the left of the stage band, the magnifier the right,
        # and the reading goes to the foot band: three places, no argument
        before = motifs.chocolate_bar(COLS, ROWS, CELL)
        ghost = Rectangle(
            width=COLS * CELL, height=ROWS * CELL, color=theme.INK, stroke_width=2.0
        )
        after = motifs.chocolate_bar(COLS, ROWS, CELL)
        after.scale(SHRINK)
        for mob in (before, ghost, after):
            mob.move_to(np.array([-2.55, 0.0, 0.0]))

        head = theme.head(theme.body("before and after, superimposed", size=30,
                                     color=theme.INK_DIM))

        self.play(FadeIn(before, run_time=0.9))
        self.wait(0.5)
        self.play(FadeOut(before, run_time=0.6), FadeIn(after, run_time=0.6),
                  Create(ghost, run_time=0.8))
        self.play(FadeIn(head, run_time=0.7))
        self.wait(1.0)

        # tenfold magnification at the right edge of the bar
        lens = Circle(radius=0.55, color=theme.INK_DIM, stroke_width=2.4)
        lens.move_to(ghost.get_right())
        self.play(Create(lens, run_time=0.7))

        frame = Circle(radius=1.35, color=theme.INK_DIM, stroke_width=2.4)
        gap = float((1 - SHRINK) * COLS * CELL / 2 * 10)
        real_edge = Line(UP * 1.25, DOWN * 1.25, color=theme.INK, stroke_width=3.0)
        rebuilt_edge = Line(UP * 1.25, DOWN * 1.25, color=theme.CHOCO_LIGHT, stroke_width=3.0)
        rebuilt_edge.shift(LEFT * min(gap, 1.15))
        measure = Line(rebuilt_edge.get_top(), real_edge.get_top(), color=theme.REFUSE,
                       stroke_width=2.4).shift(DOWN * 0.18)
        tag = theme.caption("× 10", size=24).next_to(frame, UP, buff=0.14)
        inset = VGroup(frame, real_edge, rebuilt_edge, measure, tag)
        inset.move_to(np.array([4.35, 0.0, 0.0]))

        link = Line(lens.get_center(), frame.get_left(), color=theme.GHOST, stroke_width=1.2)
        self.play(Create(link, run_time=0.5), FadeIn(inset, run_time=0.9))
        self.wait(0.8)

        verdict = VGroup(
            theme.body("every row has lost a hair's width", size=28),
            theme.body("twenty-four hairs end to end make exactly one square", size=28,
                       color=theme.GOLD),
        ).arrange(DOWN, buff=0.24)
        theme.foot(verdict)
        anim.write_lines(self, verdict, per_line=1.3, lag=0.8)
        self.wait(1.2)

        moral = theme.body("we did not create chocolate.  we spread it out.", size=32,
                           color=theme.INK_DIM)
        moral.move_to(head)
        self.play(FadeOut(head, run_time=0.4), FadeIn(moral, run_time=0.7))
        self.wait(2.2)
        self.play(FadeOut(VGroup(after, ghost, lens, inset, link, verdict, moral),
                          run_time=0.9))
        theme.assert_clear(after, inset, verdict, moral)


class S14Volume(Scene):
    """What a volume is, and which sets have one."""

    def construct(self):
        theme.apply_defaults(self)

        head = theme.body("a volume attaches a number to a set of points, obeying two rules",
                          size=30, color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.9))

        rules = VGroup(
            theme.formula(r"\mu(X \sqcup Y) \;=\; \mu(X) + \mu(Y)", size=42),
            theme.formula(r"\mu(\rho(X)) \;=\; \mu(X)", size=42),
        ).arrange(DOWN, buff=0.5)
        theme.stage(rules)
        anim.write_lines(self, rules, per_line=1.4, lag=0.8)
        self.wait(0.8)

        glosses = VGroup(
            theme.caption("the volumes of two disjoint pieces add up", size=26),
            theme.caption("moving a piece does not change its volume", size=26),
        )
        for gloss, rule in zip(glosses, rules):
            gloss.next_to(rule, DOWN, buff=0.18)
        self.play(FadeIn(glosses, run_time=0.8))
        self.wait(1.0)

        measurable = theme.body(
            "measurable:  a set you can approximate as closely as you like with boxes",
            size=30,
            color=theme.GOLD,
        )
        examples = theme.caption(
            "a chocolate bar, a cube, a ball, some wildly irregular shape — virtually everything",
            size=26,
        )
        # both lines belong to the foot band, so the band holds the pair
        closing = theme.foot(VGroup(measurable, examples).arrange(DOWN, buff=0.22))

        self.play(Write(measurable, run_time=1.8))
        self.play(FadeIn(examples, run_time=0.8))
        self.wait(1.2)

        punch = theme.body("our four batches are not.", size=32, color=theme.REFUSE)
        punch.move_to(examples)
        self.play(FadeOut(examples, run_time=0.4), FadeIn(punch, scale=1.1, run_time=0.7))
        self.wait(2.2)
        self.play(FadeOut(VGroup(head, rules, glosses, closing, punch), run_time=0.9))


class S14EndlessZoom(Scene):
    """ANIMATION IDEA — endless continuous zoom into P₁.

        "At every scale, the same riddled texture.  Never an edge, never a
        stable structure."

    Built as three uniform fields of dust a third of an octave apart, each
    doubling in scale and then recycling, each weighted by sin² of its phase so
    that the three weights always sum to the same number.  The frame therefore
    magnifies for ever at constant density, and no layer's reset is visible.

    Membership of P₁ is re-drawn at every recycle: a quarter of the dust
    belongs, three quarters do not, and which is which never settles.  That is
    the whole content of "everywhere present and everywhere absent" — there is
    no magnification at which an edge appears, because there is no edge.
    """

    PER_LAYER = 46000
    DECADES = 6.0

    def construct(self):
        theme.apply_defaults(self)

        rng = np.random.default_rng(17)
        # the base field only has to cover the frame at its smallest scale
        half_x, half_y = 8.2, 4.7
        bases, memberships, layers = [], [], []
        for _ in range(3):
            pts = np.zeros((self.PER_LAYER, 3))
            pts[:, 0] = rng.uniform(-half_x, half_x, self.PER_LAYER)
            pts[:, 1] = rng.uniform(-half_y, half_y, self.PER_LAYER)
            bases.append(pts)
            memberships.append(rng.integers(0, 4, size=(self.PER_LAYER, 48)))
            layers.append(PMobject(stroke_width=2.6))
        field = Group(*layers)
        self.add(field)

        rgb = space.rgb_of(theme.C_A)
        # The magnification is typeset, so it is only re-set when the octave
        # changes — about twenty times across the shot, not once a frame.
        readout = theme.formula(r"\times 1", size=30, color=theme.INK_DIM)
        readout.move_to(np.array([theme.FRAME_W / 2 - 1.5, theme.TOP_EDGE - 0.75, 0.0]))
        self.add(readout)
        shown = {"octave": -1}

        octaves = self.DECADES * np.log2(10.0)

        def paint(_m, alpha):
            t = octaves * alpha
            for j, (base, member, layer) in enumerate(zip(bases, memberships, layers)):
                phase = (t + j / 3.0) % 1.0
                cycle = int(t + j / 3.0) % member.shape[1]
                scale = 2.0**phase
                weight = float(np.sin(np.pi * phase) ** 2)
                pts = base * scale
                keep = (
                    (np.abs(pts[:, 0]) < 7.5)
                    & (np.abs(pts[:, 1]) < 4.25)
                    & (member[:, cycle] == 0)
                )
                idx = np.flatnonzero(keep)
                layer.points = pts[idx]
                rgba = np.ones((len(idx), 4))
                rgba[:, :3] = rgb * weight
                layer.rgbas = rgba

            octave = int(t)
            if octave != shown["octave"]:
                shown["octave"] = octave
                zoom = 2.0**octave
                tex = (rf"\times {zoom:,.0f}".replace(",", r"\,")
                       if zoom < 1e4 else rf"\times 10^{{{np.log10(zoom):.1f}}}")
                fresh = theme.formula(tex, size=30, color=theme.INK_DIM)
                fresh.move_to(readout, aligned_edge=RIGHT)
                readout.become(fresh)

        head = theme.body("zoom into P₁ — as far as you like", size=30, color=theme.INK_DIM)
        theme.head(head)
        self.add(head)
        self.play(UpdateFromAlphaFunc(field, paint, run_time=13.0, rate_func=lambda x: x))

        verdict = theme.body(
            "never an edge, never a stable structure", size=32, color=theme.GOLD
        )
        theme.foot(verdict)
        self.play(Write(verdict, run_time=1.6))
        self.wait(2.0)
        self.play(FadeOut(Group(field, head, verdict, readout), run_time=0.9))


class S14ScaleNeverSettles(Scene):
    """ANIMATION IDEA — the scale that never settles.

        "Put a chocolate bar on a weighing scale: the needle lands cleanly.  A
        cube: clean.  A wildly irregular shape: clean.  Now put P₁ on it: the
        needle swings between two bounds, and the two never meet."
    """

    def construct(self):
        theme.apply_defaults(self)

        scale = motifs.Scale(radius=1.7)
        scale.move_to(DOWN * 0.6)
        self.play(FadeIn(scale, run_time=0.9))

        specimens = [
            ("a chocolate bar", motifs.chocolate_bar(3, 2, 0.34), 0.42),
            ("a cube", self._cube(), 0.62),
            ("a wildly irregular shape", self._blob(), 0.31),
        ]
        for name, mob, value in specimens:
            mob.scale_to_fit_height(0.75).next_to(scale.pan, UP, buff=0.12)
            tag = theme.head(theme.caption(name, size=26))
            self.play(FadeIn(mob, run_time=0.5), FadeIn(tag, run_time=0.5))
            self.play(
                UpdateFromAlphaFunc(
                    scale,
                    lambda m, a, v=value: m.point_at(
                        v * a + 0.12 * np.sin(a * 22) * (1 - a) ** 2
                    ),
                    run_time=1.5,
                    rate_func=theme.EASE,
                )
            )
            clean = theme.body("clean", size=28, color=theme.C_B)
            clean.next_to(scale, DOWN, buff=0.35)
            self.play(FadeIn(clean, run_time=0.4))
            self.wait(0.5)
            self.play(FadeOut(VGroup(mob, tag, clean), run_time=0.4))

        # and now P₁
        dust = self._dust()
        dust.next_to(scale.pan, UP, buff=0.12)
        tag = theme.head(theme.formula("P_1", size=40, color=theme.C_A))
        self.play(FadeIn(dust, run_time=0.6), FadeIn(tag, run_time=0.5))

        lower = theme.caption("inner boxes", size=20, color=theme.INK_DIM)
        upper = theme.caption("outer boxes", size=20, color=theme.INK_DIM)
        lower.next_to(scale, LEFT, buff=0.35).shift(UP * 0.3)
        upper.next_to(scale, RIGHT, buff=0.35).shift(UP * 0.3)
        self.play(FadeIn(lower, run_time=0.5), FadeIn(upper, run_time=0.5))

        swing = theme.body("the two approximations never meet", size=28, color=theme.REFUSE)
        swing.next_to(scale, DOWN, buff=0.35)
        self.play(FadeIn(swing, run_time=0.6))

        # the needle is never allowed to stop
        def keep_swinging(mob, dt):
            keep_swinging.t += dt
            mob.point_at(0.5 + 0.30 * np.sin(keep_swinging.t * 2.6))

        keep_swinging.t = 0.0
        scale.add_updater(keep_swinging)
        self.wait(6.0)

        note = theme.caption("let it still be swinging when the picture cuts to black", size=22)
        theme.foot(note)
        self.play(FadeIn(note, run_time=0.8))
        self.wait(4.0)

    # ---------------------------------------------------------------- props
    @staticmethod
    def _cube():
        return motifs.rubik_cube(cell=0.26)

    @staticmethod
    def _blob():
        rng = np.random.default_rng(4)
        n = 11
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        radii = 0.5 * (1 + 0.45 * rng.normal(size=n))
        pts = [np.array([np.cos(a) * r, np.sin(a) * r, 0]) for a, r in zip(angles, radii)]
        curve = VMobject(stroke_color=theme.INK_DIM, stroke_width=2.0)
        curve.set_points_smoothly(pts + [pts[0]])
        curve.set_fill(theme.INK_DIM, opacity=0.18)
        return VGroup(curve)

    @staticmethod
    def _dust():
        rng = np.random.default_rng(8)
        pts = np.zeros((2600, 3))
        pts[:, 0] = rng.uniform(-0.55, 0.55, 2600)
        pts[:, 1] = rng.uniform(-0.35, 0.35, 2600)
        cloud = PMobject(stroke_width=1.6)
        rgba = np.ones((len(pts), 4))
        rgba[:, :3] = space.rgb_of(theme.C_A)
        cloud.add_points(pts, rgbas=rgba)
        return Group(cloud)


class S14Closing(Scene):
    """The last second: the impossible hand, then black, then the paper."""

    def construct(self):
        theme.apply_defaults(self)

        bar = motifs.chocolate_bar(4, 2, 0.66)
        bar.move_to(DOWN * 0.3)
        self.play(FadeIn(bar, run_time=1.0))
        self.wait(0.8)

        hand = motifs.ChoiceHand(scale=1.5)
        hand.move_to(bar.get_center() + UP * 1.35)
        self.play(FadeIn(hand, run_time=0.5))
        self.wait(1.0)
        self.play(FadeOut(hand, run_time=0.5))
        self.wait(0.6)
        self.play(FadeOut(bar, run_time=1.2))
        self.wait(1.0)

        card = VGroup(
            theme.serif("Banach and Tarski", size=34),
            theme.serif(
                "Sur la décomposition des ensembles de points", size=28, color=theme.INK_DIM
            ),
            theme.serif("en parties respectivement congruentes", size=28, color=theme.INK_DIM),
            theme.caption("Fundamenta Mathematicae, 1924", size=24),
        ).arrange(DOWN, buff=0.28)
        self.play(FadeIn(card, run_time=1.6))
        self.wait(3.0)
        self.play(FadeOut(card, run_time=1.6))
        self.wait(1.0)
