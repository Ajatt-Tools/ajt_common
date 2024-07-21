#!/bin/bash
# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

set -euo pipefail

readonly NC='\033[0m'
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly manifest=manifest.json

# command-line arguments
declare \
	package=unknown \
	name=unknown \
	target=ankiweb \
	addon_root=""

declare zip_name

check_tools_installed() {
	for exe in git zip zipmerge; do
		if ! command -v "$exe" >/dev/null; then
			echo -e "${RED}Missing dependency:${NC} $exe"
			exit 1
		fi
	done
}

check_correct_cwd() {
	if ! [[ -d $PWD/.git ]] || ! [[ -d $PWD/ajt_common || -d $PWD/$addon_root/ajt_common ]]; then
		echo -e "${RED}Started in a wrong directory:${NC} $PWD"
		exit 1
	fi
}

git_archive() {
	if [[ -n $addon_root ]]; then
		local -r ref=HEAD:$addon_root
	else
		local -r ref=HEAD
	fi
	run_archive() {
		git archive "$ref" --format=zip --output "$zip_name" "$@"
	}
	echo "Target $target"
	if [[ $target != ankiweb && $target != aw ]]; then
		# https://addon-docs.ankiweb.net/sharing.html#sharing-outside-ankiweb
		# If you wish to distribute .ankiaddon files outside of AnkiWeb,
		# your add-on folder needs to contain a ‘manifest.json’ file.
		echo "Creating $manifest"
		cat <<-EOF >"$manifest"
			{
			  "package": "$package",
			  "name": "$name",
			  "mod": $(date -u '+%s')
			}
		EOF
		run_archive --add-file="$manifest"
	else
		run_archive
	fi
}

read_cmd_args() {
	while (($# > 0)); do
		case $1 in
		--name)
			name=$2
			shift
			;;
		--package)
			package=$2
			shift
			;;
		--target)
			target=$2 # ankiweb or github
			shift
			;;
		--zip_name)
			zip_name=$2 # usually *.ankiaddon
			echo "explicitly set zip name to '$zip_name'"
			shift
			;;
		--root)
			addon_root=$2
			echo "explicitly set root dir to '$addon_root'"
			shift
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
	readonly package name target addon_root
	zip_name=${zip_name:-${package,,}.ankiaddon}
	zip_name=${zip_name// /_}
	readonly zip_name
}

main() {
	check_tools_installed

	rm -v -- ./*.ankiaddon 2>/dev/null || true

	read_cmd_args "$@"
	check_correct_cwd

	echo "Packaging $name"
	echo "Archiving root repo"
	git_archive

	echo "Archiving submodules"
	# shellcheck disable=SC2016
	ROOT_DIR=$PWD \
		ADDON_ROOT=$addon_root \
		git submodule foreach \
		'PREFIX=${sm_path#$ADDON_ROOT/};
		 echo "Prefix $PREFIX:${sha1}";
		 git archive "${sha1}" --prefix="${PREFIX:?}/" --format=zip --output "${ROOT_DIR:?}/${PREFIX}_${sha1}.zip"'

	zipmerge ./"$zip_name" ./*.zip
	rm -v -- ./*.zip ./"$manifest" 2>/dev/null || true
	echo -e "${GREEN}Done.${NC}"
}

main "$@"
