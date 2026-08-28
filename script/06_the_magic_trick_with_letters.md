# 06 · The magic trick, done with letters

**06:20 – 09:00** · 388 words · Iasmina 210 / Rym 178
**Purpose** — perform the whole doubling, on words, with worked examples.

**Scenes** `S06Columns · S06Examples · S06Doubling · S06Librarian`

---

**IASMINA**  I am going to sort the catalogue F₂ by the first letter of each word.
Write S(a) for the set of reduced words beginning with a. Likewise S(a⁻¹), S(b), S(b⁻¹).

> **ON SCREEN** — F₂ = {e} ⊔ S(a) ⊔ S(a⁻¹) ⊔ S(b) ⊔ S(b⁻¹)

**IASMINA**  A reduced word is either empty, or it begins with one of the four letters, and with exactly one. So those five piles cover the whole catalogue, with no overlap.

> **ANIMATION** — Four coloured columns of words, plus a tiny box for the empty word.

**RYM**  Now the experiment. I take the column S(a⁻¹), the words beginning with a⁻¹. And in front of each one, I stick an a.
Take one of them. The word a⁻¹b. Put an a in front: a a⁻¹ b. The a and the a⁻¹ cancel. What is left is b.

> **ON SCREEN** — a · (a⁻¹ b) = b

**IASMINA**  A word that began with a⁻¹ now begins with b.
Another one. a⁻¹a⁻¹. Put an a in front: what is left is a⁻¹. It began with a⁻¹, and it still does.
A third. a⁻¹b⁻¹a. Put an a in front: what is left is b⁻¹a. Now it begins with b⁻¹.

> **ANIMATION** — Each example writes itself, the two letters cancel in a fade, and the word physically jumps into its new column.

**RYM**  *challenge* — Try this one. I take a⁻¹bb, and I put an a in front.
> *silence, 3 s*
What is left is bb. It has joined the b column.
You can see what is happening. Adding an a erases the first letter of the word. And what ends up at the front is the second letter.
And that second letter can be anything at all, except an a⁻¹. Because if the word had started a⁻¹a⁻¹, those two would already have cancelled, and it would not be reduced.

**IASMINA**  *slow down* — So by putting an a in front of every word in a single column, we get exactly all the words that do not begin with a. That is three columns out of four, plus the empty word.

> **ON SCREEN** — a S(a⁻¹) = {e} ⊔ S(a⁻¹) ⊔ S(b) ⊔ S(b⁻¹)

**RYM**  And so, if I add back the column S(a), which I never touched, I have the entire catalogue.

> **ON SCREEN** — F₂ = S(a) ⊔ a S(a⁻¹)

**RYM**  Two columns out of four. The entire catalogue.
And the other two are still sitting there, untouched. So I do exactly the same thing with b.

> **ON SCREEN** — F₂ = S(b) ⊔ b S(b⁻¹)

**IASMINA**  *silence, 2 s* — Four piles. Two complete catalogues. And I added nothing: all I did was erase first letters.
That is the magic trick. All of it. And notice that it only worked because the group is free: had there been a single shortcut, two different words could have landed in the same place, and the whole sort would have collapsed.

## Animation notes

**The librarian pushes a shelf.** Four shelving units, one per first letter. The librarian pushes the a⁻¹ unit one notch to the right: every book sheds its first letter as it slides, and the unit overflows and fills the other three. Books that change shelf change binding colour in mid-air. — `S06Librarian`

**For the example the viewer must guess**, freeze frame: the book hangs in the air with a question mark on its spine, three seconds of silence, then it lands on the right shelf. — the freeze is in `S06Examples`.

Every jump in `S06Doubling` is computed, not choreographed: a word's destination is `freegroup.reduce("a" + word)` and it lands in the colour of that word's first letter.

## Bridge out

> “All that is left is to do the same thing to a ball. And that is where a new difficulty shows up.”
