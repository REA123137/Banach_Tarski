#!/usr/bin/env bash
# Join the rendered scenes into one film, in the order of the shooting script.
#
#   ./assemble.sh                       -> media/TwoBalls.mp4
#   ./assemble.sh --parts               -> media/TwoBalls-1of4.mp4 …  (four acts)
#   ./assemble.sh out.mp4 S06Columns S06Doubling
#
# Reads film_order.txt, finds each scene's most recently rendered mp4 under
# media/, and concatenates without re-encoding.
set -euo pipefail

# The four acts, by the scene each one starts on.  A single 12-minute file is
# awkward to move around; these are the natural seams of the script.
ACT_STARTS=(S01Trick S06Columns S09Orbit S13Chain)
ACT_NAMES=("the trick and the letters" "the doubling, on words and on matrices" \
           "orbits, choice, and the closing circle" "the theorem, and the chocolate")

find_scene() {
    find media -name "$1.mp4" -printf '%T@ %p\n' 2>/dev/null \
        | sort -rn | head -1 | cut -d' ' -f2-
}

join_scenes() {  # join_scenes <output> <scene>...
    local out="$1"; shift
    local list; list="$(mktemp)"
    local missing=0
    for scene in "$@"; do
        local file; file="$(find_scene "$scene")"
        if [[ -z "$file" ]]; then
            echo "missing: $scene" >&2
            missing=$((missing + 1))
            continue
        fi
        printf "file '%s'\n" "$(realpath "$file")" >> "$list"
    done
    [[ "$missing" -gt 0 ]] && echo "$missing scene(s) not rendered — run ./render.sh first" >&2
    mkdir -p "$(dirname "$out")"
    ffmpeg -y -loglevel error -f concat -safe 0 -i "$list" -c copy "$out"
    rm -f "$list"
    printf '%s  %s  %s MB\n' "$out" \
        "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" \
           | awk '{printf "%d:%02d", $1/60, $1%60}')" \
        "$(du -m "$out" | cut -f1)"
}

mapfile -t ORDER < <(grep -v '^\s*#' film_order.txt | grep -v '^\s*$')

if [[ "${1:-}" == "--parts" ]]; then
    for i in "${!ACT_STARTS[@]}"; do
        start="${ACT_STARTS[$i]}"
        end_index=${#ORDER[@]}
        if [[ $((i + 1)) -lt ${#ACT_STARTS[@]} ]]; then
            next="${ACT_STARTS[$((i + 1))]}"
            for j in "${!ORDER[@]}"; do
                [[ "${ORDER[$j]}" == "$next" ]] && end_index=$j && break
            done
        fi
        for j in "${!ORDER[@]}"; do
            [[ "${ORDER[$j]}" == "$start" ]] && start_index=$j && break
        done
        scenes=("${ORDER[@]:start_index:end_index-start_index}")
        echo "── act $((i + 1)): ${ACT_NAMES[$i]}"
        join_scenes "media/TwoBalls-$((i + 1))of${#ACT_STARTS[@]}.mp4" "${scenes[@]}"
    done
    exit 0
fi

OUT="${1:-media/TwoBalls.mp4}"
shift || true
if [[ $# -gt 0 ]]; then
    join_scenes "$OUT" "$@"
else
    join_scenes "$OUT" "${ORDER[@]}"
fi
