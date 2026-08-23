"""Check, by computation, everything the film asserts on screen.

The script's rule is that no claim is staged.  This module is the receipt:
run ``make check`` (or ``python3 -m banach_tarski.selfcheck``) and every
statement the animation makes about the free group, the angle, the sorting and
the closing circle is verified over a finite but generous range.

A failure here means a scene is now telling the viewer something untrue.
"""

from __future__ import annotations

import numpy as np

from . import freegroup as fg
from .rotations import (
    MATRICES,
    THETA,
    check_freeness,
    check_inverses,
    fixed_point_axes,
    free_axis,
    orbit,
    word_matrix,
)


def check_reduction(max_length: int = 6) -> str:
    """Reducing a word never changes the motion it names."""
    for w in fg.words(max_length, include_empty=False):
        scrambled = w + fg.inverse(w[-1]) + w[-1]
        assert fg.reduce(scrambled) == w, scrambled
        assert np.allclose(word_matrix(scrambled), word_matrix(w), atol=1e-9)
        assert fg.is_reduced(fg.reduce(scrambled))
    return f"reduction agrees with the matrices, up to length {max_length}"


def check_free_group(max_length: int = 6) -> str:
    """No non-empty reduced word is the identity: the group really is free."""
    assert check_inverses(), "a generator and its inverse are not inverse"
    assert check_freeness(max_length), "a word of the catalogue does nothing"
    return f"no word up to length {max_length} brings the sphere back (θ = {np.degrees(THETA):.3f}°)"


def check_gate_invariant(max_length: int = 7) -> str:
    """Scene 8: the number at the gate is never divisible by three."""
    tested = 0
    for w in fg.words(max_length, include_empty=False):
        if w[-1] not in ("a", "A"):
            continue
        image = word_matrix(w) @ np.array([1.0, 0.0, 0.0])
        b = image[1] * (3.0 ** len(w)) / np.sqrt(2.0)
        assert abs(b - round(b)) < 1e-6, (w, b)
        assert round(b) % 3 != 0, (w, round(b))
        tested += 1
    return f"the gate refused all {tested} numbers, up to length {max_length}"


def check_doubling(max_length: int = 5) -> str:
    """Scene 6: a·S(a⁻¹) is exactly {e} ⊔ S(a⁻¹) ⊔ S(b) ⊔ S(b⁻¹)."""
    for generator in ("a", "b"):
        source = fg.inverse_letter(generator)
        shifted = {
            fg.reduce(generator + w)
            for w in fg.words_starting_with(source, max_length)
            if len(w) <= max_length
        }
        expected = {
            w
            for w in fg.words(max_length - 1)
            if not w or w[0] != generator
        }
        missing = expected - shifted
        assert not missing, (generator, sorted(missing)[:5])
        # and the two untouched piles complete the catalogue
        union = shifted | set(fg.words_starting_with(generator, max_length - 1))
        assert union >= set(fg.words(max_length - 1)), generator
    return f"both doublings cover the catalogue, up to length {max_length - 1}"


def check_orbit_closure(max_length: int = 5) -> str:
    """Scene 11: rotating the batch P₂ lands its points on points of the orbit."""
    seed = np.array([0.37, -0.52, 0.77])
    seed /= np.linalg.norm(seed)
    pts, words = orbit(seed, max_length=max_length)
    index = {w: i for i, w in enumerate(words)}
    moved = 0
    for i, w in enumerate(words):
        if not w or w[0] != "A":
            continue
        landed = fg.reduce("a" + w)
        assert landed in index, landed
        image = MATRICES["a"] @ pts[i]
        assert np.allclose(image, pts[index[landed]], atol=1e-9), w
        moved += 1
    return f"all {moved} points of P₂ land exactly on their computed images"


def check_circle_queue(count: int = 4000) -> str:
    """Scene 12: one radian never closes up, so the queue never repeats."""
    angles = np.mod(np.arange(0, count + 1, dtype=float), 2 * np.pi)
    order = np.sort(angles)
    gap = np.min(np.diff(order))
    assert gap > 0, "the queue landed on itself"
    return f"the first {count} steps are all distinct (closest pair {gap:.2e} rad apart)"


def check_free_axis() -> str:
    """Scene 12: the new axis really does avoid every forbidden one."""
    axis = free_axis()
    forbidden = fixed_point_axes(4)
    worst = max(abs(float(axis @ f)) for f in forbidden)
    assert worst < 0.99, worst
    return f"the new axis misses {len(forbidden)} forbidden axes (closest cos {worst:.3f})"


def check_library_pages(draws=("a", "b", "ab", "ba", "aab", "abA", "bba", "aB", "bAb", "aaB")) -> str:
    """Scene 5: ten different spines, ten different pages."""
    seen: list[np.ndarray] = []
    for w in draws:
        m = word_matrix(w)
        for other in seen:
            assert not np.allclose(m, other, atol=1e-6), w
        seen.append(m)
    return f"{len(draws)} draws from the free library, never the same page twice"


CHECKS = (
    check_reduction,
    check_free_group,
    check_gate_invariant,
    check_doubling,
    check_orbit_closure,
    check_circle_queue,
    check_free_axis,
    check_library_pages,
)


def main() -> int:
    width = max(len(c.__name__) for c in CHECKS)
    failed = 0
    for check in CHECKS:
        try:
            note = check()
        except AssertionError as exc:  # pragma: no cover - the point is that it never fires
            failed += 1
            print(f"FAIL  {check.__name__:<{width}}  {exc}")
        else:
            print(f"ok    {check.__name__:<{width}}  {note}")
    if failed:
        print(f"\n{failed} check(s) failed — a scene is asserting something untrue.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
