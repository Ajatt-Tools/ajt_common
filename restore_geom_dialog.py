# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
from aqt import mw
from aqt.qt import *
from aqt.utils import restoreGeom, saveGeom


def can_access_geom_data() -> bool:
    """Return whether Anki's active profile can store dialog geometry."""
    return bool(mw and mw.pm.profile)


class AnkiSaveAndRestoreGeomDialog(QDialog):
    """
    A dialog running inside Anki should save and restore its position and size when closed/opened.
    """

    name: str

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert isinstance(self.name, str) and self.name, "Dialog name must be set."
        self._restore_geom()

    def show(self) -> None:
        """Show the dialog, then restore its saved geometry."""
        super().show()
        self._restore_geom()

    def exec(self) -> int:
        self._restore_geom()
        return super().exec()

    def _restore_geom(self) -> None:
        """Restore saved geometry only while an Anki profile is available."""
        if not can_access_geom_data():
            return
        restoreGeom(self, self.name, adjustSize=True)
        print(f"restored geom for {self.name}")

    def _save_geom(self) -> None:
        """Save current geometry only while an Anki profile is available."""
        if not can_access_geom_data():
            return
        saveGeom(self, self.name)
        print(f"saved geom for {self.name}")

    def accept(self) -> None:
        # https://doc.qt.io/qt-6/qdialog.html#accept
        self._save_geom()
        return super().accept()

    def reject(self) -> None:
        # https://doc.qt.io/qt-6/qdialog.html#reject
        self._save_geom()
        return super().reject()
