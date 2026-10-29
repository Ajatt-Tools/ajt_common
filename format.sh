#!/bin/bash

set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel)
readonly ROOT_DIR

echo "Formatting $ROOT_DIR"

EXCLUDED=()
INCLUDED=()
CHECK=false

die_if_no_arg() {
	if [[ $# -lt 2 ]]; then
		echo "Missing path for $1"
		exit 1
	fi
}

# Record a validated path while keeping include/exclude parsing in one place.
add_format_path() {
	local flag=$1
	local fp="${ROOT_DIR%%/}/${2%%/}"
	case $flag in
	-i|--include)
		INCLUDED+=("$fp")
		echo "include $fp"
		;;
	-e|--exclude)
		EXCLUDED+=("$fp")
		echo "exclude $fp"
		;;
	esac
}

# Consume option/path pairs without duplicating validation and path normalization.
read_cmd_args() {
	while (($# > 0)); do
		case $1 in
		--check)
			CHECK=true
			shift
			;;
		-e|--exclude|-i|--include)
			die_if_no_arg "$@"
			add_format_path "$1" "$2"
			shift 2
			;;
		"")
			break
			;;
		*)
			echo "Unknown command: '$1'"
			exit 1
			;;
		esac
	done
	readonly CHECK EXCLUDED INCLUDED
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

# Discover files only after parsing options so check and fix modes share the same scope.
collect_format_files() {
	if [[ ${#INCLUDED[@]} -eq 0 ]]; then
		# included list is not provided
		readarray -t FILES <<<"$(find "$ROOT_DIR" -iname '*.py')"
	else
		readarray -t FILES <<<"$(find "${INCLUDED[@]}" -iname '*.py')"
	fi
	readonly -a FILES
}

# Bash's dynamic scope exposes the caller's local TO_FORMAT array without copying file paths.
run_format_tools() {
	if [[ ${#TO_FORMAT[@]} -eq 0 ]]; then
		echo "No Python files found."
		return
	fi
	# Check mode must never run pyupgrade because it rewrites files in place.
	if $CHECK; then
		black --check --diff --line-length 120 --target-version py310 "${TO_FORMAT[@]}"
		isort --check-only --diff "${TO_FORMAT[@]}"
		return
	fi
	# Successful rewrites must not stop fix mode before isort and Black run.
	pyupgrade --exit-zero-even-if-changed --py310-plus "${TO_FORMAT[@]}"
	isort "${TO_FORMAT[@]}"
	black --line-length 120 --target-version py310 "${TO_FORMAT[@]}"
}

main() {
	exit_if_tools_not_installed
	local TO_FORMAT=()
	read_cmd_args "$@"
	collect_format_files
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
	run_format_tools
}

main "$@"
