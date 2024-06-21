# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
import os
import shutil
from collections.abc import Iterable
from typing import Optional


def ui_translate(key: str) -> str:
    return key.capitalize().replace("_", " ")


HARDCODED_PATHS = (
    "/usr/bin",
    "/opt/homebrew/bin",
    "/usr/local/bin",
    "/bin",
    os.path.join(os.getenv("HOME", "/home/user"), ".local", "bin"),
)


def find_executable_hardcoded(name: str) -> Optional[str]:
    def _iter() -> Iterable[str]:
        return map(lambda path: os.path.join(path, name), HARDCODED_PATHS)

    for path_to_exe in _iter():
        if os.path.isfile(path_to_exe):
            return path_to_exe


@functools.cache
def find_executable(name: str) -> Optional[str]:
    """
    If possible, use the executable installed in the system.
    Otherwise, try fallback paths.
    """
    return shutil.which(name) or find_executable_hardcoded(name)


def main():
    print("distutils", shutil.which("anki"))
    print("hardcoded", find_executable_hardcoded("anki"))
    print("all", find_executable("anki"))


if __name__ == "__main__":
    main()


def clamp(min_val: int, val: int, max_val: int) -> int:
    return max(min_val, min(val, max_val))
