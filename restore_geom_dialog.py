# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
from aqt import mw
from aqt.qt import *
from aqt.utils import restoreGeom, saveGeom


class AnkiSaveAndRestoreGeomDialog(QDialog):
    """
    A dialog running inside Anki should save and restore its position and size when closed/opened.
    """

    name: str

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert isinstance(self.name, str) and self.name, "Dialog name must be set."
        self._restore_geom()

    def _restore_geom(self) -> None:
        if not mw:
            return
        restoreGeom(self, self.name, adjustSize=True)
        print(f"restored geom for {self.name}")

    def _save_geom(self) -> None:
        if not mw:
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
