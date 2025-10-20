# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Sequence

from aqt.qt import *

from .restore_geom_dialog import AnkiSaveAndRestoreGeomDialog

class StatsTableError(RuntimeError):
    pass

class StatsTable(QTableWidget):
    _column_names: Sequence[str]

    def __init__(self, column_names: Sequence[str], parent=None) -> None:
        super().__init__(parent)
        self._column_names = column_names
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setColumnCount(len(self._column_names))
        self.setHorizontalHeaderLabels(self._column_names)
        self.set_stretch_all_columns()
        assert self.columnCount() == len(self._column_names)

    def set_stretch_all_columns(self) -> None:
        header = self.horizontalHeader()
        for column_number in range(self.columnCount()):
            header.setSectionResizeMode(column_number, QHeaderView.ResizeMode.Stretch)


class StatsDialog(AnkiSaveAndRestoreGeomDialog):
    name: str
    win_title: str
    _table: StatsTable
    _button_box: QDialogButtonBox

    def __init__(self, column_names: Sequence[str], parent=None) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle(self.win_title)
        self.setMinimumSize(400, 300)
        self._table = StatsTable(column_names=column_names)
        self.setLayout(QVBoxLayout())
        self._button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.layout().addWidget(self._table)
        self.layout().addWidget(self._button_box)
        qconnect(self._button_box.accepted, self.accept)
        qconnect(self._button_box.rejected, self.reject)

    def load_data(self, data: Sequence[Sequence[str]]) -> "StatsDialog":
        for idx, row in enumerate(data):
            self._table.insertRow(idx)
            if len(row) != self._table.columnCount():
                raise StatsTableError(
                    f"row {idx} has {len(row)} columns but expected {self._table.columnCount()}")
            for jdx, item in enumerate(row):
                self._table.setItem(idx, jdx, QTableWidgetItem(str(item)))
        return self
