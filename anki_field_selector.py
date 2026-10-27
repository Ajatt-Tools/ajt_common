# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.qt import *

from .model_utils import gather_all_field_names


class EditableSelector(QComboBox):
    """
    Convenience class for making combo boxes with editable input field.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a combo box that also accepts a manually entered value."""
        super().__init__(parent)
        self.setEditable(True)


class AnkiFieldSelector(EditableSelector):
    """
    An editable combobox prepopulated with all field names
    present in Note Types in the Anki collection.
    """

    def __init__(self, initial_value: str | None = None, parent: QWidget | None = None) -> None:
        """Populate field suggestions from Anki when available and preserve the supplied initial value."""
        super().__init__(parent)
        self.clear()
        try:
            self.addItems(dict.fromkeys(gather_all_field_names()))
        except AttributeError:
            assert mw is None, "Anki can't be running."
            self.addItems(["Anki is not running"] * 5)
        if initial_value:
            self.setCurrentText(initial_value)
