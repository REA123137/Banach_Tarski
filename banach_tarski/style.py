"""
Shared visual language for the Banach-Tarski film.

Everything that gives the series its look lives here: the palette, the type
scale, the black-canvas furniture (vignette, starfield), the glow helpers and
the two-voice caption system.  Scenes import from this module and never
hard-code a colour.
"""

from __future__ import annotations

import hashlib
import pathlib

import numpy as np
from manim import *

# --------------------------------------------------------------------------
# Palette.  Deep black canvas, one warm family and one cool family, plus a
# small set of accents used to label the four pieces of the decomposition.
# --------------------------------------------------------------------------

INK = "#000000"          # the canvas: pure black, as requested
INK_SOFT = "#080A10"     # panels / cards sitting on the canvas
GRID = "#161C28"         # construction lines

PAPER = "#F4F6FA"        # primary text
MUTED = "#8B94A7"        # secondary text
FAINT = "#3A4356"        # tertiary / disabled

GOLD = "#F5C86B"
AMBER = "#FFAE3B"
CORAL = "#FF7A59"
MAGENTA = "#FF5D8F"
VIOLET = "#9B7BFF"
INDIGO = "#6C7BFF"
CYAN = "#5FE3D8"
TEAL = "#2FB8B0"
MINT = "#7CFF9E"

# The four halves of the free group get stable colours across every scene:
# S(a) S(a^-1) S(b) S(b^-1).
C_A = GOLD
C_AI = CORAL
C_B = CYAN
C_BI = VIOLET
C_ID = PAPER
PIECE_COLORS = [C_A, C_AI, C_B, C_BI, C_ID]

# Two narrators.
VOICE_A = CYAN
VOICE_B = GOLD
VOICE_COLORS = {"A": VOICE_A, "B": VOICE_B}

# --------------------------------------------------------------------------
# Type.  DejaVu ships everywhere; FONT_STACK lets a nicer face win if the
# machine rendering the film happens to have one installed.
# --------------------------------------------------------------------------

FONT_STACK = ["Inter", "Manrope", "Helvetica Neue", "DejaVu Sans"]
MONO_STACK = ["JetBrains Mono", "IBM Plex Mono", "DejaVu Sans Mono"]


def _first_available(stack: list[str]) -> str:
    try:
        import manimpango

        families = set(manimpango.list_fonts())
        for name in stack:
            if name in families:
                return name
    except Exception:  # pragma: no cover - font probing is best effort
        pass
    return stack[-1]


FONT = _first_available(FONT_STACK)
MONO = _first_available(MONO_STACK)

H1, H2, H3, BODY, SMALL, TINY = 60, 44, 34, 28, 22, 18

# The caption bar owns the bottom of the frame.  Nothing else should sit below
# this line, or it will be read through the lower third.
SAFE_BOTTOM = -2.45


def T(text: str, size: float = BODY, color: str = PAPER, weight=NORMAL, **kw) -> Text:
    """Body/display type.  Every string in the film goes through here."""
    return Text(text, font=FONT, font_size=size, color=color, weight=weight, **kw)


def M(text: str, size: float = BODY, color: str = PAPER, **kw) -> Text:
    """Monospaced type - used for group words like ``a b a^-1``."""
    return Text(text, font=MONO, font_size=size, color=color, **kw)


# Unicode stand-ins so the project renders with no LaTeX toolchain installed.
INV = "⁻¹"      # superscript -1
NAT = "ℕ"
REAL = "ℝ"
INT = "ℤ"
SPHERE = "S²"
CUP = "∪"
SQCUP = "⊔"
IN = "∈"
CONG = "≅"
INF = "∞"
MU = "μ"
TIMES = "×"
ARROW = "→"
NEQ = "≠"


def word(letters: str, size: float = BODY, color: str = PAPER) -> Text:
    """Render a free-group word, turning ``A``/``B`` into a/b with inverses."""
    out = ""
    for ch in letters:
        if ch == "A":
            out += "a" + INV
        elif ch == "B":
            out += "b" + INV
        else:
            out += ch
    return M(out or "e", size=size, color=color)


# --------------------------------------------------------------------------
# Canvas furniture.
# --------------------------------------------------------------------------

_ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"


def _vignette_path(strength: float, w: int = 1280, h: int = 720) -> pathlib.Path:
    _ASSETS.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(f"{strength}-{w}-{h}".encode()).hexdigest()[:8]
    path = _ASSETS / f"vignette-{key}.png"
    if path.exists():
        return path

    from PIL import Image

    ys, xs = np.mgrid[0:h, 0:w]
    x = (xs / (w - 1) - 0.5) * 2.0
    y = (ys / (h - 1) - 0.5) * 2.0 * (h / w)
    r = np.sqrt(x**2 + y**2) / np.sqrt(1 + (h / w) ** 2)
    alpha = np.clip((r - 0.34) / 0.66, 0, 1) ** 1.7 * strength
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 3] = (alpha * 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(path)
    return path


def vignette(strength: float = 0.92) -> ImageMobject:
    """A soft black falloff that pulls the eye to the centre of frame."""
    img = ImageMobject(str(_vignette_path(strength)))
    img.stretch_to_fit_width(config.frame_width * 1.02)
    img.stretch_to_fit_height(config.frame_height * 1.02)
    img.set_z_index(50)
    return img


def starfield(n: int = 130, seed: int = 7, spread: float = 1.15) -> VGroup:
    """Faint depth cues.  Never bright enough to compete with the subject."""
    rng = np.random.default_rng(seed)
    stars = VGroup()
    for _ in range(n):
        p = np.array(
            [
                rng.uniform(-1, 1) * config.frame_width / 2 * spread,
                rng.uniform(-1, 1) * config.frame_height / 2 * spread,
                0.0,
            ]
        )
        mag = rng.random() ** 3
        d = Dot(p, radius=0.006 + 0.018 * mag, color=PAPER)
        d.set_opacity(0.06 + 0.30 * mag)
        stars.add(d)
    stars.set_z_index(-40)
    return stars


def glow(mob: VMobject, color: str | None = None, layers: int = 14,
         spread: float = 0.55, opacity: float = 0.055) -> VGroup:
    """Fake bloom: nested copies with a widening, fading stroke."""
    color = color or mob.get_color()
    halo = VGroup()
    for i in range(layers):
        t = (i + 1) / layers
        c = mob.copy()
        c.set_fill(opacity=0)
        c.set_stroke(color=color, width=spread * 42 * t, opacity=opacity * (1 - t) ** 1.4)
        halo.add(c)
    halo.set_z_index(mob.z_index - 1)
    return halo


def glow_dot(point, color: str = GOLD, radius: float = 0.075,
             layers: int = 16, reach: float = 7.0) -> VGroup:
    """A point light: a solid core inside a radial falloff."""
    g = VGroup()
    for i in range(layers, 0, -1):
        t = i / layers
        c = Circle(radius=radius * (1 + reach * t), color=color)
        c.set_stroke(width=0)
        c.set_fill(color, opacity=0.055 * (1 - t) ** 1.6)
        g.add(c)
    core = Dot(radius=radius, color=color).set_fill(PAPER, opacity=1)
    core.set_stroke(color, width=2, opacity=0.9)
    g.add(core)
    g.move_to(point)
    return g


def rule(width: float = 5.0, color: str = FAINT, weight: float = 1.6) -> Line:
    return Line(LEFT * width / 2, RIGHT * width / 2).set_stroke(color, weight)


def panel(width: float, height: float, color: str = GRID, fill: float = 0.55) -> RoundedRectangle:
    r = RoundedRectangle(width=width, height=height, corner_radius=0.16)
    r.set_stroke(color, 1.4, opacity=0.9)
    r.set_fill(INK_SOFT, opacity=fill)
    return r


# --------------------------------------------------------------------------
# Base scenes.  Every chapter inherits one of these so the furniture, the
# captions and the pacing are identical from cut to cut.
# --------------------------------------------------------------------------

class Look:
    """Easing shared by every scene, so the motion feels the same cut to cut."""

    ease = rate_functions.ease_in_out_sine
    ease_out = rate_functions.ease_out_cubic


class CaptionBar(VGroup):
    """Lower third: a coloured voice tag plus one line of narration."""

    def __init__(self, voice: str, text: str, width: float = 11.4):
        super().__init__()
        color = VOICE_COLORS.get(voice, PAPER)
        tag = T(voice, size=SMALL, color=INK, weight=BOLD)
        chip = RoundedRectangle(width=0.62, height=0.52, corner_radius=0.14)
        chip.set_fill(color, opacity=1).set_stroke(width=0)
        tag.move_to(chip)
        head = VGroup(chip, tag)

        body = T(text, size=SMALL, color=PAPER)
        if body.width > width - 1.2:
            body.scale((width - 1.2) / body.width)
        body.next_to(head, RIGHT, buff=0.34)

        group = VGroup(head, body)
        bar = Rectangle(width=group.width + 0.9, height=group.height + 0.62)
        bar.set_fill(INK, opacity=0.62).set_stroke(color, 1.0, opacity=0.30)
        bar.move_to(group)
        accent = Line(bar.get_corner(DL), bar.get_corner(DR)).set_stroke(color, 2.0, opacity=0.55)

        self.add(bar, accent, head, body)
        self.set_z_index(60)
        self.move_to(ORIGIN).to_edge(DOWN, buff=0.42)


class _Narration:
    """
    Caption bar, chapter cards and stage clearing.

    Mixed into the 2-D and moving-camera bases so a scene reads the same way
    whichever camera it happens to be using.
    """

    def _init_narration(self):
        self._caption = None

    def say(self, voice: str, text: str, hold: float = 2.2):
        """Swap the lower third to a new line and hold it."""
        new = CaptionBar(voice, text)
        self._place_caption(new)
        if self._caption is None:
            self.play(FadeIn(new, shift=UP * 0.18, run_time=0.45))
        else:
            self.play(
                FadeOut(self._caption, shift=DOWN * 0.14, run_time=0.28),
                FadeIn(new, shift=UP * 0.14, run_time=0.38),
            )
        self._caption = new
        if hold:
            self.wait(hold)
        return new

    def _place_caption(self, bar: Mobject):
        """Hook for cameras that move - the bar must stay in the frame."""

    def clear_caption(self, run_time: float = 0.35):
        if self._caption is not None:
            self.play(FadeOut(self._caption, shift=DOWN * 0.14, run_time=run_time))
            self._caption = None

    def chapter(self, number: str, title: str, subtitle: str = "", hold: float = 1.5):
        num = T(number, size=TINY, color=GOLD, weight=BOLD)
        num.set_opacity(0.9)
        head = T(title, size=H2, color=PAPER, weight=BOLD)
        sub = T(subtitle, size=SMALL, color=MUTED) if subtitle else VGroup()

        stack = VGroup(num, head, *([sub] if subtitle else [])).arrange(DOWN, buff=0.30)
        stack.move_to(ORIGIN)
        line = rule(0.01, GOLD, 2.2).next_to(head, DOWN, buff=0.18)

        self.play(
            LaggedStart(
                FadeIn(num, shift=UP * 0.15),
                AddTextLetterByLetter(head, run_time=0.9),
                lag_ratio=0.35,
            )
        )
        self.play(line.animate.stretch_to_fit_width(head.width * 0.72), run_time=0.55,
                  rate_func=Look.ease_out)
        if subtitle:
            self.play(FadeIn(sub, shift=UP * 0.12), run_time=0.5)
        self.wait(hold)
        self.play(FadeOut(VGroup(stack, line), shift=UP * 0.25, run_time=0.6))



class BTScene(_Narration, Scene):
    """2-D chapter base."""

    stars = True
    star_seed = 7
    vignette_strength = 0.92

    def setup(self):
        super().setup()
        self.camera.background_color = INK
        self._furniture = Group()
        if self.stars:
            s = starfield(seed=self.star_seed)
            self._furniture.add(s)
            self.add(s)
        v = vignette(self.vignette_strength)
        self._furniture.add(v)
        self.add(v)
        self._init_narration()


class BTMovingScene(_Narration, MovingCameraScene):
    """
    2-D chapter base for scenes that push in or pull back.

    The furniture and the caption bar are pinned to the camera frame, so they
    keep their place on screen while the world scrolls underneath.
    """

    stars = True
    star_seed = 7
    vignette_strength = 0.92

    def setup(self):
        super().setup()
        self.camera.background_color = INK
        self._furniture = Group()
        frame = self.camera.frame

        if self.stars:
            s = starfield(seed=self.star_seed)
            s.add_updater(lambda m: m.move_to(frame.get_center()))
            self._furniture.add(s)
            self.add(s)

        v = vignette(self.vignette_strength)

        def fit(m):
            m.stretch_to_fit_width(frame.width * 1.02)
            m.stretch_to_fit_height(frame.height * 1.02)
            m.move_to(frame.get_center())

        v.add_updater(fit)
        self._furniture.add(v)
        self.add(v)
        self._init_narration()

    def _place_caption(self, bar: Mobject):
        """Keep the lower third glued to the bottom of the moving frame."""
        frame = self.camera.frame
        base_width = config.frame_width
        natural = bar.width

        def follow(m: Mobject):
            k = frame.width / base_width
            m.scale_to_fit_width(natural * k)
            m.move_to(frame.get_center())
            m.shift(DOWN * (frame.height / 2 - m.height / 2 - 0.42 * k))

        follow(bar)
        bar.add_updater(follow)


class BT3DScene(ThreeDScene):
    """3-D chapter base - same furniture, pinned to the frame."""

    vignette_strength = 0.85

    def setup(self):
        super().setup()
        self.camera.background_color = INK
        self._caption = None
        self._vig = vignette(self.vignette_strength)
        self.add_fixed_in_frame_mobjects(self._vig)

    def say(self, voice: str, text: str, hold: float = 2.2):
        new = CaptionBar(voice, text)
        self.add_fixed_in_frame_mobjects(new)
        if self._caption is None:
            self.play(FadeIn(new, shift=UP * 0.18, run_time=0.45))
        else:
            self.play(
                FadeOut(self._caption, shift=DOWN * 0.14, run_time=0.28),
                FadeIn(new, shift=UP * 0.14, run_time=0.38),
            )
        self._caption = new
        if hold:
            self.wait(hold)
        return new

    def label(self, mob: Mobject):
        """Pin a 2-D label to the frame (titles, legends) above the 3-D stage."""
        self.add_fixed_in_frame_mobjects(mob)
        return mob
