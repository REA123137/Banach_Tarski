"""The two rotations, and the orbits they generate.

θ = arccos(1/3).  A turns about the z axis, B about the x axis.  The pair
generates a free group of rank two — that is the one result of the script we
state rather than prove, and it is what lets every word of ``freegroup`` act
on a genuine point of the sphere.
"""

from __future__ import annotations

import numpy as np

from .freegroup import inverse_letter, reduce, words

COS_THETA = 1.0 / 3.0
SIN_THETA = float(np.sqrt(8.0)) / 3.0
THETA = float(np.arccos(COS_THETA))  # ≈ 1.230959 rad ≈ 70.53°


def rotation_z(angle: float) -> np.ndarray:
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def rotation_x(angle: float) -> np.ndarray:
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def rotation_about(axis: np.ndarray, angle: float) -> np.ndarray:
    """Rodrigues.  Used for the new axis of the poles scene."""
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    K = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)


A = rotation_z(THETA)
B = rotation_x(THETA)

MATRICES = {
    "a": A,
    "A": A.T,   # orthogonal: the transpose is the inverse, exactly
    "b": B,
    "B": B.T,
}


def word_matrix(word: str) -> np.ndarray:
    """The matrix product of a word, read left to right as the script does."""
    m = np.eye(3)
    for letter in word:
        m = m @ MATRICES[letter]
    return m


def act(word: str, point: np.ndarray) -> np.ndarray:
    return word_matrix(word) @ np.asarray(point, dtype=float)


# --------------------------------------------------------------------------
# Orbits
# --------------------------------------------------------------------------

def orbit(point, max_length: int = 7, include_words: bool = True):
    """Every place ``point`` can be sent by a word of length <= max_length.

    Returns ``(points (N,3), words list)``.  The dust of scene 9.
    """
    p = np.asarray(point, dtype=float)
    pts, wds = [], []
    for w in words(max_length):
        pts.append(word_matrix(w) @ p)
        if include_words:
            wds.append(w)
    return np.array(pts), wds


def orbit_first_letters(max_length: int = 7) -> list[str]:
    """The first letter of every word of the orbit enumeration, in the same order."""
    return [w[0] if w else "" for w in words(max_length)]


def many_orbits(count: int, max_length: int = 5, seed: int = 3):
    """``count`` orbits of random seed points — the sphere divided into dust.

    Returns a list of ``(representative (3,), points (N,3), first_letters)``.
    """
    rng = np.random.default_rng(seed)
    letters = orbit_first_letters(max_length)
    out = []
    for _ in range(count):
        v = rng.normal(size=3)
        v /= np.linalg.norm(v)
        pts, _ = orbit(v, max_length)
        out.append((v, pts, letters))
    return out


# --------------------------------------------------------------------------
# Fixed points
# --------------------------------------------------------------------------

def axis_of(word: str) -> np.ndarray | None:
    """The rotation axis of a word: the eigenvector of eigenvalue 1.

    The two points where it pierces the sphere are the fixed points that
    scene 10 has to set aside.
    """
    m = word_matrix(word)
    if np.allclose(m, np.eye(3)):
        return None
    vals, vecs = np.linalg.eig(m)
    idx = int(np.argmin(np.abs(vals - 1.0)))
    axis = np.real(vecs[:, idx])
    n = np.linalg.norm(axis)
    if n < 1e-9:
        return None
    return axis / n


def fixed_point_axes(max_length: int = 3) -> list[np.ndarray]:
    """A finite sample of D: the axes of the shortest non-trivial words."""
    seen: list[np.ndarray] = []
    for w in words(max_length, include_empty=False):
        ax = axis_of(reduce(w))
        if ax is None:
            continue
        if not any(
            np.allclose(ax, s, atol=1e-6) or np.allclose(ax, -s, atol=1e-6) for s in seen
        ):
            seen.append(ax)
    return seen


def free_axis(seed: int = 11) -> np.ndarray:
    """An axis avoiding every forbidden one — the dart that misses the pinpricks."""
    forbidden = fixed_point_axes(4)
    rng = np.random.default_rng(seed)
    while True:
        v = rng.normal(size=3)
        v /= np.linalg.norm(v)
        if all(abs(float(v @ f)) < 0.97 for f in forbidden):
            return v


# --------------------------------------------------------------------------
# Sanity: the group really is free, as far as we can enumerate
# --------------------------------------------------------------------------

def check_freeness(max_length: int = 5, tol: float = 1e-7) -> bool:
    """No non-empty reduced word acts as the identity, up to ``max_length``."""
    for w in words(max_length, include_empty=False):
        if np.allclose(word_matrix(w), np.eye(3), atol=tol):
            return False
    return True


def check_inverses(tol: float = 1e-12) -> bool:
    for g in "ab":
        if not np.allclose(MATRICES[g] @ MATRICES[inverse_letter(g)], np.eye(3), atol=tol):
            return False
    return True
