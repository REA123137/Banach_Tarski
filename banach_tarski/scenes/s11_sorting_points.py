"""Scene 11 — 15:25-18:35 · Sorting the points, batch by batch.

    "We are not going to invent anything.  We are redoing, word for word,
    exactly what we did earlier with the letters."

Nothing here is staged.  A real orbit is generated, every point remembers the
word that produced it, the batches are the true ``S(A)M``…, and when the batch
``P₂`` is rotated by ``A`` each point lands exactly on the point whose word is
``reduce("a" + w)``.  The "ink in water" of the script is then literally the
recolouring of those landing points.

    "ANIMATION IDEA – Split screen, letters and points. […] Both animations
    replay in parallel, frame for frame, perfectly synchronised."

    "And for the union itself, ink in water: the colour of P₂ does not jump
    from batch to batch, it spreads until it covers the regions of the other
    two colours."
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
    Line,
    RIGHT,
    Scene,
    Transform,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, freegroup, space, theme
from banach_tarski.rotations import A, B, orbit

MAX_LEN = 8  # 13 121 points: one orbit, dense enough to read as dust
BATCH_COLORS = {"a": theme.C_A, "A": theme.C_AI, "b": theme.C_B, "B": theme.C_BI, "": theme.C_E}


def build_orbit(seed_point=None, max_length: int = MAX_LEN):
    """A real orbit, with every point's itinerary kept alongside it."""
    if seed_point is None:
        seed_point = np.array([0.37, -0.52, 0.77])
        seed_point = seed_point / np.linalg.norm(seed_point)
    pts, words = orbit(seed_point, max_length=max_length)
    heads = np.array([w[0] if w else "" for w in words])
    index = {w: i for i, w in enumerate(words)}
    return pts, words, heads, index


class S11Batches(Scene):
    """Every point inherits the first letter of its itinerary."""

    def construct(self):
        theme.apply_defaults(self)

        formula = theme.formula(
            "S(A) M  =  { ρ(m) :  m ∈ M,  ρ begins with A }", size=36
        )
        formula.to_edge(UP, buff=0.5)
        self.play(Write(formula, run_time=1.8))

        pts, words, heads, _ = build_orbit()
        # the sphere sits right of centre: the legend needs the left third
        stage = space.Stage(space.View(yaw=-0.55, pitch=0.24, scale=2.25))
        stage.view.origin = np.array([2.15, -0.30, 0.0])
        for wire in space.wire_sphere(1.0, 10, 5, color="#141414", width=1.0):
            stage.add(wire)
        cloud = space.Cloud(pts, colors=theme.INK_DIM, size=2.4, size_far=0.9, fog=0.8, bands=6)
        stage.add(cloud)
        stage.install(self)
        stage.spin(self, speed=0.10)
        self.wait(1.0)

        targets = np.array([space.rgb_of(BATCH_COLORS[h]) for h in heads])
        self.play(space.recolor_cloud(cloud, targets, run_time=2.4))

        legend = VGroup()
        for letter in ("a", "A", "b", "B"):
            dot = theme.body("●", size=22, color=BATCH_COLORS[letter])
            tag = theme.body(
                f"P{'1234'[('a', 'A', 'b', 'B').index(letter)]}  ·  begins with "
                f"{theme.letter_glyph(letter)}",
                size=22,
                color=theme.INK_DIM,
            )
            legend.add(VGroup(dot, tag).arrange(RIGHT, buff=0.20))
        legend.arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        legend.move_to(np.array([-4.6, -0.2, 0.0]))
        self.play(FadeIn(legend, lag_ratio=0.15, run_time=1.0))

        white = theme.caption("the representative stays white:", size=22)
        white2 = theme.caption("its itinerary is empty", size=22)
        white = VGroup(white, white2).arrange(DOWN, buff=0.14)
        white.move_to(np.array([-4.6, -2.5, 0.0]))
        self.play(FadeIn(white, run_time=0.8))
        self.wait(2.6)
        self.play(FadeOut(VGroup(formula, legend, white), run_time=0.8))


class S11Definitions(Scene):
    """The four batches, written out, with the buffer queue X."""

    def construct(self):
        theme.apply_defaults(self)

        queue = theme.formula("X  =  A⁻¹M  ∪  A⁻²M  ∪  A⁻³M  ∪  ⋯", size=38)
        queue.to_edge(UP, buff=1.0)
        self.play(Write(queue, run_time=1.8))
        note = theme.caption("the buffer, exactly as the empty word was earlier", size=24)
        note.next_to(queue, DOWN, buff=0.3)
        self.play(FadeIn(note, run_time=0.7))
        self.wait(0.6)

        batches = VGroup(
            theme.formula("P₁  =  S(A) M  ∪  M  ∪  X", size=36, color=theme.C_A),
            theme.formula("P₂  =  S(A⁻¹) M  ∖  X", size=36, color=theme.C_AI),
            theme.formula("P₃  =  S(B) M", size=36, color=theme.C_B),
            theme.formula("P₄  =  S(B⁻¹) M", size=36, color=theme.C_BI),
        ).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        batches.next_to(note, DOWN, buff=0.8)
        anim.write_lines(self, batches, per_line=1.1, lag=0.7)
        self.wait(2.4)
        self.play(FadeOut(VGroup(queue, note, batches), run_time=0.8))


class S11InkInWater(Scene):
    """The heart of the scene: one batch is rotated and covers three.

    ``P₂`` is the set of points whose itinerary begins with ``a⁻¹``.  Applying
    ``A`` to it moves every one of its points onto the point whose itinerary is
    ``reduce("a" + w)`` — computed here, not choreographed — and those landing
    points are precisely batches two, three and four.
    """

    def construct(self):
        theme.apply_defaults(self)

        pts, words, heads, index = build_orbit()
        stage = space.Stage(space.View(yaw=-0.55, pitch=0.24, scale=2.35))
        stage.view.origin = np.array([0.0, -0.35, 0.0])
        for wire in space.wire_sphere(1.0, 10, 5, color="#141414", width=1.0):
            stage.add(wire)

        clouds = {}
        for letter in ("a", "A", "b", "B", ""):
            mask = heads == letter
            if not mask.any():
                continue
            cloud = space.Cloud(
                pts[mask], colors=BATCH_COLORS[letter], size=2.4, size_far=0.9, fog=0.8, bands=6
            )
            cloud.words = [w for w, h in zip(words, heads) if h == letter]
            clouds[letter] = cloud
            stage.add(cloud)
        stage.install(self)
        self.wait(0.8)

        head = theme.body("apply A to the whole of P₂", size=32, color=theme.C_AI)
        head.to_edge(UP, buff=0.6)
        self.play(FadeIn(head, run_time=0.8))

        # The four batches are interleaved everywhere — that is what makes them
        # what they are, and it also makes them impossible to tell apart.  So
        # the other three are taken almost to nothing while P₂ moves; they come
        # back when the union has to be seen.
        self.play(
            *[
                space.fade_cloud(c, 0.05, run_time=1.2)
                for k, c in clouds.items()
                if k != "A"
            ]
        )

        # the rotation.  it is rigid, and it is the real matrix.
        p2 = clouds["A"]
        self.play(space.rotate_cloud(p2, A, run_time=3.0))
        self.wait(0.4)

        # ink in water: each landing point takes the colour of the batch it fell in
        landed = [freegroup.reduce("a" + w) for w in p2.words]
        targets = np.array([space.rgb_of(BATCH_COLORS[w[0] if w else ""]) for w in landed])
        ink = theme.caption("the colour spreads — it does not jump", size=24)
        ink.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(ink, run_time=0.6))
        self.play(space.recolor_cloud(p2, targets, run_time=3.2))
        self.wait(0.8)

        result = theme.formula("A P₂  =  P₂ ∪ P₃ ∪ P₄", size=42, color=theme.GOLD)
        result.to_edge(DOWN, buff=1.1)
        self.play(Write(result, run_time=1.4))
        self.wait(1.4)

        # and adding the untouched first batch gives back everything
        self.play(
            FadeOut(head, run_time=0.5),
            space.fade_cloud(clouds["a"], 1.0, run_time=1.4),
            space.fade_cloud(clouds[""], 1.0, run_time=1.4),
        )
        whole = theme.formula("P₁ ∪ A P₂  =  L₀ ∖ D", size=42, color=theme.GOLD)
        whole.move_to(result)
        self.play(Transform(result, whole, run_time=1.2))
        self.wait(2.2)
        self.play(FadeOut(VGroup(result, ink), run_time=0.8))


class S11SecondPair(Scene):
    """The other half of the sphere does exactly the same thing, with B."""

    def construct(self):
        theme.apply_defaults(self)

        pts, words, heads, _ = build_orbit()
        stage = space.Stage(space.View(yaw=-0.35, pitch=0.26, scale=2.35))
        stage.view.origin = np.array([0.0, -0.35, 0.0])
        for wire in space.wire_sphere(1.0, 10, 5, color="#141414", width=1.0):
            stage.add(wire)

        clouds = {}
        for letter in ("a", "A", "b", "B", ""):
            mask = heads == letter
            if not mask.any():
                continue
            cloud = space.Cloud(
                pts[mask], colors=BATCH_COLORS[letter], size=2.4, size_far=0.9, fog=0.8, bands=6
            )
            cloud.words = [w for w, h in zip(words, heads) if h == letter]
            clouds[letter] = cloud
            stage.add(cloud)
        stage.install(self)

        head = theme.body("and again, with B, on the fourth batch", size=32, color=theme.C_BI)
        head.to_edge(UP, buff=0.6)
        self.play(FadeIn(head, run_time=0.8))
        self.play(*[space.fade_cloud(c, 0.05, run_time=1.2) for k, c in clouds.items() if k != "B"])

        p4 = clouds["B"]
        self.play(space.rotate_cloud(p4, B, run_time=3.0))
        landed = [freegroup.reduce("b" + w) for w in p4.words]
        targets = np.array([space.rgb_of(BATCH_COLORS[w[0] if w else ""]) for w in landed])
        self.play(space.recolor_cloud(p4, targets, run_time=2.8))

        result = theme.formula("B P₄  =  P₁ ∪ P₂ ∪ P₄        P₃ ∪ B P₄  =  L₀ ∖ D", size=38,
                               color=theme.GOLD)
        result.to_edge(DOWN, buff=0.6)
        self.play(Write(result, run_time=1.8))
        self.play(*[space.fade_cloud(c, 1.0, run_time=1.2) for c in clouds.values()])
        self.wait(2.2)
        self.play(FadeOut(VGroup(head, result), run_time=0.8))


class S11Equidecomposable(Scene):
    """The word promised at the start, defined at last."""

    def construct(self):
        theme.apply_defaults(self)

        title = theme.display("equidecomposable", size=54, color=theme.GOLD)
        title.to_edge(UP, buff=1.1)
        formal = VGroup(
            theme.body("Two sets are equidecomposable if one can be partitioned", size=32),
            theme.body("into finitely many parts which can be reassembled into", size=32),
            theme.body("the other by rigid motions alone.", size=32),
        ).arrange(DOWN, buff=0.30)
        formal.next_to(title, DOWN, buff=0.7)
        plain = theme.body(
            "one becomes the other by cutting and moving, deforming nothing", size=32,
            color=theme.INK_DIM,
        )
        plain.next_to(formal, DOWN, buff=0.75)

        self.play(Write(title, run_time=1.0))
        anim.write_lines(self, formal, per_line=1.1, lag=0.8)
        self.play(FadeIn(plain, run_time=0.9))
        self.wait(1.2)

        got = theme.body(
            "the ball, minus its centre and the poles, is equidecomposable with two copies of itself",
            size=30,
            color=theme.GOLD,
        )
        if got.width > 12.8:
            got.scale_to_fit_width(12.8)
        got.to_edge(DOWN, buff=0.6)
        self.play(Write(got, run_time=2.2))
        self.wait(2.4)
        self.play(FadeOut(VGroup(title, formal, plain, got), run_time=0.8))


class S11SplitScreen(Scene):
    """ANIMATION IDEA — split screen, letters and points, frame for frame.

        "on the left the four columns of words from the letters scene, on the
        right the four batches of points on the sphere.  Both animations replay
        in parallel, perfectly synchronised.  When the column S(a⁻¹) slides on
        the left, the batch P₂ rotates on the right, at the same instant."
    """

    def construct(self):
        theme.apply_defaults(self)
        from banach_tarski.scenes.s06_letter_trick import COLUMN_ORDER, Columns, slot

        divider = Line(UP * 3.5, DOWN * 3.5, color=theme.GHOST, stroke_width=1.4)
        self.add(divider)

        # -- left: the columns of words -----------------------------------
        cols = Columns(count=5)
        cols.scale(0.52)
        cols.move_to(LEFT * 3.55 + DOWN * 0.15)
        self.add(cols)

        # -- right: the batches of points ----------------------------------
        pts, words, heads, _ = build_orbit(max_length=6)
        stage = space.Stage(space.View(yaw=-0.5, pitch=0.24, scale=1.55))
        stage.view.origin = np.array([3.55, -0.15, 0.0])
        for wire in space.wire_sphere(1.0, 9, 4, color="#131313", width=1.0):
            stage.add(wire)
        clouds = {}
        for letter in ("a", "A", "b", "B", ""):
            mask = heads == letter
            if not mask.any():
                continue
            c = space.Cloud(pts[mask], colors=BATCH_COLORS[letter], size=2.4, size_far=0.9,
                            fog=0.8, bands=6)
            c.words = [w for w, h in zip(words, heads) if h == letter]
            clouds[letter] = c
            stage.add(c)
        stage.install(self)

        tags = VGroup(
            theme.caption("words", size=24).move_to(LEFT * 3.55 + UP * 3.55),
            theme.caption("points", size=24).move_to(RIGHT * 3.55 + UP * 3.55),
        )
        self.play(FadeIn(tags, run_time=0.8))
        self.wait(0.8)

        # the same gesture, both sides, at the same instant
        moves = []
        occupancy = {letter: 0 for letter in COLUMN_ORDER}
        for tile in cols.items["A"]:
            landed = freegroup.reduce("a" + tile.word)
            home = landed[0] if landed else ""
            new_tile = theme.word_mobject(landed, size=24).scale(0.52)
            if home == "":
                new_tile.move_to(cols.empty.get_center())
            else:
                row = occupancy[home]
                occupancy[home] = row + 1
                new_tile.move_to(cols.get_center() + (slot(home, row, incoming=True)
                                                      - Columns(count=5).get_center()) * 0.52)
            moves.append((tile, new_tile))

        p2 = clouds["A"]
        landed_words = [freegroup.reduce("a" + w) for w in p2.words]
        targets = np.array([space.rgb_of(BATCH_COLORS[w[0] if w else ""]) for w in landed_words])

        self.play(
            LaggedStart(
                *[Transform(old, new, run_time=1.6, rate_func=theme.EASE) for old, new in moves],
                lag_ratio=0.08,
            ),
            space.rotate_cloud(p2, A, run_time=3.0),
        )
        self.play(space.recolor_cloud(p2, targets, run_time=2.0))
        self.wait(0.6)

        verdict = theme.body("the same sentence, word for word", size=30, color=theme.GOLD)
        verdict.to_edge(DOWN, buff=0.35)
        self.play(Write(verdict, run_time=1.4))
        self.wait(2.2)
        self.play(FadeOut(VGroup(tags, verdict, cols, divider), run_time=0.8))
