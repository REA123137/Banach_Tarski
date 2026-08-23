"""Scene 5 — 04:35-06:20 · The group F2, and why it must be free.

    "ON SCREEN  F2 = {all reduced words written with a, a⁻¹, b, b⁻¹}"

    "ANIMATION – The cube face turns four times and the cube is identical
    again.  Underneath, the word aaaa writes itself, then collapses to e."

    "ANIMATION IDEA – The Library of Babel. […] In a library that is not free,
    the Rubik's cube one, we pull two books with different spines and open them
    side by side: THE SAME PAGE.  Two titles, one book.  In ours, we repeat the
    experiment ten times: never the same page twice."

The pages are not staged: :func:`banach_tarski.motifs.orientation_icon` draws
the genuine matrix product of the word on the spine, so "never the same page"
is a fact the render checks.
"""

from __future__ import annotations

# The manim CLI runs a scene file as a loose script, so the package root has to
# be on sys.path before the shared modules can be imported.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from manim import (
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    PI,
    RIGHT,
    Rotate,
    Scene,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, freegroup, motifs, theme
from banach_tarski.rotations import word_matrix


class S05Catalogue(Scene):
    """F2: the catalogue of every possible sequence of motions."""

    def construct(self):
        theme.apply_defaults(self)

        name = theme.formula("F₂", size=72)
        name.to_edge(UP, buff=0.9)
        definition = theme.body(
            "{ all reduced words written with  a,  a⁻¹,  b,  b⁻¹ }", size=38
        )
        definition.next_to(name, DOWN, buff=0.45)
        self.play(Write(name, run_time=0.9), Write(definition, run_time=1.5))
        self.wait(0.6)

        plain = theme.body(
            "the catalogue of every possible sequence of motions", size=30, color=theme.INK_DIM
        )
        plain.next_to(definition, DOWN, buff=0.42)
        self.play(FadeIn(plain, run_time=0.8))

        # the catalogue fills the frame, longest words last
        rows = VGroup()
        for length in range(1, 5):
            words = [w for w in freegroup.words(length, include_empty=False) if len(w) == length]
            row = VGroup(
                *[theme.word_mobject(w, size=24) for w in words[:18]]
            ).arrange(RIGHT, buff=0.42)
            if row.width > 12.6:
                row.scale_to_fit_width(12.6)
            rows.add(row)
        rows.arrange(DOWN, buff=0.38).next_to(plain, DOWN, buff=0.6)
        for row in rows:
            self.play(FadeIn(row, lag_ratio=0.06, run_time=0.9))
        dots = theme.body("…", size=40, color=theme.INK_DIM).next_to(rows, DOWN, buff=0.2)
        self.play(FadeIn(dots, run_time=0.5))
        self.wait(1.0)

        note = theme.caption(
            "including the ones a thousand letters long", size=24
        ).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note, run_time=0.6))
        self.wait(1.6)
        self.play(FadeOut(VGroup(name, definition, plain, rows, dots, note), run_time=0.8))


class S05GroupAndFree(Scene):
    """Three things you can do with it — and then the property everything needs."""

    def construct(self):
        theme.apply_defaults(self)

        head = theme.body("We call it a group, because there are three things we can do:",
                          size=32, color=theme.INK_DIM)
        head.to_edge(UP, buff=1.0)
        self.play(FadeIn(head, run_time=0.8))

        cards = VGroup()
        for title, sample in (
            ("chain", "a  ·  b⁻¹   →   a b⁻¹"),
            ("do nothing", "e"),
            ("undo", "a b⁻¹  ·  b a⁻¹   →   e"),
        ):
            box = theme.panel(3.7, 2.0)
            label = theme.body(title, size=30, color=theme.GOLD)
            body = theme.mono(sample, size=24, color=theme.INK)
            inner = VGroup(label, body).arrange(DOWN, buff=0.35).move_to(box)
            cards.add(VGroup(box, inner))
        cards.arrange(RIGHT, buff=0.45).next_to(head, DOWN, buff=0.8)
        self.play(FadeIn(cards, lag_ratio=0.2, run_time=1.4))
        self.wait(1.4)
        self.play(FadeOut(cards, run_time=0.6), FadeOut(head, run_time=0.6))

        # and now the property everything depends on
        title = theme.display("free", size=64, color=theme.GOLD).to_edge(UP, buff=1.1)
        formal = VGroup(
            theme.body("A group is free when two different words always name", size=32),
            theme.body("two different elements, unless their equality already", size=32),
            theme.body("follows from the group axioms alone.", size=32),
        ).arrange(DOWN, buff=0.30)
        formal.next_to(title, DOWN, buff=0.7)
        plain = VGroup(
            theme.body("No shortcuts.", size=34, color=theme.INK_DIM),
            theme.body("Two different sequences leave you in different states.", size=34,
                       color=theme.INK_DIM),
        ).arrange(DOWN, buff=0.26)
        plain.next_to(formal, DOWN, buff=0.75)

        self.play(Write(title, run_time=0.9))
        anim.write_lines(self, formal, per_line=1.1, lag=0.8)
        self.wait(0.6)
        anim.write_lines(self, plain, per_line=1.1, lag=0.8)
        self.wait(2.0)
        self.play(FadeOut(VGroup(title, formal, plain), run_time=0.8))


class S05RubikNotFree(Scene):
    """The counter-example: on a cube, a a a a is the empty word."""

    def construct(self):
        theme.apply_defaults(self)

        cube = motifs.rubik_cube(cell=0.62)
        cube.move_to(UP * 1.0)
        ghost = cube.copy().set_opacity(0.18)
        self.add(ghost)
        self.play(FadeIn(cube, run_time=0.8))

        word = VGroup()
        for i in range(4):
            self.play(Rotate(cube.front, angle=-PI / 2, run_time=0.7, rate_func=theme.EASE))
            tile = theme.mono("a", size=52, color=theme.C_A)
            word.add(tile)
            word.arrange(RIGHT, buff=0.35).move_to(DOWN * 1.3)
            self.play(FadeIn(tile, shift=UP * 0.15, run_time=0.28))

        same = theme.body("identical again — and nothing cancelled", size=30, color=theme.INK_DIM)
        same.next_to(word, DOWN, buff=0.55)
        self.play(FadeIn(same, run_time=0.8))
        self.wait(0.8)

        empty = theme.mono("e", size=52, color=theme.C_E).move_to(word)
        self.play(
            *[t.animate(run_time=0.7).move_to(word.get_center()).set_opacity(0.0) for t in word],
            FadeIn(empty, run_time=0.7),
        )
        verdict = theme.body("the Rubik's cube group is not free: it has shortcuts",
                             size=30, color=theme.REFUSE)
        verdict.move_to(same)
        self.play(FadeOut(same, run_time=0.4), FadeIn(verdict, run_time=0.6))
        self.wait(2.0)
        self.play(FadeOut(VGroup(cube, ghost, empty, verdict), run_time=0.8))


class S05LibraryFlight(Scene):
    """ANIMATION IDEA — the Library of Babel: a flight through the catalogue.

        "The camera flies through an infinite hexagonal library, Borges style,
        where every book spine carries a word: ab, aab, ba⁻¹b.  We pull one
        volume at random, open it, and it holds a drawn sequence of rotations."
    """

    def construct(self):
        theme.apply_defaults(self)
        library = motifs.Library(depth=7, seed=4)
        self.add(library)
        library.add_updater(library.fly(rate=0.30))

        title = theme.serif("a Library of Babel made of motions", size=34)
        title.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(title, run_time=1.2))
        self.wait(4.0)
        self.play(FadeOut(title, run_time=0.8))

        # one volume is pulled, and opened
        library.suspend_updating()
        scrim = theme.panel(16.0, 9.0, fill="#000000", stroke="#000000")
        scrim.set_opacity(0.0)
        self.add(scrim)
        pulled = motifs.book("baB", height=1.4, width=0.36)
        pulled.move_to(LEFT * 3.2)
        self.play(
            scrim.animate(run_time=0.8).set_opacity(0.72),
            FadeIn(pulled, run_time=0.8),
        )
        opened = motifs.open_book("baB", word_matrix("baB"), width=3.4, height=2.4)
        opened.move_to(RIGHT * 1.6)
        self.play(FadeIn(opened, shift=LEFT * 0.3, run_time=1.0))
        note = theme.caption("inside: a drawn sequence of rotations", size=24)
        note.next_to(opened, DOWN, buff=0.45)
        self.play(FadeIn(note, run_time=0.7))
        self.wait(2.2)
        self.play(FadeOut(VGroup(scrim, pulled, opened, note), run_time=0.8))


class S05SamePage(Scene):
    """ANIMATION IDEA — the definition of "free", made visible in ten seconds.

    Left: a library that is not free.  Two different spines, one page.
    Right: ours.  Ten draws, never the same page twice.
    """

    def construct(self):
        theme.apply_defaults(self)

        # -- the library that is not free ---------------------------------
        head = theme.body("a library that is not free", size=32, color=theme.REFUSE)
        head.to_edge(UP, buff=0.9)
        self.play(FadeIn(head, run_time=0.7))

        # on a cube, turning one face four times changes nothing
        identity = np.eye(3)
        left = motifs.open_book("aaaa", identity, width=3.0, height=2.2)
        right = motifs.open_book("", identity, width=3.0, height=2.2)
        pair = VGroup(left, right).arrange(RIGHT, buff=1.1).shift(DOWN * 0.3)
        self.play(FadeIn(pair, lag_ratio=0.25, run_time=1.2))
        verdict = theme.display("THE SAME PAGE", size=44, color=theme.REFUSE)
        verdict.next_to(pair, DOWN, buff=0.7)
        self.play(Write(verdict, run_time=1.0))
        self.wait(1.6)
        self.play(FadeOut(VGroup(pair, verdict, head), run_time=0.7))

        # -- ours ---------------------------------------------------------
        head2 = theme.body("ours", size=32, color=theme.C_B).to_edge(UP, buff=0.9)
        self.play(FadeIn(head2, run_time=0.6))

        draws = ["a", "b", "ab", "ba", "aab", "abA", "bba", "aB", "bAb", "aaB"]
        shown = VGroup()
        seen: list[np.ndarray] = []
        for i, w in enumerate(draws):
            m = word_matrix(w)
            assert not any(np.allclose(m, s, atol=1e-6) for s in seen), (
                "two draws landed on the same page — the group would not be free"
            )
            seen.append(m)
            bk = motifs.open_book(w, m, width=2.3, height=1.6)
            shown.add(bk)
            shown.arrange_in_grid(rows=2, cols=5, buff=0.28)
            shown.next_to(head2, DOWN, buff=0.6)
            if shown.width > 13.0:
                shown.scale_to_fit_width(13.0)
            self.play(FadeIn(bk, run_time=0.42, rate_func=theme.EASE_OUT))

        verdict2 = theme.display("never the same page twice", size=42, color=theme.C_B)
        verdict2.to_edge(DOWN, buff=0.6)
        self.play(Write(verdict2, run_time=1.2))
        self.wait(2.2)
        self.play(FadeOut(VGroup(shown, verdict2, head2), run_time=0.8))
