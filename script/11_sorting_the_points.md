# 11 · Sorting the points, batch by batch

**15:25 – 18:35** · 457 words · Iasmina 179 / Rym 278
**Purpose** — redo the letter sort exactly, on points, and spell out the unions.

**Scenes** `S11Batches · S11Definitions · S11InkInWater · S11SecondPair · S11Equidecomposable · S11SplitScreen`

---

**RYM**  Here we are. And let me say straight away: we are not going to invent anything. We are redoing, word for word, exactly what we did earlier with the letters. The only difference is that we sort points instead of words.
Remember: every point is written in exactly one way as a sequence of motions applied to a representative. So every point inherits a first letter, the one of its sequence. Exactly like a word.

> **ON SCREEN** — S(A)M = { ρ(m) : m ∈ M, ρ begins with A }

**IASMINA**  The batch S(A)M is every point whose itinerary begins with A. And likewise with S(A⁻¹), with S(B), with S(B⁻¹). Four batches, one per first letter.

> **ANIMATION** — On the sphere, the dust of one orbit colours itself in four, each point taking the colour of the first letter of its itinerary. The representative stays white.

**IASMINA**  The white points are left over: the representatives themselves. Their itinerary is empty, they begin with no letter at all. We put them in the first batch, together with the queue X that acts as a buffer, exactly as we did with the empty word earlier.

> **ON SCREEN** — X = A⁻¹M ∪ A⁻²M ∪ A⁻³M ∪ ⋯
> P₁ = S(A)M ∪ M ∪ X,  P₂ = S(A⁻¹)M ∖ X,  P₃ = S(B)M,  P₄ = S(B⁻¹)M

**RYM**  *beat* — And now let us watch what happens when we put a rotation in front of a whole batch.
Take the second batch, P₂. Every one of its points has an itinerary beginning with A⁻¹. I apply A to the whole batch, which means I add an A to the front of every itinerary.
The A cancels the A⁻¹. The itinerary loses its first letter. And what ends up at the front is the second letter, which can be anything at all except an A⁻¹, since otherwise those two would already have cancelled.

**IASMINA**  So the points of A P₂ have itineraries beginning with A, or B, or B⁻¹. Which is precisely batches two, three and four.

> **ON SCREEN** — A P₂ = P₂ ∪ P₃ ∪ P₄

**IASMINA**  Now add the first batch, which we never touched, and you have the whole thing.

> **ON SCREEN** — P₁ ∪ A P₂ = L₀ ∖ D

**RYM**  And we do it again with B, on the fourth batch. All of its points have itineraries beginning with B⁻¹. We add a B in front, it cancels the B⁻¹, and what appears at the front is anything except a B⁻¹.
So B P₄ holds the points beginning with A, with A⁻¹, or with B⁻¹: batches one, two and four.

> **ON SCREEN** — B P₄ = P₁ ∪ P₂ ∪ P₄, so P₃ ∪ B P₄ = L₀ ∖ D

**IASMINA**  *slow down* — Look at what we have just obtained.
The first batch and the second, between them, give back the whole thing, provided you rotate the second. And the third and the fourth do exactly the same on their side.
Four disjoint batches. Two complete copies. And it is the same sentence, word for word, as the one we wrote about the letters.
*beat* — We can finally define the word promised at the start.

> **ON SCREEN** — Two sets are equidecomposable if one can be partitioned into finitely many parts which can be reassembled into the other by rigid motions alone.

**RYM**  In plain English: two sets are equidecomposable if one becomes the other by cutting and moving, deforming nothing.
So we have just proved that the ball, minus its centre and the poles of its rotations, is equidecomposable with two copies of itself.
All that is missing are the points we set aside.

## Animation notes

**Split screen, letters and points.** This is the key to the scene: on the left the four columns of words from the letters scene, on the right the four batches of points on the sphere. Both animations replay in parallel, frame for frame, perfectly synchronised. When the column S(a⁻¹) slides on the left, the batch P₂ rotates on the right, at the same instant. — `S11SplitScreen`

**And for the union itself, ink in water**: the colour of P₂ does not jump from batch to batch, it spreads until it covers the regions of the other two colours. You physically watch a quarter become three quarters. — `S11InkInWater`

Nothing here is staged. A real orbit is generated, every point remembers the word that produced it, and when P₂ is rotated by A each point lands exactly on the point whose word is `reduce("a" + w)`. The recolouring *is* that landing.

## Bridge out

> “And those points, we are going to get back. This is the most elegant part of the whole proof.”
