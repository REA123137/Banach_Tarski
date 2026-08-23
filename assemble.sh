#!/usr/bin/env bash
# Join the rendered scenes into one film, in the order of the shooting script.
#
#   ./assemble.sh [output.mp4]
#
# Reads film_order.txt, finds each scene's most recently rendered mp4 under
# media/, and concatenates without re-encoding.
set -euo pipefail

OUT="${1:-media/TwoBalls.mp4}"
LIST="$(mktemp)"
trap 'rm -f "$LIST"' EXIT

missing=0
while read -r scene; do
    [[ -z "$scene" || "$scene" == \#* ]] && continue
    file="$(find media -name "$scene.mp4" -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
    if [[ -z "$file" ]]; then
        echo "missing: $scene" >&2
        missing=$((missing + 1))
        continue
    fi
    printf "file '%s'\n" "$(realpath "$file")" >> "$LIST"
done < film_order.txt

[[ "$missing" -gt 0 ]] && echo "$missing scene(s) not rendered — run ./render.sh first" >&2

mkdir -p "$(dirname "$OUT")"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c copy "$OUT"
echo "$OUT"
ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 "$OUT"
