#!/bin/bash

set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel)
readonly ROOT_DIR

echo "Formatting $ROOT_DIR"

EXCLUDED=()
INCLUDED=()

die_if_no_arg() {
	if [[ $# -eq 0 ]]; then
		echo "Missing path for $1"
		exit 1
	fi
}

read_cmd_args() {
	local fp
	while (($# > 0)); do
		case $1 in
		-e|--exclude)
			shift
			die_if_no_arg "$@"
			fp="${ROOT_DIR%%/}/${1%%/}"
			EXCLUDED+=("$fp")
			echo "exclude $fp"
			;;
		-i|--include)
			shift
			die_if_no_arg "$@"
			fp="${ROOT_DIR%%/}/${1%%/}"
			INCLUDED+=("$fp")
			echo "include $fp"
			;;
		"")
			break
			;;
		*)
			echo "Unknown command: '$1'"
			exit 1
			;;
		esac
		shift
	done
	readonly -a EXCLUDED INCLUDED
}

is_excluded() {
	local file=$1
	for entry in "${EXCLUDED[@]}"; do
		if [[ ${file} == "${entry}" ]] || [[ ${file} == "${entry}"/* ]]; then
			return 0
		fi
	done
	return 1
}

exit_if_tools_not_installed() {
	for prog in pyupgrade isort black; do
		if ! [[ -x $(command -v "$prog") ]]; then
			echo "command not found: $prog"
			exit 1
		fi
	done
}

main() {
	exit_if_tools_not_installed
	local TO_FORMAT=()
	read_cmd_args "$@"
	if [[ ${#INCLUDED[@]} -eq 0 ]]; then
		# included list is not provided
		readarray -t FILES <<<"$(find "$ROOT_DIR" -iname '*.py')"
	else
		readarray -t FILES <<<"$(find "${INCLUDED[@]}" -iname '*.py')"
	fi
	readonly -a FILES

	if [[ ${#FILES[@]} -eq 0 ]] || [[ -z "${FILES[0]}" ]]; then
		echo "No Python files found."
		exit 0
	fi
	for file in "${FILES[@]}"; do
		if is_excluded "$file"; then
			echo "excluded: $file"
		else
			TO_FORMAT+=("$file")
		fi
	done
	readonly -a TO_FORMAT

	pyupgrade --py39-plus "${TO_FORMAT[@]}"
	isort "${TO_FORMAT[@]}"
	black --line-length 120 --target-version py39 "${TO_FORMAT[@]}"
}

main "$@"
