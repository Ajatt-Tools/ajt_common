# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.qt import *

from .model_utils import gather_all_field_names


class AnkiFieldSelector(QComboBox):
    """
    An editable combobox prepopulated with all field names
    present in Note Types in the Anki collection.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setEditable(True)
        try:
            self.addItems(dict.fromkeys(gather_all_field_names()))
        except AttributeError:
            assert mw is None, "Anki can't be running."
            self.addItems(["Anki is not running"] * 5)
