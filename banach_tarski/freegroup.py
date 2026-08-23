"""The free group F2, as words.

Internal spelling: ``a`` and ``b`` are the generators, ``A`` and ``B`` their
inverses.  So the word the script writes ``a b b a⁻¹`` is ``"abbA"`` here.
Nothing in this module knows about drawing; ``theme.word_glyph`` handles the
rendering of a word into ``a b b a⁻¹``.
"""

from __future__ import annotations

import itertools

GENERATORS = ("a", "A", "b", "B")


def inverse_letter(letter: str) -> str:
    return letter.lower() if letter.isupper() else letter.upper()


def inverse(word: str) -> str:
    return "".join(inverse_letter(c) for c in reversed(word))


def reduce(word: str) -> str:
    """Delete every adjacent pair ``x x⁻¹``, repeatedly, until nothing cancels.

    This is the one and only rule of the game.
    """
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == inverse_letter(letter):
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def reduction_steps(word: str) -> list[tuple[str, int]]:
    """Every intermediate state of the reduction, with the index that cancels.

    Returned as ``[(word_before, index_of_first_letter_of_the_pair), ...]``
    ending with ``(reduced_word, -1)`` — exactly what the cancellation
    animation needs in order to collide one pair at a time.
    """
    steps: list[tuple[str, int]] = []
    current = word
    while True:
        for i in range(len(current) - 1):
            if current[i] == inverse_letter(current[i + 1]):
                steps.append((current, i))
                current = current[:i] + current[i + 2 :]
                break
        else:
            steps.append((current, -1))
            return steps


def is_reduced(word: str) -> bool:
    return all(
        word[i] != inverse_letter(word[i + 1]) for i in range(len(word) - 1)
    )


def words(max_length: int, include_empty: bool = True):
    """All reduced words of length <= ``max_length``, shortlex order."""
    if include_empty:
        yield ""
    frontier = [""]
    for _ in range(max_length):
        nxt = []
        for w in frontier:
            for g in GENERATORS:
                if w and g == inverse_letter(w[-1]):
                    continue
                nxt.append(w + g)
        yield from nxt
        frontier = nxt


def words_starting_with(letter: str, max_length: int):
    """S(x): the reduced words whose first letter is ``x``."""
    for w in words(max_length, include_empty=False):
        if w[0] == letter:
            yield w


def columns(max_length: int = 4) -> dict[str, list[str]]:
    """The five piles of scene 6: one per first letter, plus the empty word."""
    piles: dict[str, list[str]] = {g: [] for g in GENERATORS}
    piles[""] = [""]
    for w in words(max_length, include_empty=False):
        piles[w[0]].append(w)
    return piles


def shift(word: str, letter: str) -> str:
    """Left-multiply and reduce: what the librarian's push does to one book."""
    return reduce(letter + word)


def sample_words(count: int, min_length: int = 1, max_length: int = 6, seed: int = 0):
    """A deterministic scatter of words, for shelves and background dust."""
    import random

    rng = random.Random(seed)
    pool = [w for w in words(max_length, include_empty=False) if len(w) >= min_length]
    rng.shuffle(pool)
    return list(itertools.islice(itertools.cycle(pool), count))
