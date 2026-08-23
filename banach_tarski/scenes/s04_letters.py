"""Scene 4 — 03:15-04:35 · The rules of the game: a motion is a letter.

    "ANIMATION – A Rubik's cube.  One face turns, then another.  Underneath the
    cube, the moves write themselves side by side like a word growing longer."

    "ANIMATION – Two curved arrows around a sphere: one rotation labelled a,
    another labelled b, about two different axes."

    "ANIMATION – The word abba⁻¹a appears, then a⁻¹ and a fade out, leaving abb."

    "ANIMATION IDEA – The cube unfolds into a ribbon. […] A letter cancelling
    its inverse is staged as a particle collision: the two letters slam
    together, one brief white flash, nothing left."
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

from banach_tarski import anim, freegroup, motifs, space, theme

MOVES = ["a", "b", "b", "A"]  # the script's example: a, b, b, a backwards


class S04RubikWord(Scene):
    """You have already done this without noticing, with a Rubik's cube."""

    def construct(self):
        theme.apply_defaults(self)

        cube = motifs.rubik_cube(cell=0.62)
        cube.move_to(UP * 0.9)
        self.play(FadeIn(cube, run_time=0.9))
        self.wait(0.4)

        caption = theme.caption("the sequence of moves you performed can be written down", size=26)
        caption.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(caption, run_time=0.6))

        word = VGroup()
        anchor = DOWN * 1.5
        for i, letter in enumerate(MOVES):
            turn = -PI / 2 if letter.islower() else PI / 2
            face = cube.front if letter.lower() == "a" else cube.top
            self.play(motifs.turn_face(cube, face, turn, run_time=0.85))
            tile = theme.mono(theme.letter_glyph(letter), size=44,
                              color=theme.LETTER_COLORS[letter])
            word.add(tile)
            word.arrange(RIGHT, buff=0.24).move_to(anchor)
            self.play(FadeIn(tile, shift=UP * 0.18, run_time=0.35))

        label = theme.body("that is a word", size=30, color=theme.INK_DIM)
        label.next_to(word, DOWN, buff=0.45)
        self.play(FadeIn(label, run_time=0.7))
        self.wait(1.6)
        self.play(FadeOut(VGroup(cube, word, label, caption), run_time=0.8))


class S04TwoRotations(Scene):
    """Two moves only, and they are given letters for names."""

    def construct(self):
        theme.apply_defaults(self)

        stage = space.Stage(space.View(yaw=-0.75, pitch=0.30, scale=2.2))
        shell = space.sphere_cloud(9000, color="#565248", size=2.1, size_far=0.8)
        stage.add(shell)
        for wire in space.wire_sphere(1.0, 10, 5, color="#1F1F1F", width=1.0):
            stage.add(wire)

        # a turns about the vertical axis, b about a horizontal one
        arrows = {}
        for letter, normal, colour in (
            ("a", [0.0, 0.0, 1.0], theme.C_A),
            ("b", [1.0, 0.0, 0.0], theme.C_B),
        ):
            path = space.arc_points(normal, 0.35, 0.35 + 3.2, radius=1.28)
            arrow = space.TipWire(path, color=colour, width=3.2, tip_size=0.20)
            stage.add(arrow)
            arrows[letter] = arrow
            axis = space.Wire(
                space.axis_segment(normal, 1.55), color=colour, width=1.4, closed=False
            )
            axis.mobject.set_stroke(opacity=0.35)
            stage.add(axis)

        stage.install(self)
        stage.spin(self, speed=0.10)

        tags = VGroup()
        for letter, colour, side in (("a", theme.C_A, LEFT), ("b", theme.C_B, RIGHT)):
            tag = theme.mono(letter, size=52, color=colour)
            tag.move_to(side * 4.6 + UP * 1.4)
            tags.add(tag)
        self.play(FadeIn(tags, run_time=0.9))
        self.wait(2.0)

        inverses = VGroup(
            theme.mono("a⁻¹", size=44, color=theme.C_AI).move_to(LEFT * 4.6 + UP * 0.35),
            theme.mono("b⁻¹", size=44, color=theme.C_BI).move_to(RIGHT * 4.6 + UP * 0.35),
        )
        note = theme.caption("turning the other way undoes what you just did", size=24)
        note.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(inverses, run_time=0.8), FadeIn(note, run_time=0.8))
        self.wait(2.4)


class S04Reduce(Scene):
    """The one rule of the game: a letter cancels its neighbour."""

    def construct(self):
        theme.apply_defaults(self)

        rule = theme.formula("a a⁻¹  =  e", size=54)
        gloss = theme.caption("e is the empty word: doing nothing", size=26)
        head = VGroup(rule, gloss).arrange(DOWN, buff=0.35).to_edge(UP, buff=1.0)
        self.play(Write(rule, run_time=1.0), FadeIn(gloss, run_time=0.8))
        self.wait(0.8)

        word = "abbAa"
        letters = theme.word_mobject(word, size=64, spaced=True)
        letters.move_to(DOWN * 0.2)
        self.play(FadeIn(letters, lag_ratio=0.15, run_time=1.2))
        self.wait(0.8)

        # play the reduction exactly as freegroup.reduction_steps computes it
        steps = freegroup.reduction_steps(word)
        current = letters
        for _, index in steps:
            if index < 0:
                break
            current = anim.cancel_in_word(self, current, index, reflow_to=DOWN * 0.2, buff=0.42)
            self.wait(0.35)

        verdict = theme.body("reduced — nothing can cancel any more", size=30, color=theme.INK_DIM)
        verdict.next_to(current, DOWN, buff=0.8)
        self.play(FadeIn(verdict, shift=UP * 0.15, run_time=0.8))
        self.wait(1.8)
        self.play(FadeOut(VGroup(head, current, verdict), run_time=0.8))


class S04Ribbon(Scene):
    """ANIMATION IDEA — the cube unfolds into a ribbon.

        "The Rubik's cube turns, then its faces unroll into a paper ribbon
        where the moves are printed as on a typewriter roll.  A letter
        cancelling its inverse is staged as a particle collision. […] Sound
        matters here: a mechanical click per letter, a clean silence for the
        cancellation."

    The click track is cued by the tile-drop beats, which are deliberately
    even: one letter every 0.32 s.
    """

    def construct(self):
        theme.apply_defaults(self)

        cube = motifs.rubik_cube(cell=0.55)
        cube.move_to(UP * 1.6)
        self.play(FadeIn(cube, run_time=0.8))
        self.play(motifs.turn_face(cube, cube.front, -PI / 2, run_time=0.8))

        # the ribbon: a long pale strip the letters are printed on
        strip = theme.panel(12.4, 1.5, fill="#0E0E0E", stroke=theme.GHOST)
        strip.move_to(DOWN * 0.9)
        perfs = VGroup()
        for x in np.arange(-6.0, 6.01, 0.4):
            for y in (0.62, -0.62):
                perfs.add(
                    theme.rule(width=0.10, color=theme.GHOST, stroke=2.0).move_to(
                        strip.get_center() + np.array([x, y, 0])
                    )
                )
        self.play(Create(strip, run_time=0.9), FadeIn(perfs, run_time=0.7))
        self.play(cube.animate(run_time=1.1, rate_func=theme.EASE).scale(0.55).move_to(UP * 2.4))

        typed = "abbAab"
        tiles = VGroup()
        for i, letter in enumerate(typed):
            tile = theme.mono(theme.letter_glyph(letter), size=48,
                              color=theme.LETTER_COLORS[letter])
            tile.move_to(strip.get_center() + LEFT * 4.4 + RIGHT * 1.15 * i)
            tiles.add(tile)
            self.play(FadeIn(tile, shift=DOWN * 0.22, run_time=0.32, rate_func=theme.SNAP))

        self.wait(0.6)
        note = theme.caption("one mechanical click per letter — then a clean silence", size=24)
        note.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(note, run_time=0.6))

        # the collision: A and a annihilate, the ribbon closes up
        anim.annihilate(self, tiles[3], tiles[4])
        remaining = VGroup(*[t for i, t in enumerate(tiles) if i not in (3, 4)])
        target = remaining.copy().arrange(RIGHT, buff=0.55).move_to(strip.get_center())
        self.play(
            *[m.animate.move_to(t) for m, t in zip(remaining, target)],
            run_time=0.6,
            rate_func=theme.EASE,
        )
        self.wait(1.8)
        self.play(FadeOut(VGroup(cube, strip, perfs, remaining, note), run_time=0.8))
