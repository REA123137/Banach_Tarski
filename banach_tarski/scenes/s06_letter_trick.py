"""Scene 6 — 06:20-09:00 · The magic trick, done with letters.

The proof itself, in readable form — animation number two in the script's own
production order.

    "ANIMATION – Four coloured columns of words, plus a tiny box for the empty
    word."

    "ANIMATION – Each example writes itself, the two letters cancel in a fade,
    and the word physically jumps into its new column."

    "ANIMATION IDEA – The librarian pushes a shelf. […] The librarian pushes
    the a⁻¹ unit one notch to the right: every book sheds its first letter as
    it slides, and the unit overflows and fills the other three.  Books that
    change shelf change binding colour in mid-air."
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
    Flash,
    LEFT,
    LaggedStart,
    RIGHT,
    Scene,
    Transform,
    UP,
    VGroup,
    Write,
)

from banach_tarski import anim, freegroup, motifs, theme

COLUMN_ORDER = ["a", "A", "b", "B"]
COLUMN_X = {"a": -5.05, "A": -1.72, "b": 1.72, "B": 5.05}
TOP_Y = 1.75
ROW_H = 0.60
ROWS = 6
WORD_SIZE = 21

# Every column is two files wide: the words that were always there on the left,
# and, on the right, the words that arrive when a generator is pushed in front
# of another column.  A newcomer must land *inside* its pile, not underneath it.
FILE_OFFSET = 0.98


def column_words(letter: str, count: int = ROWS) -> list[str]:
    """The first few words of S(x), shortlex — the ones the shelf can show."""
    return [w for w in freegroup.words_starting_with(letter, 3)][:count]


def slot(letter: str, row: int, incoming: bool = False) -> np.ndarray:
    x = COLUMN_X[letter] + (FILE_OFFSET if incoming else -FILE_OFFSET)
    return np.array([x, TOP_Y - row * ROW_H, 0.0])


class Columns(VGroup):
    """Four coloured columns of words, plus a tiny box for the empty word."""

    def __init__(self, count: int = ROWS):
        super().__init__()
        self.headers = {}
        self.items: dict[str, list[VGroup]] = {}
        for letter in COLUMN_ORDER:
            colour = theme.LETTER_COLORS[letter]
            header = theme.formula(f"S({theme.letter_glyph(letter)})", size=32, color=colour)
            header.move_to(np.array([COLUMN_X[letter], TOP_Y + 0.72, 0.0]))
            rule = theme.rule(width=2.7, color=colour, stroke=1.2).set_opacity(0.4)
            rule.next_to(header, DOWN, buff=0.16)
            self.headers[letter] = VGroup(header, rule)
            self.add(self.headers[letter])
            self.items[letter] = []
            for row, word in enumerate(column_words(letter, count)):
                tile = theme.word_mobject(word, size=WORD_SIZE)
                tile.move_to(slot(letter, row))
                tile.word = word
                self.items[letter].append(tile)
                self.add(tile)
        # the empty word gets a box of its own: it is not in any column
        box = theme.panel(0.9, 0.72, fill="#0B0B0B", stroke=theme.GHOST)
        glyph = theme.formula("e", size=34, color=theme.C_E).move_to(box)
        self.empty = VGroup(box, glyph)
        self.empty.move_to(np.array([0.0, TOP_Y - (ROWS - 1) * ROW_H - 0.85, 0.0]))
        self.add(self.empty)


class S06Columns(Scene):
    """Sorting the catalogue by first letter: five piles, no overlap."""

    def construct(self):
        theme.apply_defaults(self)

        head = theme.body("I sort the catalogue by the first letter of each word.",
                          size=32, color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.8))

        cols = Columns()
        cols.shift(DOWN * 0.15)
        for letter in COLUMN_ORDER:
            self.play(
                FadeIn(cols.headers[letter], run_time=0.35),
                LaggedStart(
                    *[FadeIn(t, shift=UP * 0.12, run_time=0.28) for t in cols.items[letter]],
                    lag_ratio=0.13,
                ),
            )
        self.play(FadeIn(cols.empty, run_time=0.6))
        self.wait(0.6)

        formula = theme.formula(
            r"F_2 \;=\; \{e\} \sqcup S(a) \sqcup S(a^{-1}) \sqcup S(b) \sqcup S(b^{-1})",
            size=38,
        )
        note = theme.caption("five piles, covering everything, with no overlap", size=26)
        block = theme.foot(VGroup(note, formula).arrange(DOWN, buff=0.20))
        self.play(Write(formula, run_time=1.8))
        self.play(FadeIn(note, run_time=0.6))
        self.wait(2.0)
        self.play(FadeOut(VGroup(head, cols, block), run_time=0.8))


class S06Examples(Scene):
    """Four worked examples, the last one left to the viewer for three seconds."""

    EXAMPLES = ["Ab", "AA", "ABa", "Abb"]

    def construct(self):
        theme.apply_defaults(self)

        head = theme.body("I take the words beginning with a⁻¹, and stick an a in front.",
                          size=32, color=theme.INK_DIM)
        theme.head(head)
        self.play(FadeIn(head, run_time=0.9))

        for index, word in enumerate(self.EXAMPLES):
            challenge = index == len(self.EXAMPLES) - 1
            self._one_example(word, challenge)

        law = theme.body(
            "adding an a erases the first letter — and the second letter is anything but a⁻¹",
            size=30,
            color=theme.GOLD,
        )
        theme.foot(law)
        self.play(Write(law, run_time=2.0))
        self.wait(2.0)
        self.play(FadeOut(VGroup(head, law), run_time=0.8))

    # ---------------------------------------------------------------- helper
    def _one_example(self, word: str, challenge: bool):
        prefix = theme.formula("a", size=58, color=theme.C_A)
        letters = theme.word_mobject(word, size=54, spaced=True)
        row = VGroup(prefix, letters).arrange(RIGHT, buff=0.36).move_to(UP * 0.2)

        self.play(FadeIn(row, run_time=0.7))

        if challenge:
            mark = theme.display("?", size=64, color=theme.GOLD)
            mark.next_to(row, DOWN, buff=0.9)
            self.play(FadeIn(mark, run_time=0.4))
            anim.countdown_silence(self, 3.0, label="silence — 3 s")
            self.play(FadeOut(mark, run_time=0.3))

        # the a and the a⁻¹ annihilate, exactly as in scene 4
        merged = VGroup(prefix, *letters)
        anim.annihilate(self, merged[0], merged[1])
        rest = VGroup(*merged[2:])
        if len(rest):
            target = rest.copy().arrange(RIGHT, buff=0.36).move_to(UP * 0.2)
            self.play(
                *[m.animate.move_to(t) for m, t in zip(rest, target)],
                run_time=0.45,
                rate_func=theme.EASE,
            )

        result = freegroup.reduce("a" + word)
        home = result[0] if result else ""
        colour = theme.LETTER_COLORS[home]
        verdict = (
            theme.prose_math("now begins with {}", theme.letter_glyph(home), size=30,
                             color=colour)
            if home
            else theme.body("the empty word", size=30, color=colour)
        )
        verdict.next_to(rest if len(rest) else row, DOWN, buff=0.8)
        self.play(FadeIn(verdict, shift=UP * 0.12, run_time=0.6))
        self.wait(0.9)
        self.play(FadeOut(VGroup(rest, verdict), run_time=0.5))


class S06Doubling(Scene):
    """The whole column slides, and the catalogue comes out twice.

    Every jump is computed, not choreographed: the destination of a word is
    ``freegroup.reduce("a" + word)`` and the colour it lands in is the colour
    of that word's first letter.
    """

    def construct(self):
        theme.apply_defaults(self)

        cols = Columns()
        cols.shift(DOWN * 0.15)
        self.add(cols)
        self.wait(0.5)

        for generator, source in (("a", "A"), ("b", "B")):
            self._push(cols, generator, source)
            self.wait(0.6)

        # the verdict and the formula are one block, so the block is what is
        # fitted into the foot band — a caption placed above a footed line
        # would climb straight back into the columns
        final = theme.formula(
            r"F_2 = S(a) \sqcup a\,S(a^{-1}) \qquad\qquad F_2 = S(b) \sqcup b\,S(b^{-1})",
            size=34,
        )
        verdict = theme.body("four piles.  two complete catalogues.  nothing was added.",
                             size=28, color=theme.GOLD)
        closing = theme.foot(VGroup(verdict, final).arrange(DOWN, buff=0.22))
        self.play(Write(final, run_time=2.0))
        self.play(FadeIn(verdict, run_time=0.9))
        self.wait(2.4)
        self.play(FadeOut(VGroup(cols, closing), run_time=0.9))

    # ---------------------------------------------------------------- helper
    def _push(self, cols: Columns, generator: str, source: str):
        colour = theme.LETTER_COLORS[generator]
        banner = theme.prose_math(
            "put {} in front of every word of {}",
            theme.letter_glyph(generator),
            f"S({theme.letter_glyph(source)})",
            size=30,
            color=colour,
        )
        theme.head(banner)
        self.play(FadeIn(banner, run_time=0.7))

        # highlight the column that is about to move
        self.play(
            *[t.animate(run_time=0.5).scale(1.08) for t in cols.items[source]],
            cols.headers[source].animate(run_time=0.5).scale(1.08),
        )

        # where does each word go?  ask the group, not the storyboard
        moves = []
        # newcomers stack in the right-hand file of their destination pile,
        # from the top, so a pile never grows off the bottom of the frame
        occupancy = {letter: 0 for letter in COLUMN_ORDER}
        for tile in cols.items[source]:
            landed = freegroup.reduce(generator + tile.word)
            home = landed[0] if landed else ""
            new_tile = theme.word_mobject(landed, size=WORD_SIZE)
            if home == "":
                new_tile.move_to(cols.empty.get_center())
            else:
                row = occupancy[home]
                occupancy[home] = row + 1
                new_tile.move_to(slot(home, row, incoming=True))
            moves.append((tile, new_tile))

        self.play(
            LaggedStart(
                *[
                    Transform(old, new, run_time=1.1, rate_func=theme.EASE)
                    for old, new in moves
                ],
                lag_ratio=0.10,
            )
        )
        self.play(cols.headers[source].animate(run_time=0.4).scale(1 / 1.08))

        covered = (r"\{e\} \sqcup S(a^{-1}) \sqcup S(b) \sqcup S(b^{-1})"
                   if generator == "a"
                   else r"\{e\} \sqcup S(a) \sqcup S(a^{-1}) \sqcup S(b^{-1})")
        line = theme.formula(
            theme.letter_glyph(generator)
            + r"\,S(" + theme.letter_glyph(source) + r") \;=\; " + covered,
            size=34,
            color=colour,
        )
        theme.foot(line)
        self.play(Write(line, run_time=1.4))
        self.wait(1.4)
        self.play(FadeOut(VGroup(banner, line), run_time=0.6))


class S06Librarian(Scene):
    """ANIMATION IDEA — the librarian pushes a shelf.

        "Four shelving units, one per first letter.  The librarian pushes the
        a⁻¹ unit one notch to the right: every book sheds its first letter as
        it slides, and the unit overflows and fills the other three.  Books
        that change shelf change binding colour in mid-air."
    """

    def construct(self):
        theme.apply_defaults(self)

        units = VGroup()
        for letter in COLUMN_ORDER:
            words = column_words(letter, 9)
            unit = motifs.shelf_unit(
                words,
                per_row=3,
                rows=3,
                color=theme.LETTER_COLORS[letter],
                label=f"S({theme.letter_glyph(letter)})",  # set as maths by shelf_unit
            )
            units.add(unit)
        units.arrange(RIGHT, buff=0.55).scale_to_fit_width(12.0)
        if units.height > 5.4:
            units.scale_to_fit_height(5.4)
        units.move_to(UP * 0.55)
        self.play(FadeIn(units, lag_ratio=0.15, run_time=1.4))
        self.wait(0.6)

        hand = motifs.human_hand(scale=0.85)
        source_unit = units[1]
        hand.next_to(source_unit, LEFT, buff=0.1).shift(DOWN * 0.2)
        self.play(FadeIn(hand, run_time=0.6))

        # the push: every book of S(a⁻¹) sheds its first letter and re-binds
        source_books = [b for row in source_unit.books for b in row]
        targets = []
        for shelf_book in source_books:
            landed = freegroup.reduce("a" + shelf_book.word)
            colour = theme.LETTER_COLORS[landed[0] if landed else ""]
            new_book = motifs.book(landed, color=colour)
            new_book.scale(shelf_book.height / new_book.height)
            targets.append(new_book)

        # spread the re-bound books across the other three units
        destinations = []
        pool = [units[0], units[2], units[3]]
        for i, unit in enumerate(pool):
            for row in unit.books:
                for b in row:
                    destinations.append(b.get_center() + np.array([0.055, 0.075, 0.0]))
        rng = np.random.default_rng(5)
        rng.shuffle(destinations)

        anims = []
        for i, (shelf_book, new_book) in enumerate(zip(source_books, targets)):
            new_book.move_to(destinations[i % len(destinations)])
            anims.append(Transform(shelf_book, new_book, run_time=1.6, rate_func=theme.EASE))

        self.play(
            hand.animate(run_time=1.6, rate_func=theme.EASE).shift(RIGHT * 1.1),
            LaggedStart(*anims, lag_ratio=0.06),
        )
        self.wait(0.8)

        verdict = theme.body("one unit overflows and fills the other three", size=30,
                             color=theme.C_AI)
        theme.foot(verdict)
        self.play(FadeIn(verdict, run_time=0.8))
        self.wait(2.0)
        self.play(FadeOut(VGroup(units, hand, verdict), run_time=0.9))
