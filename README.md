# Banach–Tarski — the animations

Every animation and animation idea from a two-voice explainer script on the
Banach–Tarski paradox, coded as a 20-chapter [Manim](https://www.manim.community/)
film. Black canvas throughout, one visual language, no LaTeX toolchain required.

> **On the script.** The PDF referenced in the brief
> (`BanachTarski_script_v7_2voices_EN.pdf`) was a local path on your Mac and was
> never uploaded to this session, so the chapter list is a reconstruction of the
> canonical beats of a two-voice Banach–Tarski script rather than a transcription
> of v7. The narration lines in each scene are placeholders in the two-voice
> form (`A` / `B`) and are meant to be replaced with your actual copy — see
> [Re-syncing to your script](#re-syncing-to-your-script).

## Running order

| # | Scene | Chapter | What it animates |
|---|-------|---------|------------------|
| 01 | `ColdOpen` | Cold open | A point of light becomes a ball, the ball becomes two |
| 02 | `TheClaim` | The claim | Rigid motions only; five pieces; `V = 2V` struck through |
| 03 | `HilbertHotel` | Hilbert's hotel | `n → n+1` for one guest, `n → 2n` for a busload |
| 04 | `SameSize` | The same size | Bijection wiring diagrams: ℕ↔2ℕ, ℕ↔ℤ |
| 05 | `DoublingTheHotel` | Doubling the hotel | Odd/even split; each half fills a whole hotel |
| 06 | `RotationsDontCommute` | Turns that don't commute | `ab` vs `ba` on two marked spheres |
| 07 | `FreeGroup` | The free group | Words, cancellation, freeness, `4·3ⁿ⁻¹` growth |
| 08 | `CayleyTree` | The Cayley graph | The 4-valent tree grown ring by ring, then a push-in |
| 09 | `ParadoxInTheGroup` | One group, two groups | **The paradoxical decomposition itself** |
| 10 | `GroupOnTheSphere` | The group on the sphere | Two turns by `arccos(1/3)`; an orbit sprays out |
| 11 | `OrbitsAndChoice` | Orbits and choice | Orbits partition S²; the Axiom of Choice picks `M` |
| 12 | `PolesAndTheHotelTrick` | The fixed points | The countable pole set `D`, removed and reabsorbed |
| 13 | `SphereToBall` | Surface to solid | Radial extension, and the circle that eats the centre |
| 14 | `ASetWithNoLength` | A set with no length | Vitali's set; the sum is 0 or ∞ |
| 15 | `FourWishes` | Four wishes about volume | Every set / additive / invariant / normalised — pick three |
| 16 | `WhatThePiecesLookLike` | What the pieces look like | A cloud with no smallest scale, zoomed 100× |
| 17 | `FivePieces` | The assembly | Exploded view → two balls; Robinson's minimality |
| 18 | `WhyNotInThePlane` | Why the plane is safe | Plane rotations commute; the dimension ladder |
| 19 | `RealityCheck` | So why not gold? | Atoms, unmeasurable pieces, the chain of ideas |
| 20 | `Outro` | Outro | Back to the two balls, and the card |

## Rendering

```bash
pip install -r requirements.txt        # needs pkg-config, cairo and pango headers
python render.py                       # everything, 1080p60
python render.py -q l                  # fast draft pass
python render.py --only s09 s10        # selected chapters
python render.py --stitch              # concatenate into out/banach_tarski_*.mp4
python render.py --list                # print the running order
```

Individual scenes go through Manim directly:

```bash
python -m manim -qh banach_tarski/scenes/s09_paradox_tree.py ParadoxInTheGroup
```

If your system has no `ffmpeg`, `imageio-ffmpeg` ships a static one — link it
onto `PATH` (`ln -s "$(python -c 'import imageio_ffmpeg,sys;
sys.stdout.write(imageio_ffmpeg.get_ffmpeg_exe())')" /usr/local/bin/ffmpeg`).

## How it is put together

```
banach_tarski/
  style.py       palette, type, black-canvas furniture, caption bar, scene bases
  mathkit.py     free-group words, Cayley layout, the two rotations, orbits
  treekit.py     drawing the Cayley graph: batched edges, vertex clouds
  particles.py   Dust point clouds, morphing, depth shading, rotation
  film.py        the running order
  scenes/        one file per chapter
render.py        the driver
manim.cfg        1080p60, pure black background
```

**Look.** One palette in `style.py`; nothing hard-codes a colour. Every scene
sits on pure black with a soft vignette and a faint starfield, and speaks
through a two-voice lower third (`self.say("A", …)` / `self.say("B", …)`).
`SAFE_BOTTOM` marks the line below which the caption bar owns the frame.

**Dust.** Sets of points are drawn as point clouds rather than shapes, because
that is what the pieces of the decomposition actually are. Manim's point-cloud
renderer writes pixels straight into the frame buffer instead of blending them,
so a low alpha punches a transparent hole rather than dimming a particle —
`particles.py` therefore carries opacity premultiplied in the RGB channels and
pins alpha at 1. Depth shading and a multiplicative specular lift are what make
a cloud read as a ball instead of a disc of confetti.

**The mathematics is computed, not mimed.** The vertices in chapter 09 fly to
the positions of their actual products: targets come from `mk.multiply`, and
`a·S(a⁻¹) = F ∖ S(a)` is a fact about the layout, not a hand-placed animation.
The rotations in chapters 06 and 10 are the standard free pair (rotation by
`arccos(1/3)` about the x- and z-axes); the poles in chapter 12 are computed as
eigenvectors of each word's matrix.

**No LaTeX.** All type goes through Pango with Unicode maths characters
(`a⁻¹`, `ℕ`, `⊔`, `∪`), so nothing needs a TeX install. `FONT_STACK` in
`style.py` prefers Inter or Manrope if present and falls back to DejaVu Sans.

## Re-syncing to your script

The narration is the only thing that should need touching:

1. Each scene calls `self.say(voice, text, hold=…)` in order. Replace `text`
   with your v7 line, keep `voice` as `"A"` or `"B"`, and set `hold` to the
   line's real duration so the picture matches the read.
2. `chapter("07", "One group, two groups", …)` sets the card; renumber to match
   your section order.
3. If v7 has a beat these chapters miss, the toolkit is the point — `Dust`,
   `TreeLayout` and the scene bases are meant to be composed into new scenes.
4. `banach_tarski/film.py` is the single running order; add or reorder there and
   `render.py` follows.

Timings are currently set for reading aloud at a steady pace; a chapter runs
roughly 40–70 seconds.
