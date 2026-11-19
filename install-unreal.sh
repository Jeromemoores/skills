#!/bin/sh
set -eu
installer=$(curl -fsSL https://raw.githubusercontent.com/Jeromemoores/skills/v1.3.0/install.sh)
printf '%s\n' "$installer" | sh -s -- --set unreal "$@"
