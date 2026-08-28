# 08 · The right angle

**10:20 – 11:15** · 134 words · Iasmina 67 / Rym 67
**Purpose** — say what the angle buys us, and move on.

**Scenes** `S08Angle · S08Gate`

---

**RYM**  All that is left is to choose the angle of our two rotations. And here we must be precise, because everything depends on it.
Remember what we require: the group must be free. No shortcuts. Translated into rotations, no sequence of rotations, however long, may bring the sphere back to exactly where it started.
The angle that does this is the one whose cosine is a third.

> **ON SCREEN** — The angle writes itself large, alone: θ = arccos(1/3). Two seconds.

**IASMINA**  *direct* — It can be proved. It is an induction on the length of the words, it turns on divisibility by three, and honestly it is not the interesting part of this story. I will give you the result, which is all we need.

> **ON SCREEN** — The two rotations by arccos(1/3) about two perpendicular axes generate a free group.

**IASMINA**  In other words: our catalogue of words now exists as rotations. Every word is a real motion, and two different words are two different motions.

## Animation notes

**The gate.** Since we are not doing the proof, we must make it felt in ten seconds. Centre screen, a gate labelled “divisible by 3?”. Words stream past, faster and faster; for each one a number steps up to the gate, which shows NO. Dozens, then hundreds, without exception. Then the gate is shown the one number that would allow a return to the start: it is divisible by three, and the gate refuses it too. The viewer has not seen the proof, but has seen why it works. — `S08Gate`

The numbers are the real invariant. Take (1, 0, 0); a reduced word whose first applied letter is a or a⁻¹ sends it to a point whose second coordinate is exactly b·√2 / 3ⁿ with b a whole number, and b is never divisible by three. `make check` asserts it over the 2 186 words up to length seven.

## Bridge out

> “We have our motions. Now the pieces they will move.”
