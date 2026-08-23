#!/usr/bin/env bash
# Render the film, or any part of it.
#
#   ./render.sh                 every scene, preview quality (480p15)
#   ./render.sh -qh             every scene, 1080p60
#   ./render.sh -qh s12         every scene of module s12_*
#   ./render.sh -qh S12Circle   one scene by name
#
# Output lands in ./media/videos/<module>/<quality>/<Scene>.mp4
set -euo pipefail

QUALITY="${1:--ql}"
FILTER="${2:-}"

shopt -s nullglob
for file in banach_tarski/scenes/s*.py; do
    base="$(basename "$file" .py)"
    if [[ -n "$FILTER" && "$base" != "$FILTER"* ]]; then
        # not a module match — maybe the filter names a single scene in it
        if ! grep -q "^class ${FILTER}(" "$file"; then
            continue
        fi
        echo "── $base :: $FILTER"
        python3 -m manim "$QUALITY" --progress_bar none "$file" "$FILTER"
        continue
    fi
    scenes=$(grep -oP '^class \K\w+(?=\(Scene\))' "$file" | tr '\n' ' ')
    [[ -z "$scenes" ]] && continue
    echo "── $base :: $scenes"
    # shellcheck disable=SC2086
    python3 -m manim "$QUALITY" --progress_bar none "$file" $scenes
done
