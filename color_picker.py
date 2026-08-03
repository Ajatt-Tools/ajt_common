# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from gettext import gettext as _

from aqt.qt import *

from .monospace_line_edit import MonoSpaceLineEdit
from .utils import q_emit

DEFAULT_COLOR = "black"


class ColorEdit(MonoSpaceLineEdit):
    font_size = 14
    min_height = 24

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        color_regex = QRegularExpression(r"^#?\w+$")
        color_validator = QRegularExpressionValidator(color_regex, self)
        self.setValidator(color_validator)
        self.setPlaceholderText(_("HTML color code"))


def color_to_hex_argb(color: QColor) -> str:
    """Return the color as a hex ARGB string."""
    return color.name(QColor.NameFormat.HexArgb).upper()


class ColorEditPicker(QWidget):
    color_changed = pyqtSignal(str)

    def __init__(self, initial_color: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        # Create members
        self._edit = ColorEdit()
        self.set_color(initial_color or DEFAULT_COLOR)
        # Create layout
        self.setLayout(layout := QHBoxLayout())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._edit)
        layout.addWidget(b := QPushButton(_("Pick")))
        b.setMinimumSize(32, 16)
        b.setBaseSize(32, 22)
        # https://doc.qt.io/qt-6/qabstractbutton.html#clicked
        qconnect(b.clicked, lambda: self.choose_color())
        # https://doc.qt.io/qt-6/qlineedit.html#textChanged
        qconnect(self._edit.textChanged, lambda text: q_emit(self.color_changed, text))

    def choose_color(self) -> None:
        color = QColorDialog.getColor(
            initial=QColor.fromString(self._edit.text() or DEFAULT_COLOR),
            parent=self,
            title="Select color",
            options=QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self._edit.setText(color_to_hex_argb(color))

    def set_color(self, hex_color: str) -> None:
        """Set the color. Accepts hex ARGB strings or named HTML colors."""
        self._edit.setText(hex_color)

    def color_hex(self) -> str:
        """Return the current color string (hex ARGB or named color)."""
        return self._edit.text()

    @deprecated(replaced_by=set_color)
    def setText(self, text: str) -> None:
        self.set_color(text)

    @deprecated(replaced_by=color_hex)
    def text(self) -> str:
        return self.color_hex()
