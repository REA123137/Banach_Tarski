"""
09 - The paradox, in the group.

The load-bearing scene.  Split the free group by first letter, multiply one
piece by a single letter, and it swells to cover everything the other piece
misses.  Do it twice and one group has become two.

Nothing here is a metaphor: every vertex really does fly to the vertex naming
its product, and the targets are computed from the group law, not eyeballed.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustMorph, DustRecolor
from banach_tarski.treekit import TreeLayout, BRANCH_COLORS
from banach_tarski import mathkit as mk

DEPTH = 5
DARK = "#101216"


class ParadoxInTheGroup(BTScene):
    star_seed = 66

    def construct(self):
        self.chapter("07", "One group, two groups",
                     "the trick that the whole theorem rests on")

        tree = TreeLayout(depth=DEPTH, length=2.20, shrink=0.47,
                          center=UP * 0.10, y_scale=0.62)
        self.tree = tree

        ghost = tree.edges_where(lambda w: True, FAINT, width=1.2, opacity=0.35)
        halves = {g: tree.edges_where(lambda w, g=g: mk.first_letter(w) == g,
                                      BRANCH_COLORS[g], width=1.9, opacity=0.9)
                  for g in mk.GENS}
        nodes = tree.node_cloud(size=4.2)
        # Bookkeeping: which word each particle currently represents.
        self.current = list(tree.words)

        self.add(ghost)
        self.play(FadeIn(ghost, run_time=0.8),
                  LaggedStart(*[FadeIn(halves[g]) for g in mk.GENS],
                              lag_ratio=0.12, run_time=1.4),
                  FadeIn(nodes, run_time=1.2))
        self.say("A", "Here is the group again, sorted by first letter.", hold=2.0)

        board = self.equation_board()
        self.play(FadeIn(board, shift=UP * 0.15), run_time=0.7)

        # ---------------------------------------------------------------- copy 1
        self.say("B", "Take the piece whose words start with a-inverse.", hold=2.2)
        mask_A = tree.half("A")
        self.spotlight(nodes, halves, keep="A")
        self.wait(0.4)

        self.say("A", "Now multiply every one of them by a. One extra letter, "
                      "on the left.", hold=2.6)

        mult = M("a  ·  S(a" + INV + ")", size=H3, color=C_AI).move_to(DOWN * 2.30)
        self.play(FadeIn(mult, scale=1.2), run_time=0.6)

        self.play(FadeOut(halves["A"], run_time=0.7))
        self.apply_letter(nodes, "a", mask_A, stagger=0.45, run_time=2.8)

        # Everything that is not S(a) is now covered.
        rest = tree.edges_where(lambda w: mk.first_letter(w) != "a", C_AI,
                                width=1.9, opacity=0.85)
        self.play(FadeIn(rest, run_time=1.0))
        self.say("B", "Look where they landed. That one piece now covers the whole "
                      "tree - everything except the a-branch.", hold=3.0)

        self.play(FadeIn(halves["a"], run_time=0.8),
                  self.reveal(nodes, ["a"], moved=mask_A))
        eq1 = M("S(a)  " + CUP + "  a·S(a" + INV + ")   =   F", size=SMALL, color=PAPER)
        eq1.move_to(board[1][0])
        self.play(FadeOut(mult, run_time=0.4), Write(eq1, run_time=1.1))
        self.say("A", "Add the a-branch back, and two of our four pieces have "
                      "rebuilt the entire group.", hold=3.0)

        # ---------------------------------------------------------------- copy 2
        self.say("B", "Now do exactly the same with b.", hold=1.8)
        self.play(FadeOut(rest), FadeOut(halves["a"]), run_time=0.6)
        self.restore_positions(nodes)
        self.play(FadeIn(halves["A"]), run_time=0.4)

        mask_B = tree.half("B")
        self.spotlight(nodes, halves, keep="B")
        self.play(FadeOut(halves["B"], run_time=0.6))
        self.apply_letter(nodes, "b", mask_B, stagger=0.4, run_time=2.4)

        rest2 = tree.edges_where(lambda w: mk.first_letter(w) != "b", C_BI,
                                 width=1.9, opacity=0.85)
        self.play(FadeIn(rest2, run_time=0.9), FadeIn(halves["b"], run_time=0.9),
                  self.reveal(nodes, ["b"], moved=mask_B))
        eq2 = M("S(b)  " + CUP + "  b·S(b" + INV + ")   =   F", size=SMALL, color=PAPER)
        eq2.move_to(board[1][1])
        self.play(Write(eq2, run_time=1.1))
        self.say("A", "The other two pieces rebuild it as well.", hold=2.4)

        # ---------------------------------------------------------------- payoff
        # Both moves are now made at once, so the two rebuilt copies are sitting
        # on top of each other before they are pulled apart.
        self.clear_caption()
        self.play(FadeOut(rest2), FadeOut(halves["b"]), FadeOut(halves["a"]),
                  FadeOut(halves["A"]), run_time=0.7)
        self.say("B", "Make both moves at the same time, and the tree is now covered "
                      "twice over.", hold=2.4)
        self.apply_letter(nodes, "a", mask_A, run_time=2.2)
        self.play(DustRecolor(nodes, tree.colors(), run_time=0.8))
        self.play(FadeOut(ghost), run_time=0.6)

        self.say("A", "Two complete copies, from four pieces of one.", hold=2.2)
        self.split_in_two(nodes)

        note = T("the identity is the only leftover - and we know how to absorb one "
                 "extra point", size=TINY, color=MUTED).move_to(DOWN * 2.15)
        self.play(FadeIn(note), run_time=0.7)
        self.say("A", "One dot is left over in the middle: the empty word. "
                      "Hilbert's hotel already told us how to swallow that.", hold=3.2)
        self.say("B", "Cut a group into four pieces, move each piece by a single "
                      "rotation, and you have two of the group you started with.",
                 hold=3.2)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.2)

    # -- helpers --------------------------------------------------------------
    def equation_board(self) -> VGroup:
        """A quiet strip at the top where the two identities accumulate."""
        slots = VGroup(
            Rectangle(width=5.6, height=0.5).set_opacity(0),
            Rectangle(width=5.6, height=0.5).set_opacity(0),
        ).arrange(RIGHT, buff=0.4)
        head = T("what the pieces rebuild", size=14, color=FAINT)
        head.next_to(slots, UP, buff=0.14)
        VGroup(head, slots).move_to(UP * 3.35)
        return VGroup(head, slots)

    def spotlight(self, nodes: Dust, halves: dict, keep: str):
        """Dim every branch but one, in both the edges and the vertices."""
        tree = self.tree
        mask = tree.half(keep)
        rgba = np.array([
            ManimColor(BRANCH_COLORS[b] if b == keep else DARK).to_rgba()
            for b in tree.branch
        ])
        rgba[:, 3] = 1.0
        anims = [DustRecolor(nodes, [BRANCH_COLORS[b] if b == keep else DARK
                                     for b in tree.branch], run_time=0.9)]
        for g, m in halves.items():
            anims.append(m.animate.set_stroke(opacity=0.9 if g == keep else 0.12))
        self.play(*anims, run_time=0.9)
        return mask

    def reveal(self, nodes: Dust, branches, moved) -> Animation:
        """Bring the named branches back to full colour alongside the moved piece."""
        tree = self.tree
        colors = []
        for i, b in enumerate(tree.branch):
            if moved[i]:
                colors.append(BRANCH_COLORS[mk.first_letter(tree.words[i])])
            elif b in branches:
                colors.append(BRANCH_COLORS[b])
            else:
                colors.append(DARK)
        return DustRecolor(nodes, colors, run_time=1.0)

    def apply_letter(self, nodes: Dust, letter: str, mask, run_time: float = 2.4,
                     stagger: float = 0.4):
        """
        Left-multiply the selected vertices by ``letter`` and fly them there.

        Targets come from wherever each particle currently is - which is what
        lets the two moves be composed instead of only demonstrated one at a
        time.
        """
        tree = self.tree
        targets = nodes.pts.copy()
        moved = list(self.current)
        for i, keep in enumerate(mask):
            if not keep:
                continue
            image = mk.multiply(letter, self.current[i])
            if image in tree.pos:
                targets[i] = tree.pos[image]
                moved[i] = image
        self.play(DustMorph(nodes, targets, stagger=stagger, swirl=0.35,
                            run_time=run_time))
        self.current = moved

    def restore_positions(self, nodes: Dust):
        """Put every vertex back where its own word says it belongs."""
        tree = self.tree
        self.play(
            DustMorph(nodes, tree.points, stagger=0.3, run_time=1.4),
            DustRecolor(nodes, tree.colors(), run_time=1.4),
        )
        self.current = list(tree.words)

    def split_in_two(self, nodes: Dust):
        """
        Fly the two rebuilt copies apart.

        Particles carrying a word too deep to fit in the smaller copies fade
        out - the drawing is a finite window on an infinite tree, and this is
        where that shows.
        """
        tree = self.tree
        left = TreeLayout(depth=DEPTH - 1, length=1.30, shrink=0.47,
                          center=LEFT * 3.45 + UP * 0.55, y_scale=0.62)
        right = TreeLayout(depth=DEPTH - 1, length=1.30, shrink=0.47,
                           center=RIGHT * 3.45 + UP * 0.55, y_scale=0.62)

        targets = nodes.pts.copy()
        colors = []
        for i, w0 in enumerate(tree.words):
            u = self.current[i]
            first = mk.first_letter(w0)
            copy = left if first in ("a", "A") else (right if first in ("b", "B") else None)
            if copy is not None and u in copy.pos:
                targets[i] = copy.pos[u]
                colors.append(BRANCH_COLORS[first])
            else:
                colors.append(INK)

        self.play(DustMorph(nodes, targets, rgbas=colors, swirl=0.9, stagger=0.5,
                            run_time=3.0))

        lab_l = M("F", size=H2, color=C_A, weight=BOLD).move_to(LEFT * 3.45 + DOWN * 1.55)
        lab_r = M("F", size=H2, color=C_B, weight=BOLD).move_to(RIGHT * 3.45 + DOWN * 1.55)
        self.play(FadeIn(lab_l, scale=1.3), FadeIn(lab_r, scale=1.3), run_time=0.7)
