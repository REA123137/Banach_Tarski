"""
06 - Turns that don't commute.

Two rotations of a sphere, applied in both orders.  In the plane the answer
would be the same either way; on a sphere it is not, and that failure is the
crack the paradox climbs through.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustRotate
from banach_tarski import mathkit as mk

N = 1500
R = 1.25
CAPS = ((np.array([1.0, 0, 0]), CORAL), (np.array([0, 1.0, 0]), MINT),
        (np.array([0, 0, 1.0]), CYAN))


def marked_sphere(shift=ORIGIN, n=N, radius=R, seed=0):
    """
    A dust sphere carrying three orthogonal coloured caps.

    A plain sphere looks identical however you turn it, so the caps are what
    make a rotation visible at all.  Base and caps are separate clouds: the
    caps get bigger, brighter particles and so stay readable against the body.
    """
    pts = mk.random_sphere(n, radius, seed=seed)
    dirs = pts / radius
    cap_idx, cap_cols = [], []
    for i, d in enumerate(dirs):
        for axis, col in CAPS:
            if d @ axis > np.cos(34 * DEGREES):
                cap_idx.append(i)
                cap_cols.append(col)
                break
    cap_idx = np.array(cap_idx, dtype=int)
    base_idx = np.setdiff1d(np.arange(n), cap_idx)
    off = np.asarray(shift, dtype=float)
    base = Dust(pts[base_idx] + off, "#5A5347", size=2.0)
    caps = Dust(pts[cap_idx] + off, cap_cols, size=5.0)
    return Group(base, caps)


def turn(ball: Group, matrix, **kw):
    """Rotate a marked sphere's body and caps together, about its own centre."""
    about = ball[0].pts.mean(axis=0)
    return [DustRotate(layer, matrix, about=about, **kw) for layer in ball]


class RotationsDontCommute(BT3DScene):
    def construct(self):
        self.set_camera_orientation(phi=66 * DEGREES, theta=-90 * DEGREES, zoom=0.95)

        left = marked_sphere(LEFT * 2.85)
        right = marked_sphere(RIGHT * 2.85)
        for ball in (left, right):
            for layer in ball:
                layer.depth_shade(self, radius=R, floor=0.22)

        head = T("does the order matter?", size=H3, color=PAPER).move_to(UP * 3.30)
        lab_l = T("first a, then b", size=SMALL, color=GOLD).move_to(LEFT * 3.4 + UP * 2.45)
        lab_r = T("first b, then a", size=SMALL, color=CYAN).move_to(RIGHT * 3.4 + UP * 2.45)
        for m in (head, lab_l, lab_r):
            self.label(m)

        self.play(FadeIn(head, shift=DOWN * 0.15), run_time=0.7)
        self.play(FadeIn(left), FadeIn(right), run_time=1.0)
        self.play(FadeIn(lab_l, shift=UP * 0.1), FadeIn(lab_r, shift=UP * 0.1), run_time=0.6)

        self.say("A", "Two rotations of a sphere. Call them a and b. "
                      "Same two turns on both copies - only the order differs.", hold=2.8)

        # -- turn one -----------------------------------------------------------
        step_l = T("a", size=BODY, color=GOLD, weight=BOLD).move_to(LEFT * 3.4 + DOWN * 1.95)
        step_r = T("b", size=BODY, color=CYAN, weight=BOLD).move_to(RIGHT * 3.4 + DOWN * 1.95)
        self.label(step_l)
        self.label(step_r)
        self.play(FadeIn(step_l, scale=1.4), FadeIn(step_r, scale=1.4), run_time=0.4)
        self.play(*turn(left, mk.R_a), *turn(right, mk.R_b), run_time=2.0)
        self.wait(0.3)

        # -- turn two -----------------------------------------------------------
        step_l2 = T("a  then  b", size=BODY, color=PAPER, weight=BOLD).move_to(step_l)
        step_r2 = T("b  then  a", size=BODY, color=PAPER, weight=BOLD).move_to(step_r)
        self.label(step_l2)
        self.label(step_r2)
        self.play(FadeOut(step_l), FadeOut(step_r), FadeIn(step_l2), FadeIn(step_r2),
                  run_time=0.4)
        self.play(*turn(left, mk.R_b), *turn(right, mk.R_a), run_time=2.0)
        self.wait(0.6)

        # -- they disagree ------------------------------------------------------
        neq = T("≠", size=H1, color=CORAL, weight=BOLD).move_to(ORIGIN)
        self.label(neq)
        self.play(FadeIn(neq, scale=1.6), run_time=0.6)
        self.say("B", "Different. The two spheres do not agree, and no amount of "
                      "further turning will make a b equal b a.", hold=2.8)

        self.play(FadeOut(neq), run_time=0.4)
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(2.0)
        self.stop_ambient_camera_rotation()

        self.say("A", "In the plane, order never matters - two turns about the same "
                      "centre always add up.", hold=2.6)
        self.say("B", "In three dimensions the axes get in each other's way. "
                      "That is the whole difference.", hold=2.8)

        self.play(FadeOut(head), run_time=0.35)
        formula = T("a b   ≠   b a", size=H3, color=PAPER).move_to(UP * 3.30)
        self.label(formula)
        self.play(FadeIn(formula, shift=UP * 0.12), run_time=0.7)
        self.wait(1.0)

        self.play(
            FadeOut(left), FadeOut(right), FadeOut(head), FadeOut(lab_l), FadeOut(lab_r),
            FadeOut(step_l2), FadeOut(step_r2), FadeOut(formula),
            FadeOut(self._caption), run_time=1.0,
        )
