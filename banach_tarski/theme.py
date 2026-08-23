"""Visual identity for *Two Balls* — the Banach-Tarski film.

Everything in the film is drawn on pure black. The palette is deliberately
small: four letter colours (one per generator of the free group), one warm
off-white for prose, one red reserved exclusively for refusal, and a single
grey used for anything that is a ghost of something else.

No LaTeX is required anywhere: all mathematics is set in Unicode with the
helpers below, so the project renders on a bare machine.
"""

from __future__ import annotations

import subprocess
from functools import lru_cache

from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Dot,
    Line,
    MarkupText,
    Mobject,
    Rectangle,
    Text,
    VGroup,
    VMobject,
    config,
    rate_functions,
)

# --------------------------------------------------------------------------
# Colours
# --------------------------------------------------------------------------

BG = "#000000"

INK = "#F2EFE9"        # prose, the colour of the spoken word
INK_DIM = "#8C8880"    # secondary prose, captions, units
GHOST = "#2E2E2E"      # wireframes, guides, the ball that is no longer there
GHOST_SOFT = "#1A1A1A"

# One colour per generator.  These four are the spine of the whole film:
# a word, a book, a column, a batch of points and a piece of the ball all wear
# the colour of their first letter.
C_A = "#FF6B5A"        # a
C_AI = "#FFC24B"       # a^-1
C_B = "#4FD1C5"        # b
C_BI = "#8B7BFF"       # b^-1
C_E = "#F2EFE9"        # the empty word, the representatives

LETTER_COLORS = {"a": C_A, "A": C_AI, "b": C_B, "B": C_BI, "": C_E}

REFUSE = "#FF3B30"     # struck-through counter-examples, and nothing else
GOLD = "#E8B84B"       # the theorem, the payoff
CHOICE = "#BFD7FF"     # the axiom of choice: cold, translucent, unreal
CHOCO = "#7A4A2B"
CHOCO_LIGHT = "#A9683C"

# --------------------------------------------------------------------------
# Type
# --------------------------------------------------------------------------

_FONT_WISHLIST = {
    "display": ("Inter Display", "Inter", "Lato", "DejaVu Sans"),
    "body": ("Inter", "Lato", "DejaVu Sans"),
    "mono": ("DejaVu Sans Mono", "Liberation Mono", "monospace"),
    "serif": ("EB Garamond", "Bitstream Charter", "DejaVu Serif"),
}


@lru_cache(maxsize=1)
def _installed_families() -> frozenset[str]:
    try:
        out = subprocess.run(
            ["fc-list", ":", "family"], capture_output=True, text=True, timeout=10
        ).stdout
    except Exception:  # pragma: no cover - fontconfig missing
        return frozenset()
    families = set()
    for line in out.splitlines():
        for name in line.split(","):
            families.add(name.strip())
    return frozenset(families)


@lru_cache(maxsize=8)
def font(role: str = "body") -> str:
    """Best available family for a role, degrading to DejaVu Sans."""
    installed = _installed_families()
    for candidate in _FONT_WISHLIST[role]:
        if not installed or candidate in installed:
            return candidate
    return "DejaVu Sans"


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def body(text: str, size: float = 34, color: str = INK, **kwargs) -> Text:
    return Text(text, font=font("body"), font_size=size, color=color, **kwargs)


def display(text: str, size: float = 62, color: str = INK, **kwargs) -> Text:
    return Text(
        text, font=font("display"), font_size=size, color=color, weight="MEDIUM", **kwargs
    )


def mono(text: str, size: float = 38, color: str = INK, **kwargs) -> Text:
    return Text(text, font=font("mono"), font_size=size, color=color, **kwargs)


def serif(text: str, size: float = 34, color: str = INK, **kwargs) -> Text:
    return Text(text, font=font("serif"), font_size=size, color=color, **kwargs)


def rich(markup: str, size: float = 34, color: str = INK, **kwargs) -> MarkupText:
    """Pango markup — used whenever one line needs several colours."""
    return MarkupText(markup, font=font("body"), font_size=size, color=color, **kwargs)


def formula(text: str, size: float = 44, color: str = INK, **kwargs) -> Text:
    """A display formula.  Unicode only, set in the body face at a wider tracking."""
    return Text(
        text, font=font("body"), font_size=size, color=color, **kwargs
    )


def caption(text: str, size: float = 24, color: str = INK_DIM) -> Text:
    return Text(text, font=font("body"), font_size=size, color=color)


def scene_label(index: int, title: str) -> VGroup:
    """The discreet running head every scene carries in the top left corner."""
    num = Text(f"{index:02d}", font=font("mono"), font_size=20, color=GHOST)
    name = Text(title.upper(), font=font("body"), font_size=20, color=INK_DIM)
    name.set_opacity(0.55)
    group = VGroup(num, name).arrange(RIGHT, buff=0.28)
    group.to_corner(UP + LEFT, buff=0.5)
    return group


# --------------------------------------------------------------------------
# Word typography
# --------------------------------------------------------------------------

SUP_INV = "⁻¹"  # superscript -1


def letter_glyph(letter: str) -> str:
    """'A' -> 'a⁻¹', 'a' -> 'a'."""
    if letter == "":
        return "e"
    return letter.lower() + (SUP_INV if letter.isupper() else "")


def word_glyph(word: str) -> str:
    return "".join(letter_glyph(c) for c in word) if word else "e"


def word_mobject(
    word: str,
    size: float = 38,
    color: str | None = None,
    face: str = "mono",
    spaced: bool = False,
) -> VGroup:
    """A word of F2 as a row of individually addressable letter mobjects.

    Returned as a ``VGroup`` so that a single letter can be faded, flashed or
    made to collide with its neighbour — which is what most of the film does.
    """
    maker = {"mono": mono, "body": body, "serif": serif}[face]
    if not word:
        glyph = maker("e", size=size, color=color or C_E)
        return VGroup(glyph)
    letters = VGroup(
        *[maker(letter_glyph(c), size=size, color=color or LETTER_COLORS[c]) for c in word]
    )
    letters.arrange(RIGHT, buff=size * (0.010 if not spaced else 0.006) + (0.10 if spaced else 0.02))
    return letters


# --------------------------------------------------------------------------
# Furniture
# --------------------------------------------------------------------------

def rule(width: float = 6.0, color: str = GHOST, stroke: float = 1.5) -> Line:
    return Line(LEFT * width / 2, RIGHT * width / 2, color=color, stroke_width=stroke)


def panel(width: float, height: float, fill: str = GHOST_SOFT, stroke: str = GHOST) -> Rectangle:
    return Rectangle(
        width=width,
        height=height,
        fill_color=fill,
        fill_opacity=1.0,
        stroke_color=stroke,
        stroke_width=1.6,
    )


def glow(mob: Mobject, color: str, layers: int = 6, spread: float = 6.0, opacity: float = 0.055):
    """A cheap bloom: concentric copies of a stroke, each fainter and fatter.

    Used sparingly — on the two balls, on the closing circle, on the theorem.
    """
    halo = VGroup()
    for i in range(layers):
        ring = mob.copy()
        if isinstance(ring, VMobject):
            ring.set_fill(opacity=0)
            ring.set_stroke(color=color, width=(i + 1) * spread, opacity=opacity)
        halo.add(ring)
    return halo


def vignette(strength: float = 0.55) -> VGroup:
    """Four soft black bands that keep the eye in the middle of the frame."""
    bands = VGroup()
    w, h = config.frame_width, config.frame_height
    for direction, size in ((UP, h), (DOWN, h), (LEFT, w), (RIGHT, w)):
        for i in range(8):
            t = i / 8
            band = Rectangle(
                width=w if direction[1] else w * 0.14,
                height=h if direction[0] else h * 0.14,
                fill_color=BLACK,
                fill_opacity=strength / 8 * (1 - t),
                stroke_width=0,
            )
            band.move_to(ORIGIN).shift(direction * (0.5 * (h if direction[1] else w) * (0.5 + 0.06 * i)))
            bands.add(band)
    return bands


def star_field(n: int = 90, seed: int = 7) -> VGroup:
    """A faint dust of dots.  The film's black is never quite empty."""
    import numpy as np

    rng = np.random.default_rng(seed)
    dots = VGroup()
    for _ in range(n):
        x = rng.uniform(-config.frame_width / 2, config.frame_width / 2)
        y = rng.uniform(-config.frame_height / 2, config.frame_height / 2)
        d = Dot(point=[x, y, 0], radius=rng.uniform(0.004, 0.014), color=INK)
        d.set_opacity(rng.uniform(0.04, 0.18))
        dots.add(d)
    return dots


# --------------------------------------------------------------------------
# Motion
# --------------------------------------------------------------------------

# The film has one house easing.  Nothing starts abruptly and nothing stops
# abruptly; the only exception is the cancellation of a letter, which is meant
# to be violent.
EASE = rate_functions.ease_in_out_sine
EASE_OUT = rate_functions.ease_out_cubic
EASE_IN = rate_functions.ease_in_cubic
SNAP = rate_functions.ease_out_expo


class Film:
    """Global tempo knobs, so a whole reel can be slowed down in one place."""

    beat = 0.55
    breath = 1.1
    hold = 2.0


def apply_defaults(scene) -> None:
    """Called at the top of every scene's ``construct``."""
    scene.camera.background_color = BG
