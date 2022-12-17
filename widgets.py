# Widgets shared among AJT addons.
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Iterable

from aqt import mw
from aqt.qt import *


class AnkiFieldSelector(QComboBox):
    """
    An editable combobox prepopulated with all field names
    present in Note Types in the Anki collection.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(True)
        self.addItems(dict.fromkeys(self._gather_field_names()))

    @staticmethod
    def _gather_field_names() -> Iterable[str]:
        for model in mw.col.models.all_names_and_ids():
            for field in mw.col.models.get(model.id)['flds']:
                yield field['name']
