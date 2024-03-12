#!/bin/bash

echo "Formatting $PWD"

readarray -t FILES <<<"$(git ls-files | grep -P '\.py$')"
readonly -a FILES

pyupgrade \
	--py39-plus \
	"${FILES[@]}"
black \
	--line-length 120 \
	--target-version py39 \
	"${FILES[@]}"
