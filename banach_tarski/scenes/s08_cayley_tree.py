"""
08 - The Cayley graph.

Every word in the free group becomes a vertex, and multiplying by a letter
becomes a step along an edge.  What comes out is an infinite four-way tree
that looks the same at every scale - and holds four copies of itself.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.treekit import TreeLayout, BRANCH_COLORS
from banach_tarski import mathkit as mk

DEPTH = 5


class CayleyTree(BTMovingScene):
    star_seed = 55

    def construct(self):
        self.chapter("06", "The Cayley graph", "the free group, drawn")

        tree = TreeLayout(depth=DEPTH, length=2.40, shrink=0.47,
                          center=UP * 0.45, y_scale=0.66)
        layers = tree.edge_layers(width=2.6, opacity=0.9)

        # -- the identity --------------------------------------------------------
        root = glow_dot(tree.pos[""], PAPER, radius=0.075, reach=5)
        root_lbl = M("e", size=SMALL, color=PAPER).next_to(root, DOWN, buff=0.22)
        self.play(FadeIn(root, scale=0.4), run_time=0.7)
        self.play(FadeIn(root_lbl, shift=UP * 0.1), run_time=0.4)
        self.say("A", "One dot for the empty word - do nothing at all.", hold=1.8)

        # -- first ring ----------------------------------------------------------
        first_nodes = tree.cloud(tree.depth_mask(1), size=7.0)
        labels = VGroup(*[
            tree.word_label(g, size=SMALL, color=BRANCH_COLORS[g],
                            direction=mk.TREE_DIRS[g] * np.array([1, 0.8, 1]) + UP * 0.35,
                            buff=0.40)
            for g in mk.GENS
        ])
        self.play(Create(layers[0], run_time=1.2, lag_ratio=0.1))
        self.play(FadeIn(first_nodes), LaggedStart(*[FadeIn(l, scale=0.7) for l in labels],
                                                   lag_ratio=0.12), run_time=1.0)
        self.say("B", "Four edges out of it, one for each letter. Walk an edge, "
                      "and you have multiplied by that letter.", hold=2.8)

        # -- grow ------------------------------------------------------------------
        self.play(FadeOut(labels), FadeOut(root_lbl), run_time=0.5)
        clouds = Group()   # Dust is a point cloud, not a VMobject
        for d in range(2, DEPTH + 1):
            nodes = tree.cloud(tree.depth_mask(d), size=max(6.5 * 0.72 ** (d - 1), 1.8))
            clouds.add(nodes)
            self.play(
                Create(layers[d - 1], run_time=1.15, lag_ratio=0.02),
                FadeIn(nodes, run_time=1.15),
            )
        self.say("A", "Every extra letter branches three more ways. Never back on "
                      "itself - that would just cancel.", hold=2.8)

        self.say("B", "No loops anywhere. That is exactly what free means, drawn: "
                      "one and only one path between any two words.", hold=3.0)

        # -- self-similarity --------------------------------------------------------
        frame = self.camera.frame
        target = tree.pos["a"]
        self.play(
            frame.animate.set(width=config.frame_width * 0.42).move_to(target),
            run_time=2.6, rate_func=Look.ease,
        )
        self.say("A", "Push in on any branch, and you find the whole tree again.",
                 hold=2.4)
        self.play(
            frame.animate.set(width=config.frame_width).move_to(ORIGIN),
            run_time=2.4, rate_func=Look.ease,
        )

        # -- the four halves ---------------------------------------------------------
        self.clear_caption()
        legend = VGroup()
        for g in mk.GENS:
            swatch = Square(side_length=0.22).set_fill(BRANCH_COLORS[g], opacity=1)
            swatch.set_stroke(width=0)
            txt = M("S(" + mk.PRETTY[g] + ")", size=TINY, color=PAPER)
            legend.add(VGroup(swatch, txt).arrange(RIGHT, buff=0.20))
        legend.arrange(RIGHT, buff=0.62).move_to(DOWN * 3.05).scale(0.95)
        box = panel(legend.width + 0.7, legend.height + 0.5)
        box.move_to(legend)
        legend_group = VGroup(box, legend)

        self.play(FadeIn(legend_group, shift=UP * 0.15), run_time=0.8)

        for g in mk.GENS:
            mask = tree.half(g)
            highlight = tree.cloud(mask, size=6.0)
            highlight.recolor(BRANCH_COLORS[g])
            self.play(FadeIn(highlight, run_time=0.5))
            self.wait(0.25)
            self.play(FadeOut(highlight, run_time=0.4))

        self.say("B", "Sort the words by their first letter, and the tree falls into "
                      "four pieces - plus the dot in the middle.", hold=3.0)

        split = T("F  =  {e}  " + SQCUP + "  S(a)  " + SQCUP + "  S(a" + INV + ")  "
                  + SQCUP + "  S(b)  " + SQCUP + "  S(b" + INV + ")",
                  size=SMALL, color=PAPER).move_to(UP * 3.35)
        self.play(FadeIn(split, shift=DOWN * 0.12), run_time=0.8)
        self.say("A", "Four pieces. Now watch what one rotation does to one of them.",
                 hold=2.6)

        self.play(*[FadeOut(m) for m in self.mobjects if m not in self._furniture],
                  run_time=1.0)
