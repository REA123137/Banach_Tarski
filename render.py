#!/usr/bin/env python3
"""
Render the film.

    python render.py                 # every chapter, 1080p60
    python render.py --quality l     # fast pass for checking
    python render.py --only s09 s10  # just those chapters
    python render.py --stitch        # also concatenate into one file

Manim is invoked as a subprocess so each chapter gets a clean interpreter -
a scene that dies takes only itself down, and the run reports which.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from banach_tarski.film import FILM  # noqa: E402

QUALITY_DIR = {"l": "480p15", "m": "720p30", "h": "1080p60", "p": "1440p60", "k": "2160p60"}


def render(chapter, quality: str, extra: list[str]) -> pathlib.Path | None:
    script = ROOT / "banach_tarski" / "scenes" / f"{chapter.key}.py"
    cmd = [sys.executable, "-m", "manim", f"-q{quality}", str(script), chapter.scene, *extra]
    print(f"\n\033[1m→ {chapter.scene}\033[0m  ({chapter.title})")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"\033[31m  failed: {chapter.scene}\033[0m")
        return None
    out = ROOT / "media" / "videos" / chapter.key / QUALITY_DIR[quality] / f"{chapter.scene}.mp4"
    return out if out.exists() else None


def stitch(parts: list[pathlib.Path], quality: str) -> pathlib.Path:
    """Concatenate the chapters into one file, without re-encoding."""
    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    listing = out_dir / "chapters.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in parts))
    target = out_dir / f"banach_tarski_{QUALITY_DIR[quality]}.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c", "copy", str(target)],
        check=True,
    )
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quality", "-q", default="h", choices=sorted(QUALITY_DIR),
                    help="manim quality flag (default h = 1080p60)")
    ap.add_argument("--only", nargs="*", default=None,
                    help="chapter key prefixes or scene names to render")
    ap.add_argument("--stitch", action="store_true", help="concatenate the result")
    ap.add_argument("--list", action="store_true", help="print the running order and exit")
    args, extra = ap.parse_known_args()

    if args.list:
        for c in FILM:
            print(f"  {c.key:<26} {c.scene:<24} {c.title}")
        return 0

    wanted = FILM
    if args.only:
        wanted = [c for c in FILM
                  if any(c.key.startswith(p) or c.scene == p for p in args.only)]
        if not wanted:
            print("nothing matched", args.only)
            return 1

    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found on PATH - manim needs it to write video", file=sys.stderr)
        return 1

    parts, failed = [], []
    for chapter in wanted:
        path = render(chapter, args.quality, extra)
        (parts if path else failed).append(path or chapter.scene)

    print(f"\n\033[1m{len(parts)}/{len(wanted)} chapters rendered\033[0m")
    if failed:
        print("failed:", ", ".join(failed))
    if args.stitch and parts:
        print("stitched →", stitch(parts, args.quality))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
