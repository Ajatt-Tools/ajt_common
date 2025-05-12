# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
from aqt import mw
from aqt.qt import *
from PyQt6.QtWidgets import QComboBox

from .model_utils import gather_all_field_names


class EditableSelector(QComboBox):
    """
    Convenience class for making combo boxes with editable input field.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setEditable(True)


class AnkiFieldSelector(EditableSelector):
    """
    An editable combobox prepopulated with all field names
    present in Note Types in the Anki collection.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        try:
            self.addItems(dict.fromkeys(gather_all_field_names()))
        except AttributeError:
            assert mw is None, "Anki can't be running."
            self.addItems(["Anki is not running"] * 5)
