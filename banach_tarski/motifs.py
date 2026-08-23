"""The three recurring images of the film.

The script insists that only three analogies exist and that each is used
twice, so the objects carrying them are built once, here, and imported by
every scene that needs them:

* :class:`Machine`   — the theorem drawn as a machine behind eight numbered
  panels (scene 3, one panel per scene, fully open in scene 13);
* :class:`Library`   — the Library of Babel (scene 5, the librarian's push in
  scene 6, the impossible hand in scene 9);
* :class:`ChoiceHand` — the hand of the axiom of choice (scene 9, one second
  again over the chocolate at the very end).

Plus the small props several scenes share: gears, books, shelves, a Rubik's
cube, a chocolate bar and a weighing scale.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DEGREES,
    DOWN,
    LEFT,
    ORIGIN,
    OUT,
    PI,
    RIGHT,
    UP,
    Arc,
    Arrow,
    Circle,
    Difference,
    Dot,
    Ellipse,
    Line,
    Polygon,
    RegularPolygon,
    Rectangle,
    RoundedRectangle,
    Square,
    VGroup,
    VMobject,
    Write,
)

from . import theme

# --------------------------------------------------------------------------
# Gears
# --------------------------------------------------------------------------


def gear(radius: float = 0.5, teeth: int = 12, color: str = theme.INK_DIM, depth: float = 0.16):
    """A cog.  Drawn as one polygon so it can be rotated as a rigid body."""
    pts = []
    for i in range(teeth):
        a0 = 2 * PI * i / teeth
        a1 = a0 + PI / teeth * 0.55
        a2 = a0 + PI / teeth
        a3 = a0 + PI / teeth * 1.45
        for ang, r in ((a0, radius), (a1, radius + depth), (a2, radius + depth), (a3, radius)):
            pts.append(np.array([np.cos(ang) * r, np.sin(ang) * r, 0.0]))
    body = Polygon(*pts, color=color, stroke_width=2.0)
    body.set_fill(theme.BG, opacity=1.0)
    hub = Circle(radius=radius * 0.32, color=color, stroke_width=2.0)
    spokes = VGroup(
        *[
            Line(
                np.array([np.cos(a) * radius * 0.32, np.sin(a) * radius * 0.32, 0]),
                np.array([np.cos(a) * radius * 0.86, np.sin(a) * radius * 0.86, 0]),
                color=color,
                stroke_width=1.4,
            )
            for a in np.linspace(0, 2 * PI, 5, endpoint=False)
        ]
    )
    return VGroup(body, spokes, hub)


# --------------------------------------------------------------------------
# The machine
# --------------------------------------------------------------------------

MACHINE_COGS = [
    ("1", "the letters"),
    ("2", "the catalogue"),
    ("3", "the matrices"),
    ("4", "the orbits"),
    ("5", "the choice"),
    ("6", "the poles"),
    ("7", "the centre"),
    ("8", "the assembly"),
]


class Machine(VGroup):
    """One ball in on the left, two out on the right, eight panels in between.

    ``self.panels[i]`` is the numbered cover, ``self.cogs[i]`` the mechanism
    underneath.  :meth:`drop` is the gesture that ends most scenes.
    """

    def __init__(self, width: float = 8.4, height: float = 4.2):
        super().__init__()
        self.body = RoundedRectangle(
            corner_radius=0.22,
            width=width,
            height=height,
            stroke_color=theme.INK_DIM,
            stroke_width=2.2,
            fill_color=theme.GHOST_SOFT,
            fill_opacity=1.0,
        )
        self.add(self.body)

        # feed and delivery
        self.chute_in = Line(
            self.body.get_left() + LEFT * 1.5, self.body.get_left(), color=theme.INK_DIM, stroke_width=2
        )
        self.chute_out_top = Line(
            self.body.get_right(),
            self.body.get_right() + RIGHT * 1.5 + UP * 0.75,
            color=theme.INK_DIM,
            stroke_width=2,
        )
        self.chute_out_bottom = Line(
            self.body.get_right(),
            self.body.get_right() + RIGHT * 1.5 + DOWN * 0.75,
            color=theme.INK_DIM,
            stroke_width=2,
        )
        self.add(self.chute_in, self.chute_out_top, self.chute_out_bottom)

        # the mechanism, and the eight covers over it
        self.cogs = VGroup()
        self.labels = VGroup()
        self.panels = VGroup()
        cols, rows = 4, 2
        cw = (width - 0.6) / cols
        ch = (height - 0.6) / rows
        for k, (num, name) in enumerate(MACHINE_COGS):
            r, c = divmod(k, cols)
            pos = self.body.get_center() + np.array(
                [(c - (cols - 1) / 2) * cw, ((rows - 1) / 2 - r) * ch, 0.0]
            )
            cog = gear(radius=min(cw, ch) * 0.30, teeth=11 + k % 3, color=theme.INK_DIM)
            cog.move_to(pos)
            label = theme.caption(name, size=17)
            label.next_to(cog, DOWN, buff=0.10)
            label.set_opacity(0.7)
            cover = Rectangle(
                width=cw - 0.10,
                height=ch - 0.10,
                fill_color="#111111",
                fill_opacity=1.0,
                stroke_color=theme.GHOST,
                stroke_width=1.4,
            ).move_to(pos)
            stamp = theme.mono(num, size=24, color=theme.INK_DIM).move_to(pos)
            stamp.set_opacity(0.75)
            panel = VGroup(cover, stamp)
            self.cogs.add(cog)
            self.labels.add(label)
            self.panels.add(panel)
        self.add(self.cogs, self.labels, self.panels)
        self.labels.set_opacity(0.0)

    def drop(self, index: int, run_time: float = 0.9):
        """The gesture that closes a scene: panel ``index`` falls away."""
        from manim import AnimationGroup, FadeIn, FadeOut

        panel = self.panels[index]
        return AnimationGroup(
            panel.animate(run_time=run_time, rate_func=theme.EASE_IN)
            .shift(DOWN * 3.2)
            .set_opacity(0.0),
            FadeIn(self.labels[index], run_time=run_time),
            lag_ratio=0.15,
        )

    def run(self, turns: float = 1.0, run_time: float = 3.0):
        """Every visible cog turns, alternating direction, as a real train would."""
        from manim import AnimationGroup, Rotate

        anims = []
        for i, cog in enumerate(self.cogs):
            anims.append(
                Rotate(
                    cog,
                    angle=(1 if i % 2 == 0 else -1) * turns * 2 * PI,
                    run_time=run_time,
                    rate_func=theme.EASE,
                )
            )
        return AnimationGroup(*anims)


# --------------------------------------------------------------------------
# Books, shelves, and the Library of Babel
# --------------------------------------------------------------------------


def book(
    word: str,
    height: float = 1.15,
    width: float = 0.30,
    color: str | None = None,
    label: bool = True,
) -> VGroup:
    """One volume of the catalogue, seen spine-on, titled with its word."""
    col = color or theme.LETTER_COLORS.get(word[0] if word else "", theme.C_E)
    spine = RoundedRectangle(
        corner_radius=0.045,
        width=width,
        height=height,
        stroke_color=col,
        stroke_width=1.7,
        fill_color=col,
        fill_opacity=0.14,
    )
    grp = VGroup(spine)
    grp.word = word
    if label:
        title = theme.serif(theme.word_glyph(word), size=17, color=col)
        title.rotate(PI / 2)
        if title.height > height * 0.82:
            title.scale(height * 0.82 / title.height)
        title.move_to(spine)
        grp.add(title)
        grp.title = title
    band = Line(
        spine.get_left() + UP * height * 0.36,
        spine.get_right() + UP * height * 0.36,
        color=col,
        stroke_width=1.1,
    ).set_opacity(0.6)
    grp.add(band)
    grp.spine = spine
    grp.color_used = col
    return grp


def shelf_unit(
    words: list[str],
    per_row: int = 6,
    rows: int = 3,
    color: str | None = None,
    label: str | None = None,
) -> VGroup:
    """One shelving unit: the librarian pushes these, one notch at a time."""
    frame_w = per_row * 0.38 + 0.30
    frame_h = rows * 1.35 + 0.25
    frame = Rectangle(
        width=frame_w,
        height=frame_h,
        stroke_color=theme.GHOST,
        stroke_width=1.6,
        fill_opacity=0,
    )
    books = VGroup()
    for r in range(rows):
        row = VGroup()
        for i in range(per_row):
            k = r * per_row + i
            w = words[k % len(words)]
            row.add(book(w, color=color))
        row.arrange(RIGHT, buff=0.07)
        row.move_to(frame.get_top() + DOWN * (0.72 + r * 1.35))
        books.add(row)
        if r < rows - 1:
            plank = Line(
                frame.get_left() + DOWN * (1.35 * (r + 1) - frame_h / 2 + frame_h / 2),
                frame.get_right() + DOWN * (1.35 * (r + 1) - frame_h / 2 + frame_h / 2),
                color=theme.GHOST,
                stroke_width=1.4,
            )
            plank.move_to(frame.get_top() + DOWN * (1.35 * (r + 1) + 0.05))
            frame = VGroup(frame, plank) if not isinstance(frame, VGroup) else frame.add(plank)
    unit = VGroup(frame, books)
    unit.books = books
    if label:
        tag = theme.mono(label, size=26, color=color or theme.INK_DIM)
        tag.next_to(unit, DOWN, buff=0.22)
        unit.add(tag)
        unit.tag = tag
    return unit


class _HexWall(RegularPolygon):
    """A wall of the library.  It is drawn, never filled.

    ``set_opacity`` touches fill and stroke together, so any scene that dims
    the library would otherwise paint a grey slab across the frame; refusing
    the fill here makes that impossible.
    """

    def __init__(self, *args, **kwargs):
        self._sealed = False
        super().__init__(*args, **kwargs)
        self.set_fill(opacity=0.0)
        self._sealed = True

    def set_fill(self, *args, **kwargs):
        if getattr(self, "_sealed", False):
            return self
        return super().set_fill(*args, **kwargs)


class Library(VGroup):
    """A Borges hexagon, receding.  Every spine carries a word of F2."""

    def __init__(self, depth: int = 5, words: list[str] | None = None, seed: int = 0):
        super().__init__()
        from .freegroup import sample_words

        words = words or sample_words(200, 1, 5, seed=seed)
        self.rings = VGroup()
        idx = 0
        for k in range(depth):
            t = k / max(depth - 1, 1)
            radius = 5.6 * (0.30 + 0.70 * (1 - t) ** 1.4)
            opacity = 0.14 + 0.72 * (1 - t)
            hexagon = _HexWall(
                n=6, radius=radius, start_angle=PI / 6, color=theme.INK_DIM, stroke_width=1.4
            )
            hexagon.set_stroke(opacity=opacity * 0.55)
            ring = VGroup(hexagon)
            shelves = VGroup()
            for side in range(6):
                a0 = PI / 6 + 2 * PI * side / 6
                a1 = PI / 6 + 2 * PI * (side + 1) / 6
                p0 = radius * np.array([np.cos(a0), np.sin(a0), 0])
                p1 = radius * np.array([np.cos(a1), np.sin(a1), 0])
                n_books = max(2, int(6 * (1 - 0.55 * t)))
                for j in range(n_books):
                    u = (j + 0.5) / n_books
                    pos = p0 + (p1 - p0) * u
                    b = book(words[idx % len(words)], height=0.44 * (1 - 0.55 * t), width=0.11, label=False)
                    idx += 1
                    b.move_to(pos)
                    b.rotate(np.arctan2(*(p1 - p0)[1::-1]))
                    b.set_opacity(opacity)
                    shelves.add(b)
            ring.add(shelves)
            self.rings.add(ring)
        self.add(self.rings)
        self.set_z_index(0)

    def fly(self, rate: float = 0.34, near: float = 15.0, far: float = 2.2):
        """An endless forward flight: rings swell, fade out, and are recycled.

        Returned as a ``dt`` updater so the camera never stops moving and the
        shot can be held for as long as the voice needs.
        """

        def update(_mob, dt):
            for ring in self.rings:
                ring.scale(float(np.exp(rate * dt)), about_point=ORIGIN)
                w = ring[0].width
                if w > near:
                    ring.scale(far / max(w, 1e-6), about_point=ORIGIN)
                    w = ring[0].width
                t = (w - far) / (near - far)
                opacity = float(np.clip(1.0 - t, 0.0, 1.0) ** 1.3 * np.clip(t * 6.0, 0.0, 1.0))
                ring[0].set_stroke(opacity=opacity * 0.45)
                ring[1].set_opacity(opacity)

        return update


class ChoiceHand(VGroup):
    """Translucent, untextured, shadowless.  It is not supposed to exist."""

    def __init__(self, scale: float = 1.0, color: str = theme.CHOICE):
        super().__init__()
        palm = RoundedRectangle(
            corner_radius=0.28, width=1.15, height=1.25, stroke_width=1.6, stroke_color=color
        )
        palm.set_fill(color, opacity=0.10)
        fingers = VGroup()
        for i, (dx, length, tilt) in enumerate(
            [(-0.38, 1.05, 0.09), (-0.13, 1.25, 0.03), (0.13, 1.18, -0.03), (0.38, 0.95, -0.10)]
        ):
            f = RoundedRectangle(
                corner_radius=0.11, width=0.23, height=length, stroke_width=1.4, stroke_color=color
            )
            f.set_fill(color, opacity=0.08)
            f.move_to(palm.get_top() + np.array([dx, length / 2 - 0.12, 0]))
            f.rotate(tilt, about_point=palm.get_top() + np.array([dx, 0, 0]))
            fingers.add(f)
        thumb = RoundedRectangle(
            corner_radius=0.11, width=0.24, height=0.82, stroke_width=1.4, stroke_color=color
        )
        thumb.set_fill(color, opacity=0.08)
        thumb.rotate(0.85)
        thumb.move_to(palm.get_left() + np.array([-0.16, 0.30, 0]))
        wrist = RoundedRectangle(
            corner_radius=0.14, width=0.62, height=0.55, stroke_width=1.3, stroke_color=color
        )
        wrist.set_fill(color, opacity=0.07)
        wrist.next_to(palm, DOWN, buff=-0.10)
        self.add(wrist, palm, thumb, fingers)
        self.scale(scale)
        self.set_z_index(5)


def human_hand(scale: float = 1.0) -> VGroup:
    """The hand that hesitates, before the other one arrives."""
    h = ChoiceHand(scale=scale, color=theme.INK)
    for part in h.family_members_with_points():
        part.set_fill(theme.INK, opacity=0.05)
        part.set_stroke(theme.INK, opacity=0.55, width=1.5)
    return h


# --------------------------------------------------------------------------
# Small props
# --------------------------------------------------------------------------


CUBE_FACE_COLORS = ["#F2EFE9", "#FFC24B", "#FF6B5A", "#4FD1C5", "#8B7BFF", "#5A8CFF"]


def rubik_face(colors: list[str] | None = None, cell: float = 0.42) -> VGroup:
    colors = colors or ["#F2EFE9"] * 9
    face = VGroup()
    for r in range(3):
        for c in range(3):
            sq = Square(side_length=cell, stroke_color="#0A0A0A", stroke_width=2.0)
            sq.set_fill(colors[r * 3 + c], opacity=1.0)
            sq.move_to(np.array([(c - 1) * cell, (1 - r) * cell, 0]))
            face.add(sq)
    return face


def rubik_cube(cell: float = 0.42) -> VGroup:
    """A cube in cabinet projection: three faces, enough to turn one of them."""
    front = rubik_face([CUBE_FACE_COLORS[0]] * 9, cell)
    top = rubik_face([CUBE_FACE_COLORS[1]] * 9, cell)
    side = rubik_face([CUBE_FACE_COLORS[2]] * 9, cell)
    skew = np.array([[1, 0.5, 0], [0, 0.55, 0], [0, 0, 1]], dtype=float)
    top.apply_matrix(skew)
    top.next_to(front, UP, buff=0).shift(RIGHT * cell * 0.75)
    skew2 = np.array([[0.5, 0, 0], [0.55, 1, 0], [0, 0, 1]], dtype=float)
    side.apply_matrix(skew2)
    side.next_to(front, RIGHT, buff=0).shift(UP * cell * 0.75)
    cube = VGroup(front, top, side)
    cube.front, cube.top, cube.side = front, top, side
    # the affine map each face was drawn through, so a turn can be played back
    # in the face's own plane rather than in the picture plane
    cube.skew = {id(front): np.eye(3), id(top): skew, id(side): skew2}
    return cube


def turn_face(cube: VGroup, face: VGroup, angle: float, run_time: float = 0.8):
    """Turn one face of the cube, correctly, in cabinet projection.

    A face drawn through the skew ``S`` turns in its own plane by ``R``; on the
    page that reads as ``S R S⁻¹``.  Rotating the drawn parallelogram directly
    instead — which is what ``Rotate`` would do — tears the face off the cube.
    """
    from manim import UpdateFromAlphaFunc

    skew = cube.skew[id(face)]
    inverse = np.linalg.inv(skew)
    centre = face.get_center()
    start = face.copy()

    def spin(mob, alpha):
        a = angle * alpha
        rot = np.array(
            [[np.cos(a), -np.sin(a), 0.0], [np.sin(a), np.cos(a), 0.0], [0.0, 0.0, 1.0]]
        )
        fresh = start.copy()
        fresh.apply_matrix(skew @ rot @ inverse, about_point=centre)
        mob.become(fresh)

    return UpdateFromAlphaFunc(face, spin, run_time=run_time, rate_func=theme.EASE)


def chocolate_bar(cols: int = 6, rows: int = 4, cell: float = 0.62) -> VGroup:
    """Twenty-four squares, seen from above."""
    bar = VGroup()
    squares = VGroup()
    for r in range(rows):
        for c in range(cols):
            sq = RoundedRectangle(
                corner_radius=0.05,
                width=cell * 0.92,
                height=cell * 0.92,
                stroke_color="#2B1710",
                stroke_width=1.6,
                fill_color=theme.CHOCO,
                fill_opacity=1.0,
            )
            inner = RoundedRectangle(
                corner_radius=0.04,
                width=cell * 0.72,
                height=cell * 0.72,
                stroke_width=0,
                fill_color=theme.CHOCO_LIGHT,
                fill_opacity=0.55,
            ).move_to(sq)
            cellg = VGroup(sq, inner)
            cellg.move_to(np.array([(c - (cols - 1) / 2) * cell, ((rows - 1) / 2 - r) * cell, 0]))
            cellg.grid = (r, c)
            squares.add(cellg)
    bar.add(squares)
    bar.squares = squares
    bar.cols, bar.rows, bar.cell = cols, rows, cell
    return bar


class Scale(VGroup):
    """A weighing scale whose needle either settles, or never does."""

    def __init__(self, radius: float = 1.5):
        super().__init__()
        self.radius = radius
        self.dial = Arc(radius=radius, start_angle=PI * 0.15, angle=PI * 0.7, color=theme.INK_DIM, stroke_width=2)
        ticks = VGroup()
        for i in range(21):
            a = PI * 0.15 + PI * 0.7 * i / 20
            long = i % 5 == 0
            p0 = radius * np.array([np.cos(a), np.sin(a), 0])
            p1 = (radius - (0.18 if long else 0.09)) * np.array([np.cos(a), np.sin(a), 0])
            ticks.add(Line(p0, p1, color=theme.INK_DIM, stroke_width=2.0 if long else 1.0))
        self.ticks = ticks
        self.pivot = ORIGIN
        self.needle = Line(ORIGIN, radius * 0.92 * np.array([np.cos(PI / 2), np.sin(PI / 2), 0]),
                           color=theme.GOLD, stroke_width=3.0)
        self.cap = Dot(radius=0.07, color=theme.GOLD)
        pan = Line(LEFT * 0.9, RIGHT * 0.9, color=theme.INK_DIM, stroke_width=3).shift(UP * radius * 1.12)
        self.pan = pan
        self.add(self.dial, ticks, pan, self.needle, self.cap)

    def point_at(self, t: float):
        """``t`` in [0, 1] across the dial.

        The needle is anchored to the cap rather than to the world origin, so
        the instrument keeps working wherever the scene puts it.
        """
        pivot = self.cap.get_center()
        a = PI * 0.15 + PI * 0.7 * (1 - float(np.clip(t, 0.0, 1.0)))
        self.needle.put_start_and_end_on(
            pivot,
            pivot + self.radius * 0.92 * np.array([np.cos(a), np.sin(a), 0.0]),
        )
        return self


def dartboard(radius: float = 2.4, rings: int = 5) -> VGroup:
    board = VGroup()
    for i in range(rings, 0, -1):
        c = Circle(radius=radius * i / rings, color=theme.GHOST, stroke_width=1.4)
        c.set_fill("#0C0C0C", opacity=0.35 if i % 2 else 0.15)
        board.add(c)
    board.add(Circle(radius=radius * 0.06, color=theme.INK_DIM, stroke_width=1.6))
    return board


def orientation_icon(matrix, radius: float = 0.55, label: str | None = None) -> VGroup:
    """A small sphere showing *where a word leaves you*.

    Two books of the free library never open on the same page; two books of
    the Rubik library do.  The page is this icon, and it is computed from the
    genuine matrix product, so the claim is not staged — it is true.
    """
    from .space import View

    view = View(yaw=-0.7, pitch=0.30, scale=radius, distance=9.0)
    outline = Circle(radius=radius, color=theme.GHOST, stroke_width=1.4)
    axes = VGroup()
    m = np.asarray(matrix, dtype=float)
    for vec, col in (
        ([1.0, 0.0, 0.0], theme.C_A),
        ([0.0, 1.0, 0.0], theme.C_B),
        ([0.0, 0.0, 1.0], theme.C_E),
    ):
        tip = m @ np.array(vec)
        p_tip, _ = view.project_one(tip)
        p_org, _ = view.project_one(np.zeros(3))
        axes.add(Line(p_org, p_tip, color=col, stroke_width=2.6))
        axes.add(Dot(p_tip, radius=0.035, color=col))
    icon = VGroup(outline, axes)
    if label:
        tag = theme.mono(label, size=18, color=theme.INK_DIM)
        tag.next_to(outline, DOWN, buff=0.12)
        icon.add(tag)
    return icon


def open_book(word: str, matrix, width: float = 2.2, height: float = 1.6) -> VGroup:
    """A volume of the library, opened: the spine's word, and the page it holds."""
    col = theme.LETTER_COLORS.get(word[0] if word else "", theme.C_E)
    left = Rectangle(width=width / 2, height=height, stroke_color=col, stroke_width=1.6)
    left.set_fill("#0D0D0D", opacity=1.0)
    right = left.copy()
    left.shift(LEFT * width / 4)
    right.shift(RIGHT * width / 4)
    spine = Line(left.get_top() + RIGHT * width / 4, left.get_bottom() + RIGHT * width / 4,
                 color=col, stroke_width=1.4).set_opacity(0.6)
    title = theme.serif(theme.word_glyph(word), size=22, color=col)
    title.move_to(left)
    page = orientation_icon(matrix, radius=height * 0.30)
    page.move_to(right)
    return VGroup(left, right, spine, title, page)


def shoe(left: bool = True, scale: float = 1.0, color: str = theme.INK) -> VGroup:
    """A shoe, seen from the side.  A left shoe is not a right shoe — that is
    the whole content of Russell's example."""
    pts = [
        (-0.55, -0.18), (0.50, -0.18), (0.62, -0.05), (0.55, 0.10),
        (0.16, 0.16), (0.02, 0.42), (-0.34, 0.44), (-0.55, 0.22),
    ]
    body = Polygon(*[np.array([x, y, 0.0]) for x, y in pts], color=color, stroke_width=2.0)
    body.set_fill(color, opacity=0.10)
    sole = Line(np.array([-0.55, -0.18, 0]), np.array([0.62, -0.18, 0]),
                color=color, stroke_width=3.0)
    g = VGroup(body, sole)
    if not left:
        g.flip(UP)
    g.scale(scale)
    return g


def sock(scale: float = 1.0, color: str = theme.INK) -> VGroup:
    """A sock.  There is no left one.  That is the whole difficulty."""
    pts = [
        (-0.16, 0.48), (0.16, 0.48), (0.16, -0.02), (0.56, -0.10),
        (0.60, -0.34), (0.20, -0.42), (-0.16, -0.34),
    ]
    body = Polygon(*[np.array([x, y, 0.0]) for x, y in pts], color=color, stroke_width=2.0)
    body.set_fill(color, opacity=0.10)
    cuff = Line(np.array([-0.16, 0.36, 0]), np.array([0.16, 0.36, 0]),
                color=color, stroke_width=2.0).set_opacity(0.6)
    return VGroup(body, cuff).scale(scale)


def container(width: float = 1.5, height: float = 1.0, color: str = theme.GHOST) -> Rectangle:
    box = Rectangle(width=width, height=height, stroke_color=color, stroke_width=1.6)
    box.set_fill("#0A0A0A", opacity=1.0)
    return box


class Dial(VGroup):
    """One input or output of a matrix, drawn as an instrument."""

    def __init__(self, value: float = 0.0, radius: float = 0.42, color: str = theme.INK_DIM,
                 label: str | None = None):
        super().__init__()
        self.radius = radius
        self.face = Circle(radius=radius, color=color, stroke_width=1.8)
        ticks = VGroup(
            *[
                Line(
                    (radius - 0.09) * np.array([np.cos(a), np.sin(a), 0]),
                    radius * np.array([np.cos(a), np.sin(a), 0]),
                    color=color,
                    stroke_width=1.2,
                )
                for a in np.linspace(0, 2 * PI, 12, endpoint=False)
            ]
        )
        self.needle = Line(ORIGIN, np.array([0.0, radius * 0.78, 0.0]),
                           color=theme.GOLD, stroke_width=2.6)
        self.readout = theme.mono(f"{value:+.2f}", size=18, color=theme.INK)
        self.readout.next_to(self.face, DOWN, buff=0.10)
        self.add(self.face, ticks, self.needle, self.readout)
        if label:
            tag = theme.mono(label, size=18, color=color)
            tag.next_to(self.face, UP, buff=0.10)
            self.add(tag)
        self.set_value(value)

    def set_value(self, value: float):
        angle = PI / 2 - float(np.clip(value, -1.0, 1.0)) * PI * 0.75
        self.needle.put_start_and_end_on(
            ORIGIN + self.face.get_center(),
            self.face.get_center() + self.radius * 0.78 * np.array([np.cos(angle), np.sin(angle), 0]),
        )
        new = theme.mono(f"{value:+.2f}", size=18, color=theme.INK)
        new.move_to(self.readout)
        self.readout.become(new)
        return self
