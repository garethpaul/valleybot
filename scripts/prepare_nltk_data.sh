#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export NLTK_DATA="$ROOT_DIR/nltk_data"

python_bin=${PYTHON:-python3}
"$python_bin" -m textblob.download_corpora lite
