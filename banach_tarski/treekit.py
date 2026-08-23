"""
Drawing the Cayley graph of the free group on two generators.

The tree is the picture the whole proof runs on, so it gets its own module:
one layout, reused by the scene that builds it and by the scene that breaks it
into four pieces and puts two copies back together.

Edges are batched into a handful of multi-path VMobjects rather than one
mobject per edge - at depth five that is the difference between a few hundred
mobjects and five.
"""

from __future__ import annotations

import numpy as np
from manim import *

from . import mathkit as mk
from .style import C_A, C_AI, C_B, C_BI, C_ID, FAINT, PAPER
from .particles import Dust

BRANCH_COLORS = {"a": C_A, "A": C_AI, "b": C_B, "B": C_BI, None: C_ID}


class TreeLayout:
    """Positions, indices and colours for every reduced word up to ``depth``."""

    def __init__(self, depth: int = 5, length: float = 2.6, shrink: float = 0.47,
                 center=ORIGIN, y_scale: float = 1.0):
        """
        ``y_scale`` squashes the vertical generators.  The tree is as tall as it
        is wide, and a 16:9 frame is not, so a little squash is what keeps the
        b-branches on screen without shrinking the whole picture.
        """
        self.depth = depth
        self.pos, self.edges = mk.cayley_tree(depth, root=np.zeros(3),
                                              length=length, shrink=shrink)
        squash = np.array([1.0, y_scale, 1.0])
        for w in self.pos:
            self.pos[w] = self.pos[w] * squash + np.asarray(center, dtype=float)
        self.words = sorted(self.pos.keys(), key=lambda w: (len(w), w))
        self.index = {w: i for i, w in enumerate(self.words)}
        self.points = np.array([self.pos[w] for w in self.words])
        self.branch = [mk.first_letter(w) for w in self.words]

    # -- queries -----------------------------------------------------------
    def half(self, letter: str) -> np.ndarray:
        """Boolean mask for S(letter): every word starting with that letter."""
        return np.array([b == letter for b in self.branch])

    def mask(self, predicate) -> np.ndarray:
        return np.array([bool(predicate(w)) for w in self.words])

    def colors(self, palette: dict | None = None) -> list[str]:
        palette = palette or BRANCH_COLORS
        return [palette[b] for b in self.branch]

    # -- mobjects ----------------------------------------------------------
    def edge_layers(self, width: float = 1.6, opacity: float = 0.85,
                    palette: dict | None = None) -> list[VMobject]:
        """One VMobject per depth, so the tree can be grown ring by ring."""
        palette = palette or BRANCH_COLORS
        layers = []
        for d in range(1, self.depth + 1):
            group = VGroup()
            for letter, color in ((g, palette[g]) for g in mk.GENS):
                m = VMobject()
                drawn = False
                for u, v in self.edges:
                    if len(v) != d or mk.first_letter(v) != letter:
                        continue
                    m.start_new_path(self.pos[u])
                    m.add_line_to(self.pos[v])
                    drawn = True
                if drawn:
                    m.set_stroke(color, width * (0.62**(d - 1)) + 0.35,
                                 opacity=opacity)
                    group.add(m)
            layers.append(group)
        return layers

    def edges_where(self, predicate, color: str, width: float = 1.8,
                    opacity: float = 0.9) -> VMobject:
        """
        One VMobject holding every edge whose child word satisfies ``predicate``.

        Batching keeps a five-deep tree at a handful of mobjects instead of
        several hundred, which is what makes it animatable at all.
        """
        m = VMobject()
        drawn = False
        for u, v in self.edges:
            if not predicate(v):
                continue
            m.start_new_path(self.pos[u])
            m.add_line_to(self.pos[v])
            drawn = True
        if not drawn:
            return VMobject()
        m.set_stroke(color, width, opacity=opacity)
        return m

    def node_cloud(self, size: float = 3.0, palette: dict | None = None) -> Dust:
        return Dust(self.points, self.colors(palette), size=size)

    def cloud(self, mask=None, size: float = 3.0, palette: dict | None = None) -> Dust:
        """Dust for a chosen subset of the vertices."""
        if mask is None:
            return self.node_cloud(size=size, palette=palette)
        mask = np.asarray(mask)
        colors = [c for c, keep in zip(self.colors(palette), mask) if keep]
        return Dust(self.points[mask], colors, size=size)

    def depth_mask(self, d: int) -> np.ndarray:
        return np.array([len(w) == d for w in self.words])


    def word_label(self, w: str, size: float = 20, color: str = PAPER,
                   direction=UP, buff: float = 0.16):
        from .style import M

        lab = M(mk.pretty(w), size=size, color=color)
        lab.move_to(self.pos[w] + np.asarray(direction) * buff)
        return lab
