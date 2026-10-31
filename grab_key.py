# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
from collections.abc import Sequence

from aqt.qt import *


def mod_mask_qt6() -> Qt.KeyboardModifier:
    """Return the combined mask of modifiers supported by shortcut capture."""
    return (
        Qt.KeyboardModifier.ControlModifier
        | Qt.KeyboardModifier.AltModifier
        | Qt.KeyboardModifier.ShiftModifier
        | Qt.KeyboardModifier.MetaModifier
    )


def forbidden_keys() -> Sequence[Qt.Key]:
    """Return modifier-only keys that cannot form a shortcut by themselves."""
    return (
        Qt.Key.Key_Shift,
        Qt.Key.Key_Alt,
        Qt.Key.Key_Control,
        Qt.Key.Key_Meta,
    )


def modifiers_allowed(modifiers: Qt.KeyboardModifier) -> bool:
    return modifiers & mod_mask_qt6() == modifiers  # Qt6


def to_int(modifiers: Qt.KeyboardModifier) -> int:
    return int(modifiers.value)  # Qt6


class KeyPressDialog(QDialog):
    """Capture a shortcut or clear it when Escape is pressed."""

    value_accepted = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None, initial_value: str | None = None, *args, **kwargs) -> None:
        """Initialize the dialog, preserving an unassigned shortcut when the initial value is None."""
        super().__init__(parent, *args, **kwargs)
        self._shortcut = initial_value
        self.setMinimumSize(380, 64)
        self.setWindowTitle("Grab key combination")
        self.setLayout(self._make_layout())

    @staticmethod
    def _make_layout() -> QLayout:
        label = QLabel(
            "Please press the key or key combination you would like to assign.\n"
            "Supported modifiers: CTRL, ALT, SHIFT or META.\n"
            "Press ESC to delete the shortcut."
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(label)
        return layout

    def _accept_value(self, value: str | None) -> None:
        """Publish the captured shortcut and close the dialog with an accepted result."""
        self.set_value(value)
        self.accept()

    def set_value(self, value: str | None) -> None:
        """Store the shortcut, using None for an unassigned value, and notify listeners."""
        self._shortcut = value
        self.value_accepted.emit(value)  # type: ignore

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # https://stackoverflow.com/questions/35033116
        # https://doc.qt.io/qt-6/qdialog.html#keyPressEvent
        key = int(event.key())
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Escape:
            self._accept_value(None)
        elif modifiers_allowed(modifiers) and key > 0 and key not in forbidden_keys():
            self._accept_value(QKeySequence(to_int(modifiers) + key).toString())

    def value(self) -> str | None:
        """Return the stored shortcut or None when no shortcut is assigned."""
        return self._shortcut


class ShortCutGrabButton(QPushButton):
    """Open shortcut capture and display a placeholder for an unassigned shortcut."""

    _placeholder = "[Not assigned]"

    def __init__(self, initial_value: str | None = None) -> None:
        """Initialize a grab button with an optional shortcut rather than requiring an assigned value."""
        super().__init__(initial_value or self._placeholder)
        self._dialog = KeyPressDialog(self, initial_value)
        qconnect(self.clicked, self._dialog.exec)
        qconnect(
            self._dialog.value_accepted,
            lambda value: self.setText(value or self._placeholder),
        )

    def setValue(self, value: str) -> None:
        """Set the shortcut and update the visible button label through the dialog's notification."""
        self._dialog.set_value(value)

    def value(self) -> str:
        return self._dialog.value() or ""


def detect_keypress() -> None:
    app = QApplication(sys.argv)
    w = QDialog()
    w.setWindowTitle("Test")
    w.setLayout(layout := QVBoxLayout())
    layout.addWidget(b := ShortCutGrabButton())
    w.show()
    code = app.exec()
    print(f'{"Accepted" if w.result() else "Rejected"}. Code: {code}, shortcut: "{b.value()}"')
    sys.exit(code)


if __name__ == "__main__":
    detect_keypress()
