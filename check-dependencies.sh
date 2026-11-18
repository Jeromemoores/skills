#!/bin/sh
set -eu
task_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$task_root/skills/dependency-docs/scripts/dependency_docs.py" check --project "${1:-$PWD}" --format table
