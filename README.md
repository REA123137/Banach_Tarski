# Two Balls

Animations for the shooting script *Two Balls — the Banach-Tarski paradox,
explained in the order you actually understand it* (Iasmina & Rym, v4).

Every **ANIMATION** block of the script and every **ANIMATION IDEA** the script
attaches to a scene is coded here as an independently renderable
[manim](https://www.manim.community/) scene. Black background throughout, one
easing curve, one small palette, no LaTeX.

```bash
make deps          # cairo, pango, ffmpeg, manim
make preview       # every scene, fast
make QUALITY=-qh   # every scene, 1080p60
make list          # what can be rendered
make check         # verify the mathematics the film asserts
```

or, for one shot:

```bash
python3 -m manim -qh banach_tarski/scenes/s12_circle.py S12Circle
```

Output lands in `media/videos/<module>/<quality>/<Scene>.mp4`.

## Nothing on screen is staged

The script's rule — *no word is used before it has been defined* — has a
counterpart in the code: no claim is faked in the animation. The pieces of the
opening shot are moved by the real rotation matrices; a word's destination when
a generator is pushed in front of it is `freegroup.reduce("a" + w)`; the pages
of the free library are matrix products, and the two books of the *unfree*
library open on the same page because `aaaa` really is the identity there; the
number shown to the gate in scene 8 is the integer the induction of the real
proof watches; and when the batch `P₂` is rotated in scene 11, every point
lands exactly on the point whose itinerary is `reduce("a" + w)`.

`make check` verifies all of it and prints a line per claim. If a scene ever
starts telling the viewer something untrue, that command fails.

## Layout

```
banach_tarski/
  theme.py       palette, type, easing — the film's visual identity
  freegroup.py   words of F₂: reduction, the five piles, the librarian's push
  rotations.py   θ = arccos(1/3), the matrices, orbits, fixed-point axes
  space.py       a hand-rolled 3D stage: numpy projection + point clouds
  motifs.py      the machine, the Library of Babel, the hand of the axiom
  anim.py        the gestures the film repeats
  selfcheck.py   the receipt (make check)
  scenes/        one module per scene of the script
```

### Why a hand-rolled 3D stage

manim's own 3D camera projects every vertex of every bezier, which is slow and
unstable once a scene holds tens of thousands of points. The film needs the
opposite: a very large number of *dots*, moving smoothly, with depth fog, on
black. So `space.py` does the projection in numpy and hands the result to flat
2D mobjects — one `PMobject` per depth band, per-point colour, thousands of
points for free. A camera move is one `ValueTracker` away, and a ball of 26 000
points renders in real time.

One consequence worth knowing if you extend it: the cairo renderer writes
point-cloud pixels straight into the frame buffer and never blends, so an rgba
alpha is silently dropped on export. `Cloud.sync` premultiplies the alpha into
the colour instead — correct, because the film is drawn on pure black — and
discards points that have gone dark rather than letting them punch holes
through the dust behind them.

## The scenes

| # | module | scenes |
|---|--------|--------|
| 1 | `s01_trick` | `S01Trick` · `S01Squeeze` · `S01GhostReplay` · `S01HandOff` |
| 2 | `s02_statement` | `S02Statement` · `S02WordsDefend` |
| 3 | `s03_doubleable` | `S03Disjoint` · `S03Doubleable` · `S03Machine` · `S03MachineFull` |
| 4 | `s04_letters` | `S04RubikWord` · `S04TwoRotations` · `S04Reduce` · `S04Ribbon` |
| 5 | `s05_free_group` | `S05Catalogue` · `S05GroupAndFree` · `S05RubikNotFree` · `S05LibraryFlight` · `S05SamePage` |
| 6 | `s06_letter_trick` | `S06Columns` · `S06Examples` · `S06Doubling` · `S06Librarian` |
| 7 | `s07_points` | `S07WordsVsPoints` · `S07Matrices` · `S07Magnifier` · `S07DialMachine` |
| 8 | `s08_angle` | `S08Angle` · `S08Gate` |
| 9 | `s09_orbits` | `S09Orbit` · `S09Representatives` · `S09ShoesSocks` · `S09AxiomCard` · `S09ImpossibleHand` |
| 10 | `s10_fixed_points` | `S10Partition` · `S10FixedPoints` · `S10Removed` · `S10LongExposure` |
| 11 | `s11_sorting_points` | `S11Batches` · `S11Definitions` · `S11InkInWater` · `S11SecondPair` · `S11Equidecomposable` · `S11SplitScreen` |
| 12 | `s12_circle` | `S12Circle` · `S12Dartboard` · `S12Poles` · `S12Centre` |
| 13 | `s13_theorem` | `S13Chain` · `S13Replay` · `S13MachineOpens` |
| 14 | `s14_chocolate` | `S14Chocolate` · `S14Rigged` · `S14Volume` · `S14EndlessZoom` · `S14ScaleNeverSettles` · `S14Closing` |

### The three recurring motifs

The script allows exactly three analogies, each used twice, so the objects
carrying them are built once in `motifs.py` and imported by every scene that
needs them: the **machine with eight panels** (introduced in scene 3, one panel
drops per scene, fully open in scene 13), the **Library of Babel** (scene 5,
the librarian's push in scene 6, the impossible hand in scene 9), and the
**hand of the axiom of choice** (scene 9, and one second again over the
chocolate at the very end).

### Live action

The script's LIVE ACTION beats are shot separately. What is coded here is
everything between them, plus the animated stand-ins the plates cut against:
`S01HandOff` is the match-frame for the hand-off through the lens — same
gesture, same easing, same hold — so that the opening with the two balls and
the closing with the square of chocolate rhyme exactly.

## Type

The project uses Inter, EB Garamond and DejaVu Sans Mono when they are
installed, and degrades to DejaVu Sans when they are not, so a bare machine
still renders. All mathematics is set in Unicode: there is no LaTeX dependency
anywhere.

```bash
sudo apt-get install fonts-inter fonts-ebgaramond      # optional, recommended
```
