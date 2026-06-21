#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export NLTK_DATA="$ROOT_DIR/nltk_data"

: "${REPOSITORY_PYTHON:?REPOSITORY_PYTHON must name the reviewed absolute interpreter}"
"$ROOT_DIR/scripts/run-python.sh" --module textblob.download_corpora lite
