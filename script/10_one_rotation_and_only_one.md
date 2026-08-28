# 10 · The problem: one rotation, and only one

**14:05 – 15:25** · 192 words · Iasmina 109 / Rym 83
**Purpose** — recall what a partition is, show why the axes and the centre break it.

**Scenes** `S10Partition · S10FixedPoints · S10Removed · S10LongExposure`

---

**RYM**  Let us recall what we are trying to build. A partition of the ball: pieces that do not overlap, and that together cover everything.

> **ON SCREEN** — L = P₁ ⊔ P₂ ⊔ P₃ ⊔ P₄ with Pᵢ ∩ Pⱼ = ∅ (i ≠ j)

**RYM**  For a point to land in one piece and only one, it must be writable in exactly one way as a rotation applied to a representative. If two different rotations gave the same point, that point would sit in two pieces at once, and it would no longer be a partition.
And there are points that do precisely that.

> **ANIMATION** — A rotation about an axis. The sphere turns, but the two points where the axis pierces it stay perfectly still. They flash red. Then dozens of axes are superimposed, each with its pair of red points.

**IASMINA**  Take a point lying on the axis of a rotation. That rotation does not move it. It stays where it is. So “do nothing” and “apply this rotation” give the same result: two different words, one single point.
The centre of the ball has exactly the same problem, only worse: no rotation ever moves it.
So we set them aside. We write D for the set of all fixed points of rotations in G, and we remove the centre as well.

> **ON SCREEN** — L = {(x,y,z) : x² + y² + z² ≤ 1},  L₀ = L ∖ {(0,0,0)},  D = {p ∈ L₀ : ρ(p) = p for some ρ ∈ G, ρ ≠ Id}

**IASMINA**  So we work on L₀ with D removed. And I promise you now: we will get all of it back, the centre and the axes, before the end.

## Animation notes

**Long exposure.** Film the rotating sphere with light trails, like a night photograph. Every point leaves a streak. Two points, and only two, stay sharp: the fixed points. Then superimpose twenty different rotations, and the screen becomes a sky of star trails with, here and there, perfectly motionless stars. The idea of a fixed point lands without a word. — `S10LongExposure`

The axes are the genuine ones: each is the eigenvector of eigenvalue 1 of a short word's matrix.

## Bridge out

> “On what is left, the sort works perfectly. Let us do it.”
