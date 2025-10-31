#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
PUBSPEC="$ROOT_DIR/frontend/chaos_contained/pubspec.yaml"

current_ver=$(awk -F': ' '/^version:/{print $2}' "$PUBSPEC" | head -n1)
base_ver=${current_ver%%+*}
major=$(echo "$base_ver" | cut -d. -f1)
minor=$(echo "$base_ver" | cut -d. -f2)
patch=$(echo "$base_ver" | cut -d. -f3)

new_patch=$((patch+1))
new_ver="$major.$minor.$new_patch+1"

echo "Bumping version: $current_ver -> $new_ver"
sed -i "s/^version: .*/version: $new_ver/" "$PUBSPEC"

cd "$ROOT_DIR"
git add frontend/chaos_contained/pubspec.yaml
git commit -m "chore(release): bump version to $new_ver"
git tag -a "v$new_ver" -m "Release v$new_ver"
echo "Tagged v$new_ver. Push with: git push --follow-tags"


