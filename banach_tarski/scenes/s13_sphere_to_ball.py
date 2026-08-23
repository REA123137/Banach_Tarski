"""
13 - From the surface to the solid.

The paradox is built on the sphere's surface.  Getting it into the solid ball
takes one line: sweep each piece along the radius.  That misses the exact
centre, which is then absorbed the same way a hotel absorbs one more guest.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *

from banach_tarski.style import *
from banach_tarski.particles import Dust, DustMorph, DustRotate, DustRecolor
from banach_tarski import mathkit as mk

R = 1.9
N = 3600


class SphereToBall(BT3DScene):
    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-90 * DEGREES, zoom=0.95)

        title = T("surface to solid", size=H3, color=PAPER).move_to(UP * 3.30)
        self.label(title)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)

        # -- the sphere, in four pieces -------------------------------------------
        rng = np.random.default_rng(9)
        dirs = mk.random_sphere(N, 1.0, seed=13)
        labels = rng.integers(0, 4, size=N)
        colors = [PIECE_COLORS[i] for i in labels]

        shell = Dust(dirs * R, colors, size=2.8)
        shell.depth_shade(self, radius=R, floor=0.16)
        self.play(FadeIn(shell), run_time=1.0)
        self.say("A", "Everything so far happened on the surface. Here are the "
                      "pieces, on the skin of the sphere.", hold=2.8)

        # -- one radius ---------------------------------------------------------------
        p = dirs[0] * R
        ray = Line(ORIGIN, p).set_stroke(PAPER, 2.4, opacity=0.9)
        tip = Dust(p.reshape(1, 3), PAPER, size=13.0)
        self.play(Create(ray), FadeIn(tip), run_time=0.9)
        self.say("B", "Take one point, and drag it straight in toward the centre.",
                 hold=2.2)

        trail = Dust(np.linspace(p * 0.06, p, 40), PAPER, size=4.0)
        self.play(FadeIn(trail), run_time=0.8)
        self.say("A", "Every point on that line gets the same label as the point on "
                      "the surface it came from.", hold=2.8)

        # -- fill the ball --------------------------------------------------------------
        self.play(FadeOut(ray), FadeOut(tip), FadeOut(trail), run_time=0.6)

        radii = (rng.random(N) ** (1 / 3)) * 0.985 + 0.015
        solid = dirs * (radii[:, None] * R)
        self.play(DustMorph(shell, solid, stagger=0.6, run_time=2.8))
        self.say("B", "Do it for every point at once, and the four pieces of the "
                      "surface become four pieces of the whole ball.", hold=3.0)

        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(2.0)
        self.stop_ambient_camera_rotation()

        # -- the missing centre -----------------------------------------------------------
        self.say("A", "With one point missing. The very centre belongs to no radius.",
                 hold=2.6)

        self.play(DustRecolor(shell, [c for c in colors], opacity=0.20, run_time=0.9))
        centre = glow_dot(ORIGIN, PAPER, radius=0.055, reach=7)
        self.add_fixed_in_frame_mobjects(centre)
        self.play(FadeIn(centre, scale=0.4), run_time=0.8)

        # A circle inside the ball, through the centre, rotated by an angle whose
        # multiples never repeat: the hotel, one last time.
        theta = np.arange(1, 46) * 1.0
        circle_pts = np.stack(
            [0.62 * np.cos(theta) + 0.62, np.zeros_like(theta), 0.62 * np.sin(theta)],
            axis=1,
        )
        orbit = Dust(circle_pts, CYAN, size=8.0)
        guide = Circle(radius=0.62).rotate(PI / 2, axis=RIGHT).shift(RIGHT * 0.62)
        guide.set_stroke(CYAN, 1.8, opacity=0.5)

        self.play(Create(guide), FadeIn(orbit), run_time=1.1)
        self.say("B", "Draw a circle inside the ball that passes through the centre, "
                      "and turn it by an angle that never comes back round.", hold=3.2)

        step = np.array([[np.cos(1.0), 0, np.sin(1.0)], [0, 1, 0],
                         [-np.sin(1.0), 0, np.cos(1.0)]])
        for _ in range(2):
            self.play(DustRotate(orbit, step, about=np.array([0.62, 0, 0]),
                                 run_time=1.3))
        self.play(FadeOut(centre, scale=0.4), run_time=0.7)

        self.say("A", "Each point steps to the next. The centre is swallowed, and "
                      "nothing is left over.", hold=2.8)

        self.play(DustRecolor(shell, colors, run_time=1.0), FadeOut(orbit),
                  FadeOut(guide), run_time=1.0)

        done = T("a solid ball, in five pieces", size=SMALL, color=MINT)
        done.move_to(DOWN * 2.30)
        self.label(done)
        self.play(FadeIn(done, shift=UP * 0.1), run_time=0.7)
        self.say("B", "Four pieces from the surface, plus the circle that mops up "
                      "the centre. Five in total.", hold=3.0)

        self.play(FadeOut(shell), FadeOut(title), FadeOut(done),
                  FadeOut(self._caption), run_time=1.1)
