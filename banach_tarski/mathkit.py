"""
The mathematics the film actually animates.

Free group words, the Cayley tree layout, the two rotations of the sphere that
generate a free group, orbit sampling, and a few geometry helpers.  Kept apart
from the scenes so the pictures and the proof stay honest about each other.
"""

from __future__ import annotations

import numpy as np

# Generators are written with a single character each:
#   'a' = a      'A' = a inverse      'b' = b      'B' = b inverse
GENS = ("a", "A", "b", "B")
PRETTY = {"a": "a", "A": "a⁻¹", "b": "b", "B": "b⁻¹"}


def inv(letter: str) -> str:
    return letter.swapcase()


def reduce_word(w: str) -> str:
    """Free reduction: delete every adjacent ``x x^-1`` pair, repeatedly."""
    out: list[str] = []
    for ch in w:
        if out and out[-1] == inv(ch):
            out.pop()
        else:
            out.append(ch)
    return "".join(out)


def multiply(*words: str) -> str:
    return reduce_word("".join(words))


def words_of_length(n: int) -> list[str]:
    """Every reduced word of length exactly ``n`` (there are 4*3^(n-1))."""
    if n == 0:
        return [""]
    out = []
    for w in words_of_length(n - 1):
        for g in GENS:
            if w and g == inv(w[-1]):
                continue
            out.append(w + g)
    return out


def words_up_to(n: int) -> list[str]:
    return [w for k in range(n + 1) for w in words_of_length(k)]


def first_letter(w: str) -> str | None:
    """Which of the four halves S(a), S(a^-1), S(b), S(b^-1) a word lives in."""
    return w[0] if w else None


def pretty(w: str) -> str:
    return "".join(PRETTY[c] for c in w) if w else "e"


# --------------------------------------------------------------------------
# Cayley tree layout.
# --------------------------------------------------------------------------

TREE_DIRS = {
    "a": np.array([1.0, 0.0, 0.0]),
    "A": np.array([-1.0, 0.0, 0.0]),
    "b": np.array([0.0, 1.0, 0.0]),
    "B": np.array([0.0, -1.0, 0.0]),
}


def cayley_tree(depth: int = 6, root=np.zeros(3), length: float = 2.5,
                shrink: float = 0.47) -> tuple[dict[str, np.ndarray], list[tuple[str, str]]]:
    """
    Positions for every reduced word up to ``depth``, laid out as the classic
    self-similar picture of the 4-regular tree, plus the parent/child edges.
    """
    pos: dict[str, np.ndarray] = {"": np.array(root, dtype=float)}
    edges: list[tuple[str, str]] = []
    frontier = [""]
    for d in range(depth):
        step = length * shrink**d
        nxt = []
        for w in frontier:
            for g in GENS:
                if w and g == inv(w[-1]):
                    continue
                child = w + g
                pos[child] = pos[w] + TREE_DIRS[g] * step
                edges.append((w, child))
                nxt.append(child)
        frontier = nxt
    return pos, edges


# --------------------------------------------------------------------------
# A free group of rotations inside SO(3).
#
# The classic pair: rotate by arccos(1/3) about the x-axis and about the
# z-axis.  No non-trivial reduced word in these two is the identity, so the
# group they generate is free of rank two - which is the whole engine of the
# paradox.
# --------------------------------------------------------------------------

_C = 1.0 / 3.0
_S = 2.0 * np.sqrt(2.0) / 3.0
THETA = float(np.arccos(_C))  # ~70.53 degrees

R_a = np.array([[1, 0, 0], [0, _C, -_S], [0, _S, _C]], dtype=float)
R_b = np.array([[_C, -_S, 0], [_S, _C, 0], [0, 0, 1]], dtype=float)
ROT = {"a": R_a, "A": R_a.T, "b": R_b, "B": R_b.T}


def apply_word(w: str, v: np.ndarray) -> np.ndarray:
    """Act on a vector by the rotation the word names (rightmost acts first)."""
    out = np.array(v, dtype=float)
    for ch in reversed(w):
        out = ROT[ch] @ out
    return out


def orbit(seed: np.ndarray, depth: int = 6):
    """
    Sample one orbit of the free group on the sphere.

    Yields ``(point, half)`` where ``half`` is the first letter of the word -
    the piece of the paradoxical decomposition that point belongs to.
    """
    for w in words_up_to(depth):
        yield apply_word(w, seed), first_letter(w), w


def random_sphere(n: int, radius: float = 1.0, seed: int = 0) -> np.ndarray:
    """
    Uniform random points on S^2.

    Deliberately random rather than an even lattice: a lattice is beautiful on
    paper and turns into moire banding once it is spinning on screen.
    """
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, 3))
    return radius * v / np.linalg.norm(v, axis=1, keepdims=True)


def ball_points(n: int, radius: float = 1.0, seed: int = 3) -> np.ndarray:
    """Uniform points in the solid ball, for the radial-extension scene."""
    rng = np.random.default_rng(seed)
    dirs = rng.normal(size=(n, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    r = radius * rng.random(n) ** (1 / 3)
    return dirs * r[:, None]
