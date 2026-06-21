#!/bin/sh
set -eu

: "${REPOSITORY_PYTHON:?REPOSITORY_PYTHON must name the reviewed absolute interpreter}"

case $REPOSITORY_PYTHON in
    /*) ;;
    *) printf '%s\n' 'REPOSITORY_PYTHON must be an absolute path' >&2; exit 2 ;;
esac

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)

if [ "${1-}" = --module ]; then
    shift
    module=$1
    shift
    exec "$REPOSITORY_PYTHON" -I -B -c '
import runpy
import sys

root = sys.argv[1]
module = sys.argv[2]
sys.argv = sys.argv[2:]
sys.path.insert(0, root)
runpy.run_module(module, run_name="__main__", alter_sys=True)
' "$root" "$module" "$@"
fi

script=$1
shift

exec "$REPOSITORY_PYTHON" -I -B -c '
import os
import runpy
import sys

root = sys.argv[1]
script = os.path.realpath(sys.argv[2])
sys.argv = sys.argv[2:]
sys.path.insert(0, root)
sys.path.insert(0, os.path.dirname(script))
runpy.run_path(script, run_name="__main__")
' "$root" "$script" "$@"
