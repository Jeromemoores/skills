#!/bin/sh
set -eu

version=1.0.0
release="https://github.com/Jeromemoores/skills/releases/download/v$version"
target=both
skill_set=all
profile=${HOME:?HOME must identify your user profile}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --target) target=$2; shift 2 ;;
        --set) skill_set=$2; shift 2 ;;
        --user-root) profile=$2; shift 2 ;;
        *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
    esac
done
case "$target" in both|claude|codex) ;; *) echo 'Use --target both, claude, or codex.' >&2; exit 2 ;; esac
case "$skill_set" in all|web|unreal) ;; *) echo 'Use --set all, web, or unreal.' >&2; exit 2 ;; esac

source_root=
case "$0" in
    */install.sh)
        script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
        if [ -d "$script_dir/skills" ]; then source_root=$script_dir; fi
        ;;
esac
if [ -z "$source_root" ]; then
    command -v curl >/dev/null 2>&1 || { echo 'curl is required to download the release.' >&2; exit 1; }
    command -v tar >/dev/null 2>&1 || { echo 'tar is required to extract the release.' >&2; exit 1; }
    work=$(mktemp -d "${TMPDIR:-/tmp}/jeromemoores-skills.XXXXXXXX")
    bundle=skills
    case "$skill_set" in web) bundle=web-skills ;; unreal) bundle=unreal-skills ;; esac
    package="$bundle-v$version"
    archive="$package.tar.gz"
    curl -fLsS "$release/$archive" -o "$work/$archive"
    curl -fLsS "$release/SHA256SUMS" -o "$work/SHA256SUMS"
    expected=$(awk -v file="$archive" '$2 == file { print $1 }' "$work/SHA256SUMS")
    [ "${#expected}" -eq 64 ] || { echo 'Release checksum entry is missing or ambiguous.' >&2; exit 1; }
    if command -v sha256sum >/dev/null 2>&1; then
        actual=$(sha256sum "$work/$archive" | awk '{print $1}')
    elif command -v shasum >/dev/null 2>&1; then
        actual=$(shasum -a 256 "$work/$archive" | awk '{print $1}')
    else
        echo 'sha256sum or shasum is required to verify the release.' >&2; exit 1
    fi
    [ "$actual" = "$expected" ] || { echo 'Release checksum verification failed.' >&2; exit 1; }
    tar -xzf "$work/$archive" -C "$work"
    source_root="$work/$package"
fi

sets=shared
case "$skill_set" in all) sets='shared web unreal' ;; web) sets='shared web' ;; unreal) sets='shared unreal' ;; esac
for set_name in $sets; do
    while IFS= read -r name || [ -n "$name" ]; do
        [ -n "$name" ] || continue
        case "$name" in *[!a-z0-9-]*|-*|*-) echo "Invalid skill name: $name" >&2; exit 1 ;; esac
        source="$source_root/skills/$name"
        [ -f "$source/SKILL.md" ] || { echo "Missing skill: $name" >&2; exit 1; }
        if [ "$target" = both ] || [ "$target" = claude ]; then
            destination="$profile/.claude/skills/$name"
            mkdir -p "$destination"
            cp -R "$source/." "$destination/"
        fi
        if [ "$target" = both ] || [ "$target" = codex ]; then
            destination="$profile/.agents/skills/$name"
            mkdir -p "$destination"
            cp -R "$source/." "$destination/"
        fi
    done < "$source_root/skill-sets/$set_name.txt"
done
printf 'Installed %s skills for %s, version %s.\n' "$skill_set" "$target" "$version"
echo 'Start a new agent session if the skills do not appear. Documentation downloads require Python 3.11+ and Git.'
if [ -n "${work:-}" ]; then printf 'Downloaded release retained at: %s\n' "$work"; fi
