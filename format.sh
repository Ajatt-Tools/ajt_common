#!/bin/bash

echo "Formatting $PWD"

# Pass a list of files or take all files in the repository.

if [[ $# -gt 0 ]]; then
	FILES=("$@")
else
	readarray -t FILES <<<"$(git ls-files | grep -P '\.py$')"
fi
readonly -a FILES

pyupgrade \
	--py39-plus \
	"${FILES[@]}"
black \
	--line-length 120 \
	--target-version py39 \
	"${FILES[@]}"
