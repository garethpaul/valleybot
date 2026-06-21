#!/usr/bin/env python3
"""Verify TextBlob/NLTK runtime data is present in the project data directory."""
import os
from pathlib import Path

import nltk.data


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NLTK_DATA = (ROOT / "nltk_data").resolve()
REQUIRED_RESOURCES = (
    "corpora/brown",
    "tokenizers/punkt_tab",
    "corpora/wordnet",
    "taggers/averaged_perceptron_tagger_eng",
)


def _resource_path(pointer):
    location = str(pointer)
    if ".zip" in location:
        location = location.split(".zip", 1)[0] + ".zip"
    return Path(location).resolve()


def main():
    configured = Path(os.environ.get("NLTK_DATA", "")).resolve()
    if configured != EXPECTED_NLTK_DATA:
        raise SystemExit(
            "NLTK_DATA must be the project-local directory: {0}".format(
                EXPECTED_NLTK_DATA
            )
        )

    missing = []
    for resource in REQUIRED_RESOURCES:
        try:
            found = _resource_path(nltk.data.find(resource))
        except LookupError:
            missing.append("{0} is missing".format(resource))
            continue

        if found != EXPECTED_NLTK_DATA and EXPECTED_NLTK_DATA not in found.parents:
            missing.append("{0} resource is outside NLTK_DATA: {1}".format(resource, found))

    if missing:
        raise SystemExit("missing NLTK resource(s): {0}".format("; ".join(missing)))


if __name__ == "__main__":
    main()
