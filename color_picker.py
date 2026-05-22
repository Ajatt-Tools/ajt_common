# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from gettext import gettext as _

from aqt.qt import *

from .monospace_line_edit import MonoSpaceLineEdit


class ColorEdit(MonoSpaceLineEdit):
    font_size = 14
    min_height = 24

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        color_regex = QRegularExpression(r"^#?\w+$")
        color_validator = QRegularExpressionValidator(color_regex, self)
        self.setValidator(color_validator)
        self.setPlaceholderText(_("HTML color code"))


class ColorEditPicker(QWidget):
    def __init__(self, initial_color: str = "", parent=None) -> None:
        super().__init__(parent)
        self._edit = ColorEdit()
        self.set_color(initial_color or "black")
        self.setLayout(layout := QHBoxLayout())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._edit)
        layout.addWidget(b := QPushButton(_("Pick")))
        b.setMinimumSize(32, 16)
        b.setBaseSize(32, 22)
        qconnect(b.clicked, self.choose_color)

    def choose_color(self) -> None:
        color = QColorDialog.getColor(initial=QColor.fromString(self._edit.text()))
        if color.isValid():
            self._edit.setText(color.name())

    def setText(self, text: str) -> None:
        return self._edit.setText(text)

    def text(self) -> str:
        return self._edit.text()
