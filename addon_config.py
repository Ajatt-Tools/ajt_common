# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Callable, Iterable, Any

from aqt import mw


def get_default_config():
    manager = mw.addonManager
    addon = manager.addonFromModule(__name__)
    return manager.addonConfigDefaults(addon)


def get_config() -> dict:
    return mw.addonManager.getConfig(__name__)


def write_config(config: dict):
    return mw.addonManager.writeConfig(__name__, config)


def set_config_action(fn: Callable):
    return mw.addonManager.setConfigAction(__name__, fn)


class AddonConfigManager:
    """Dict-like proxy class for managing addon's config."""
    _default_config = get_default_config()
    _config = get_config()

    def __init__(self, default: bool = False):
        if default:
            self._config = self._default_config

    @property
    def is_default(self) -> bool:
        return self._default_config is self._config

    def _get(self, key: str):
        if key in self._default_config:
            return self._config.get(key, self._default_config[key])
        else:
            raise KeyError(f"Key '{key}' is not defined in the default config.")

    def __getitem__(self, key: str):
        return self._get(key)

    def __setitem__(self, key, value):
        try:
            self._get(key)
        except KeyError:
            raise
        else:
            self._config[key] = value

    def get(self, key, default=None):
        try:
            return self._get(key)
        except KeyError:
            return default

    def items(self):
        for key in self._default_config:
            yield key, self[key]

    def toggleables(self) -> Iterable[tuple[str, Any]]:
        for key, val in self.items():
            if isinstance(val, bool):
                yield key, val

    @classmethod
    def bool_keys(cls) -> Iterable[str]:
        """Returns an iterable of boolean keys in the config."""
        return (key for key, value in cls._default_config.items() if isinstance(value, bool))

    def update(self, another):
        if all(key in self._default_config for key in another):
            return self._config.update(another)
        else:
            raise RuntimeError("Passed config with keys that aren't present in the default config.")

    def write_config(self):
        if self.is_default:
            raise RuntimeError("Can't write default config.")
        return write_config(self._config)
