"""Visual identity for *Two Balls* — the Banach-Tarski film.

Everything is drawn on pure black and set in LaTeX's Computer Modern, through
``Tex`` and ``MathTex``: the film is a mathematics film and it should be set in
the type mathematics is set in.

The palette is deliberately small: four letter colours (one per generator of
the free group), one warm off-white for prose, one red reserved exclusively for
refusal, and a single grey for anything that is a ghost of something else.

The second half of this module is the layout system.  The frame is divided into
three bands — a head band for titles and formulas, a stage band for geometry,
a foot band for captions — and every placement helper *fits* its argument into
its band, shrinking it if it does not fit.  Overlap is therefore not something
to be checked for afterwards; it cannot be constructed.
"""

from __future__ import annotations

import re

import numpy as np
from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Dot,
    Line,
    MathTex,
    Mobject,
    Rectangle,
    Tex,
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
# Prose into LaTeX
# --------------------------------------------------------------------------

# The script is written in Unicode; LaTeX is what actually sets it.  These are
# every non-ASCII character the film uses, and nothing else is allowed through.
_LATEX_SPECIAL = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_UNICODE_PAIRS = [
    ("⁻¹", "$^{-1}$"),
    ("⁻ⁿ", "$^{-n}$"),
]

_UNICODE = {
    # punctuation and marks
    "—": "---", "–": "--", "…": r"\dots{}", "·": r"$\cdot$",
    "’": "'", "“": "``", "”": "''", "é": r"\'e", "°": r"$^\circ$",
    "′": "$'$", "⁄": "/", "●": r"$\bullet$",
    # exponents and indices
    "⁰": "$^0$", "¹": "$^1$", "²": "$^2$", "³": "$^3$", "ⁿ": "$^n$",
    "₀": "$_0$", "₁": "$_1$", "₂": "$_2$", "₃": "$_3$", "₄": "$_4$",
    "ᵢ": "$_i$", "ⱼ": "$_j$",
    # greek
    "θ": r"$\theta$", "ρ": r"$\rho$", "μ": r"$\mu$", "α": r"$\alpha$",
    # relations and operators
    "⊔": r"$\sqcup$", "∪": r"$\cup$", "∩": r"$\cap$", "∖": r"$\setminus$",
    "∈": r"$\in$", "∼": r"$\sim$", "∅": r"$\emptyset$", "≈": r"$\approx$",
    "≠": r"$\neq$", "≤": r"$\leq$", "≥": r"$\geq$", "±": r"$\pm$",
    "×": r"$\times$", "−": "$-$", "→": r"$\rightarrow$", "√": r"$\sqrt{\,}$",
    "⟨": r"$\langle$", "⟩": r"$\rangle$", "⋯": r"$\cdots$",
}


def latex_escape(text: str) -> str:
    """Turn a line of the script into LaTeX that sets exactly what it says.

    Anything that would be a LaTeX control sequence is escaped first; only then
    are the Unicode symbols replaced by real mathematics, so the substitutions
    can safely introduce ``$`` and braces of their own.
    """
    out = "".join(_LATEX_SPECIAL.get(ch, ch) for ch in text)
    for pair, repl in _UNICODE_PAIRS:
        out = out.replace(pair, repl)
    out = "".join(_UNICODE.get(ch, ch) for ch in out)
    # adjacent maths groups become one, so spacing stays even
    out = out.replace("$$", "")
    if any(ord(ch) > 127 for ch in out):
        stray = sorted({ch for ch in out if ord(ch) > 127})
        raise ValueError(f"no LaTeX for {stray!r} in {text!r}")
    return out


# --------------------------------------------------------------------------
# Type
# --------------------------------------------------------------------------

MAX_WIDTH = config.frame_width - 1.3      # nothing ever touches the side edges

# LaTeX sets a good deal smaller than a hinted screen face at the same nominal
# size, so every size in the scenes is read through this factor.  Change it
# here and the whole film re-sizes together.
TEX_SCALE = 1.80


def _size(size: float) -> float:
    return size * TEX_SCALE


def _fit(mob: Mobject, max_width: float | None = None) -> Mobject:
    """No line is ever allowed to run off the frame."""
    limit = MAX_WIDTH if max_width is None else max_width
    if mob.width > limit:
        mob.scale_to_fit_width(limit)
    return mob


def body(text: str, size: float = 34, color: str = INK, width: float | None = None, **kw) -> Tex:
    return _fit(Tex(latex_escape(text), font_size=_size(size), color=color, **kw), width)


def display(text: str, size: float = 62, color: str = INK, width: float | None = None, **kw) -> Tex:
    return _fit(
        Tex(r"\textbf{" + latex_escape(text) + "}", font_size=_size(size), color=color, **kw),
        width,
    )


def mono(text: str, size: float = 38, color: str = INK, width: float | None = None, **kw) -> Tex:
    return _fit(
        Tex(r"\texttt{" + latex_escape(text) + "}", font_size=_size(size), color=color, **kw),
        width,
    )


def serif(text: str, size: float = 34, color: str = INK, width: float | None = None, **kw) -> Tex:
    return body(text, size=size, color=color, width=width, **kw)


def caption(text: str, size: float = 26, color: str = INK_DIM, width: float | None = None) -> Tex:
    return _fit(
        Tex(r"\textit{" + latex_escape(text) + "}", font_size=_size(size), color=color), width
    )


def formula(tex: str, size: float = 44, color: str = INK, width: float | None = None, **kw) -> MathTex:
    """Mathematics, written as mathematics.  ``tex`` is LaTeX, not Unicode.

    A stray Unicode symbol here would reach LaTeX as itself and fail deep
    inside a compile log, so it is caught at the call instead.
    """
    if any(ord(ch) > 127 for ch in tex):
        stray = sorted({ch for ch in tex if ord(ch) > 127})
        raise ValueError(f"formula() takes LaTeX; {stray!r} is Unicode, in {tex!r}")
    return _fit(MathTex(tex, font_size=_size(size), color=color, **kw), width)


def prose_math(text: str, *maths: str, size: float = 32, color: str = INK,
               width: float | None = None) -> Tex:
    """A line of prose with mathematics set into it.

    ``text`` is the script's own Unicode, with ``{}`` marking each slot;
    ``maths`` are LaTeX.  This is how a caption says "put a in front of every
    word of S(a^{-1})" without the LaTeX being escaped into literal characters.
    """
    body_tex = latex_escape(text)
    for m in maths:
        body_tex = body_tex.replace(r"\{\}", f"${m}$", 1)
    return _fit(Tex(body_tex, font_size=_size(size), color=color), width)


def highlighted(text: str, word: str, size: float = 36, color: str = INK,
                accent: str = GOLD) -> Tex:
    """A line of prose with one word set apart — used where a term is defined."""
    piece = latex_escape(word)
    line = Tex(
        latex_escape(text), font_size=_size(size), color=color, substrings_to_isolate=[piece]
    )
    line.set_color_by_tex(piece, accent)
    return _fit(line)


# --------------------------------------------------------------------------
# Word typography
# --------------------------------------------------------------------------

def letter_glyph(letter: str) -> str:
    """The LaTeX for one letter: ``A`` -> ``a^{-1}``."""
    if letter == "":
        return "e"
    return letter.lower() + ("^{-1}" if letter.isupper() else "")


def word_glyph(word: str) -> str:
    return "".join(letter_glyph(c) for c in word) if word else "e"


def word_tex(word: str, size: float = 38, color: str = INK) -> MathTex:
    """A whole word as one piece of mathematics."""
    return MathTex(word_glyph(word), font_size=_size(size), color=color)


def word_mobject(
    word: str,
    size: float = 38,
    color: str | None = None,
    face: str = "mono",
    spaced: bool = False,
) -> VGroup:
    """A word of F2 as a row of individually addressable letters.

    Returned as a ``VGroup`` so a single letter can be faded, flashed or made
    to collide with its neighbour — which is what most of the film does.
    """
    if not word:
        return VGroup(MathTex("e", font_size=_size(size), color=color or C_E))
    letters = VGroup(
        *[
            MathTex(letter_glyph(c), font_size=_size(size), color=color or LETTER_COLORS[c])
            for c in word
        ]
    )
    letters.arrange(RIGHT, buff=0.18 if spaced else 0.10, aligned_edge=DOWN)
    return letters


# --------------------------------------------------------------------------
# The three bands
# --------------------------------------------------------------------------

FRAME_W = config.frame_width          # 14.22
FRAME_H = config.frame_height         # 8.00
TOP_EDGE = FRAME_H / 2
BOTTOM_EDGE = -FRAME_H / 2

BAND = 1.50            # height reserved at the top and at the bottom for type
MARGIN = 0.26          # breathing room against the frame edge
STAGE_TOP = TOP_EDGE - BAND
STAGE_BOTTOM = BOTTOM_EDGE + BAND
STAGE_HALF = STAGE_TOP                 # geometry lives in |y| <= STAGE_HALF
STAGE_HEIGHT = STAGE_TOP - STAGE_BOTTOM


def head(mob: Mobject, gap: float = MARGIN) -> Mobject:
    """Put a title, a formula or a running head in the top band.

    If it is too tall for the band it is scaled until it fits, so it can never
    reach down into the geometry.
    """
    room = BAND - gap - 0.10
    if mob.height > room:
        mob.scale_to_fit_height(room)
    _fit(mob)
    mob.move_to(np.array([0.0, TOP_EDGE - gap - mob.height / 2, 0.0]))
    return mob


def foot(mob: Mobject, gap: float = MARGIN) -> Mobject:
    """Put a caption, a verdict or a bridge in the bottom band."""
    room = BAND - gap - 0.10
    if mob.height > room:
        mob.scale_to_fit_height(room)
    _fit(mob)
    mob.move_to(np.array([0.0, BOTTOM_EDGE + gap + mob.height / 2, 0.0]))
    return mob


def stage(mob: Mobject, margin: float = 0.18, width: float | None = None) -> Mobject:
    """Centre a drawing in the middle band, scaled to fit it."""
    limit_h = STAGE_HEIGHT - 2 * margin
    limit_w = (MAX_WIDTH if width is None else width)
    if mob.height > limit_h:
        mob.scale_to_fit_height(limit_h)
    if mob.width > limit_w:
        mob.scale_to_fit_width(limit_w)
    mob.move_to(ORIGIN)
    return mob


def stage_scale(radius: float = 1.0, margin: float = 0.22) -> float:
    """The largest view scale at which a sphere of ``radius`` stays in the band."""
    return (STAGE_HALF - margin) / radius


def side_slot(side: float, mob: Mobject, width: float = 4.4) -> Mobject:
    """Park a legend or a label in the left or right third, clear of the middle."""
    if mob.width > width:
        mob.scale_to_fit_width(width)
    x = side * (FRAME_W / 2 - MARGIN - mob.width / 2)
    mob.move_to(np.array([x, 0.0, 0.0]))
    return mob


def stage_corner(mob: Mobject, x_sign: float = 1.0, y_sign: float = 1.0,
                 gap: float = 0.20) -> Mobject:
    """Tuck a running readout into a corner of the stage band.

    The frame corners belong to the head and foot bands; a counter parked
    there would sooner or later meet a title.
    """
    x = x_sign * (FRAME_W / 2 - MARGIN - mob.width / 2)
    y = y_sign * (STAGE_HALF - gap - mob.height / 2)
    mob.move_to(np.array([x, y, 0.0]))
    return mob


def overlaps(a: Mobject, b: Mobject, pad: float = 0.06) -> bool:
    """Do two things share any of the frame?  Bounding boxes, deliberately."""
    if not a.has_points() or not b.has_points():
        return False
    ax0, ax1 = a.get_left()[0] - pad, a.get_right()[0] + pad
    ay0, ay1 = a.get_bottom()[1] - pad, a.get_top()[1] + pad
    bx0, bx1 = b.get_left()[0], b.get_right()[0]
    by0, by1 = b.get_bottom()[1], b.get_top()[1]
    return not (ax1 < bx0 or bx1 < ax0 or ay1 < by0 or by1 < ay0)


def assert_clear(*mobs: Mobject) -> None:
    """Fail loudly at construction time if two things are on top of each other.

    Cheap enough to leave switched on: a scene that collides refuses to render
    rather than shipping a frame with a caption written across a sphere.
    """
    items = [m for m in mobs if m is not None and m.has_points()]
    for i, a in enumerate(items):
        for b in items[i + 1 :]:
            if overlaps(a, b):
                raise AssertionError(
                    f"these two overlap: {a} at {a.get_center()[:2]} "
                    f"and {b} at {b.get_center()[:2]}"
                )


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
    """A cheap bloom: concentric copies of a stroke, each fainter and fatter."""
    halo = VGroup()
    for i in range(layers):
        ring = mob.copy()
        if isinstance(ring, VMobject):
            ring.set_fill(opacity=0)
            ring.set_stroke(color=color, width=(i + 1) * spread, opacity=opacity)
        halo.add(ring)
    return halo


def star_field(n: int = 90, seed: int = 7) -> VGroup:
    """A faint dust of dots.  The film's black is never quite empty."""
    rng = np.random.default_rng(seed)
    dots = VGroup()
    for _ in range(n):
        x = rng.uniform(-FRAME_W / 2, FRAME_W / 2)
        y = rng.uniform(-FRAME_H / 2, FRAME_H / 2)
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
