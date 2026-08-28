#!/usr/bin/env bash
# Collect each sequence into its own folder: the scenes that make it up, and
# the script that goes with them.
#
#   ./pack.sh [outdir]        default: out/
#
# out/
#   01_the_trick/
#     script.md
#     1-S01Trick.mp4  2-S01Squeeze.mp4  …
set -euo pipefail

OUT="${1:-out}"
rm -rf "$OUT"
mkdir -p "$OUT"

# which scenes belong to which sequence, in playing order
sequence_of() {                       # sequence_of <SceneName> -> NN
    printf '%s' "${1:1:2}"
}

mapfile -t ORDER < <(grep -v '^\s*#' film_order.txt | grep -v '^\s*$')

declare -A RANK
for i in "${!ORDER[@]}"; do RANK[${ORDER[$i]}]=$i; done

for script in script/*.md; do
    n="$(basename "$script" | cut -d_ -f1)"
    name="$(basename "$script" .md)"
    dir="$OUT/$name"
    mkdir -p "$dir"
    cp "$script" "$dir/script.md"
    k=0
    for scene in "${ORDER[@]}"; do
        [[ "$(sequence_of "$scene")" == "$n" ]] || continue
        file="$(find media -name "$scene.mp4" -printf '%T@ %p\n' 2>/dev/null \
                | sort -rn | head -1 | cut -d' ' -f2-)"
        if [[ -z "$file" ]]; then
            echo "  missing render: $scene" >&2
            continue
        fi
        k=$((k + 1))
        cp "$file" "$dir/$k-$scene.mp4"
    done
    printf '%-34s %s script + %d scenes\n' "$name" "·" "$k"
done

echo
echo "packed into $OUT/"
