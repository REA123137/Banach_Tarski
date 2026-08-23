"""
The running order.

One list, used by the render driver, the README and anything else that needs
to know what the film is made of.  ``key`` is the module, ``scene`` the class.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chapter:
    key: str
    scene: str
    title: str
    beat: str


FILM: list[Chapter] = [
    Chapter("s01_cold_open", "ColdOpen", "Cold open",
            "One ball of light becomes two, with no explanation offered."),
    Chapter("s02_the_claim", "TheClaim", "The claim",
            "The statement pinned down: five pieces, rigid motions only, V = 2V."),
    Chapter("s03_hilbert_hotel", "HilbertHotel", "Hilbert's hotel",
            "A full hotel takes one more guest, then infinitely many."),
    Chapter("s04_same_size", "SameSize", "The same size",
            "Bijections as wiring diagrams: N with 2N, N with Z."),
    Chapter("s05_doubling", "DoublingTheHotel", "Doubling the hotel",
            "Split the guests in two; each half fills a hotel. One in, two out."),
    Chapter("s06_rotations", "RotationsDontCommute", "Turns that don't commute",
            "ab and ba on two marked spheres, side by side."),
    Chapter("s07_free_group", "FreeGroup", "The free group",
            "Words, cancellation, freeness, and the 4·3^(n-1) explosion."),
    Chapter("s08_cayley_tree", "CayleyTree", "The Cayley graph",
            "The infinite four-way tree, grown ring by ring, then pushed into."),
    Chapter("s09_paradox_tree", "ParadoxInTheGroup", "One group, two groups",
            "The paradoxical decomposition itself - the load-bearing scene."),
    Chapter("s10_group_on_sphere", "GroupOnTheSphere", "The group on the sphere",
            "Two turns by arccos(1/3); one point's orbit sprays across the sphere."),
    Chapter("s11_orbits_choice", "OrbitsAndChoice", "Orbits and choice",
            "Orbits partition the sphere; picking one point from each needs AC."),
    Chapter("s12_poles", "PolesAndTheHotelTrick", "The fixed points",
            "Countably many poles are removed, then absorbed by the hotel trick."),
    Chapter("s13_sphere_to_ball", "SphereToBall", "Surface to solid",
            "Radial extension, and the circle that mops up the centre."),
    Chapter("s14_vitali", "ASetWithNoLength", "A set with no length",
            "Vitali's set: countably many copies, total 0 or infinity."),
    Chapter("s15_measure", "FourWishes", "Four wishes about volume",
            "Every set, additive, invariant, normalised - pick any three."),
    Chapter("s16_dust", "WhatThePiecesLookLike", "What the pieces look like",
            "A cloud with no smallest scale, and an admission that it is a stand-in."),
    Chapter("s17_five_pieces", "FivePieces", "The assembly",
            "Exploded view of five pieces, reassembled into two balls. Robinson, 1947."),
    Chapter("s18_dimensions", "WhyNotInThePlane", "Why the plane is safe",
            "Plane rotations commute; the dimension ladder from R to R^n."),
    Chapter("s19_reality_and_outro", "RealityCheck", "So why not gold?",
            "Atoms, unmeasurable pieces, and the chain of ideas end to end."),
    Chapter("s19_reality_and_outro", "Outro", "Outro",
            "Back to the two balls, and the closing card."),
]
