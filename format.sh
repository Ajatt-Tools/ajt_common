#!/bin/bash

echo "Formatting $PWD"

ROOT_DIR=$(git rev-parse --show-toplevel)
readonly ROOT_DIR

# Pass a list of files or take all files in the repository.

if [[ $# -gt 0 ]]; then
	FILES=("$@")
else
	readarray -t FILES <<<"$(find "$ROOT_DIR" -iname '*.py')"
fi
readonly -a FILES

pyupgrade --py39-plus "${FILES[@]}"
isort "${FILES[@]}"
black --line-length 120 --target-version py39 "${FILES[@]}"
