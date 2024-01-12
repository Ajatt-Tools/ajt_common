# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections.abc import Iterable
from typing import Callable, Any, cast

import aqt
from aqt import mw


def get_default_config() -> dict:
    manager = mw.addonManager
    addon = manager.addonFromModule(__name__)
    return manager.addonConfigDefaults(addon)


def get_config() -> dict:
    return mw.addonManager.getConfig(__name__)


def write_config(config: dict):
    return mw.addonManager.writeConfig(__name__, config)


def set_config_action(fn: Callable):
    return mw.addonManager.setConfigAction(__name__, fn)


def set_config_update_action(fn: Callable):
    return mw.addonManager.setConfigUpdatedAction(__name__, fn)


class MgrPropMixIn:
    @property
    def mgr(self) -> aqt.addons.AddonManager:
        """Anki's ConfigEditor requires this property."""
        return mw.addonManager


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

    def __getitem__(self, key: str):
        if key in self._default_config:
            return self._config.get(key, self._default_config[key])
        else:
            raise KeyError(f"Key '{key}' is not defined in the default config.")

    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            raise
        else:
            self._config[key] = value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return self._default_config.keys()

    def bool_keys(self) -> Iterable[str]:
        """Returns an iterable of boolean (toggleable) parameters in the config."""
        return (key for key, value in self._default_config.items() if isinstance(value, bool))

    def items(self) -> Iterable[tuple[str, Any]]:
        for key in self.keys():
            yield key, self[key]

    def toggleables(self) -> Iterable[tuple[str, bool]]:
        """Return all toggleable keys and values in the config."""
        for key in self.bool_keys():
            yield key, self[key]

    def update(self, another: dict[str, Any], clear_old: bool = False) -> None:
        self._raise_if_redundant_keys(another)
        if clear_old:
            self._config.clear()
        self._config.update(another)

    def update_from_addon_manager(self, new_conf: dict):
        """
        This method may be passed to mw.addonManager.setConfigUpdatedAction
        to update our copy of the config dictionary after the user finishes editing it.
        """
        try:
            # Config has been already written to disk by aqt.addons.ConfigEditor
            self.update(new_conf, clear_old=True)
        except RuntimeError as ex:
            from aqt.utils import showCritical

            showCritical(str(ex), parent=mw, help=cast(str, None))
            # Restore previous config.
            self.write_config()

    def dict_copy(self) -> dict:
        """Get a deep copy of the config dictionary."""
        import copy
        return copy.deepcopy(self._config)

    def write_config(self):
        if self.is_default:
            raise RuntimeError("Can't write default config.")
        return write_config(self._config)

    def _raise_if_redundant_keys(self, new_config: dict):
        if redundant_keys := [key for key in new_config if key not in self._default_config]:
            raise RuntimeError(
                "Passed a new config with keys that aren't present in the default config: %s."
                % ", ".join(redundant_keys)
            )
