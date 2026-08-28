"""Reusable gestures.

The film repeats a small number of moves — a statement that writes itself, a
counter-example that gets struck through, two letters that annihilate, a word
that jumps column.  They live here so that every scene performs them at
exactly the same tempo.
"""

from __future__ import annotations

import numpy as np
from manim import (
    AnimationGroup,
    Circle,
    Create,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    LEFT,
    LaggedStart,
    Line,
    Mobject,
    RIGHT,
    Succession,
    Transform,
    UP,
    Uncreate,
    VGroup,
    Wait,
    Write,
    rate_functions,
)

from . import theme


# --------------------------------------------------------------------------
# On-screen blocks
# --------------------------------------------------------------------------


def stack(*mobs: Mobject, buff: float = 0.42, center: bool = True) -> VGroup:
    g = VGroup(*mobs).arrange(DOWN, buff=buff)
    if center:
        g.move_to(np.zeros(3))
    return g


def statement(lines: list[str], size: float = 40, color: str = theme.INK, buff: float = 0.44) -> VGroup:
    return stack(*[theme.body(line, size=size, color=color) for line in lines], buff=buff)


def write_lines(scene, group: VGroup, per_line: float = 0.9, lag: float = 0.55, wait: float = 0.0):
    """The house way of putting text up: one line at a time, never all at once."""
    scene.play(
        LaggedStart(
            *[Write(line, run_time=per_line) for line in group],
            lag_ratio=lag,
        )
    )
    if wait:
        scene.wait(wait)


def reveal(mob: Mobject, run_time: float = 0.8, shift=None):
    return FadeIn(mob, shift=shift if shift is not None else UP * 0.18, run_time=run_time, rate_func=theme.EASE_OUT)


def dismiss(mob: Mobject, run_time: float = 0.6, shift=None):
    return FadeOut(mob, shift=shift if shift is not None else DOWN * 0.18, run_time=run_time, rate_func=theme.EASE_IN)


def swap(scene, old: Mobject, new: Mobject, run_time: float = 0.9):
    new.move_to(old)
    scene.play(
        FadeOut(old, shift=UP * 0.2, run_time=run_time * 0.6),
        FadeIn(new, shift=UP * 0.2, run_time=run_time * 0.6),
    )


# --------------------------------------------------------------------------
# Refusal
# --------------------------------------------------------------------------


def strike(mob: Mobject, color: str = theme.REFUSE, pad: float = 0.16, width: float = 5.0) -> Line:
    """The red rule that crosses out a counter-example.  Only ever red."""
    return Line(
        mob.get_left() + LEFT * pad,
        mob.get_right() + RIGHT * pad,
        color=color,
        stroke_width=width,
    ).move_to(mob)


def refuse(scene, mob: Mobject, run_time: float = 0.7, hold: float = 0.35):
    """Strike a thing out and dim it.  The definition is a machine that refuses."""
    bar = strike(mob)
    scene.play(Create(bar, run_time=run_time, rate_func=theme.SNAP))
    scene.play(
        mob.animate(run_time=0.4).set_opacity(0.35),
        bar.animate(run_time=0.4).set_stroke(opacity=0.7),
    )
    if hold:
        scene.wait(hold)
    return bar


# --------------------------------------------------------------------------
# Cancellation: the one violent moment of the film
# --------------------------------------------------------------------------


def annihilate(scene, left: Mobject, right: Mobject, flash_color: str = "#FFFFFF"):
    """Two letters slam together, one white flash, nothing left."""
    midpoint = (left.get_center() + right.get_center()) / 2
    scene.play(
        left.animate(run_time=0.22, rate_func=rate_functions.rush_into).move_to(midpoint),
        right.animate(run_time=0.22, rate_func=rate_functions.rush_into).move_to(midpoint),
    )
    spark = Dot(point=midpoint, radius=0.05, color=flash_color)
    scene.add(spark)
    scene.play(
        Flash(
            midpoint,
            color=flash_color,
            line_length=0.22,
            num_lines=14,
            flash_radius=0.34,
            run_time=0.32,
        ),
        FadeOut(left, run_time=0.16),
        FadeOut(right, run_time=0.16),
        FadeOut(spark, run_time=0.30),
    )


def cancel_in_word(scene, letters: VGroup, index: int, reflow_to=None, buff: float = 0.18):
    """Collide ``letters[index]`` with ``letters[index+1]`` and close the gap."""
    left, right = letters[index], letters[index + 1]
    annihilate(scene, left, right)
    remaining = VGroup(*[m for i, m in enumerate(letters) if i not in (index, index + 1)])
    if len(remaining) == 0:
        return remaining
    target = remaining.copy().arrange(RIGHT, buff=buff)
    target.move_to(reflow_to if reflow_to is not None else letters.get_center())
    scene.play(
        *[m.animate.move_to(t) for m, t in zip(remaining, target)],
        run_time=0.45,
        rate_func=theme.EASE,
    )
    return remaining


# --------------------------------------------------------------------------
# Emphasis
# --------------------------------------------------------------------------


def pulse(mob: Mobject, scale: float = 1.10, run_time: float = 0.7, color: str | None = None):
    anims = [mob.animate(run_time=run_time / 2, rate_func=theme.EASE).scale(scale)]
    return Succession(
        mob.animate(run_time=run_time / 2, rate_func=theme.EASE).scale(scale),
        mob.animate(run_time=run_time / 2, rate_func=theme.EASE).scale(1 / scale),
    )


def halo(mob: Mobject, color: str, run_time: float = 0.9, radius: float = 0.4):
    ring = Circle(radius=radius, color=color, stroke_width=3).move_to(mob)
    return Succession(
        Create(ring, run_time=run_time * 0.4),
        AnimationGroup(
            ring.animate(run_time=run_time * 0.6).scale(1.7).set_stroke(opacity=0),
        ),
    )


def countdown_silence(scene, seconds: float, label: str | None = None):
    """The script's ``silence 3 s``: real silence, but the frame keeps breathing."""
    if label:
        tag = theme.caption(label, size=22)
        theme.foot(tag)
        scene.play(FadeIn(tag, run_time=0.4))
        scene.wait(max(seconds - 0.8, 0.1))
        scene.play(FadeOut(tag, run_time=0.4))
    else:
        scene.wait(seconds)


def bridge(scene, text: str, run_time: float = 1.6, hold: float = 0.7):
    """The thirteen bridges.  Never cut, always the same treatment."""
    line = theme.body(text, size=30, color=theme.INK_DIM)
    theme.foot(line)
    scene.play(FadeIn(line, shift=UP * 0.15, run_time=run_time * 0.4))
    scene.wait(hold)
    scene.play(FadeOut(line, run_time=run_time * 0.35))


def title_card(scene, index: int, title: str, subtitle: str | None = None, hold: float = 1.2):
    """Opens every scene: the number, the title, a rule that draws itself."""
    num = theme.mono(f"{index:02d}", size=26, color=theme.GHOST)
    name = theme.display(title, size=54)
    rule = theme.rule(width=max(name.width, 4.0) + 1.0)
    block = VGroup(num, name, rule).arrange(DOWN, buff=0.34)
    if subtitle:
        sub = theme.caption(subtitle, size=24)
        block.add(sub)
        block.arrange(DOWN, buff=0.34)
    block.move_to(np.zeros(3))
    scene.play(
        FadeIn(num, run_time=0.5),
        Write(name, run_time=1.1),
        lag_ratio=0.2,
    )
    scene.play(Create(rule, run_time=0.7, rate_func=theme.EASE))
    if subtitle:
        scene.play(FadeIn(sub, run_time=0.5))
    scene.wait(hold)
    scene.play(FadeOut(block, run_time=0.7, rate_func=theme.EASE_IN))
    return block
