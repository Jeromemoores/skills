#!/bin/sh
set -eu
installer=$(curl -fsSL https://raw.githubusercontent.com/Jeromemoores/skills/v1.0.1/install.sh)
printf '%s\n' "$installer" | sh -s -- --set unreal "$@"
