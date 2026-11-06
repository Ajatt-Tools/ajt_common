# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import enum
from collections.abc import Iterable, Sequence
from typing import Any

from aqt.qt import *

# Implementations
# https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
# https://www.geeksforgeeks.org/pyqt5-checkable-combobox-showing-checked-items-in-textview/


MISSING = object()


def reverse_check_state(check_state: Qt.CheckState) -> Qt.CheckState:
    """Toggle a checked item off and any other check state on."""
    if check_state == Qt.CheckState.Checked:
        return Qt.CheckState.Unchecked
    else:
        return Qt.CheckState.Checked


# Keep the existing Qt-style API names until a separate rename can update their shared add-on callers.
# noinspection PyPep8Naming
class CheckableComboBox(QComboBox):
    """Allow multiple checked selections while displaying their labels in the line edit."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Install checkable-item handling and refresh the display after model changes."""
        super().__init__(parent)

        # Initial state
        self._opened = False

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self._line_edit.setReadOnly(True)

        # Make the lineedit the same color as QPushButton
        palette = QApplication.palette()
        palette.setBrush(QPalette.ColorRole.Base, palette.button())
        self._line_edit.setPalette(palette)

        # Use custom delegate and model
        self.setItemDelegate(QStyledItemDelegate())
        self.setModel(QStandardItemModel(self))

        # When any item get pressed.
        # pressed supplies the QModelIndex consumed by handle_item_pressed().
        # https://doc.qt.io/qt-6/qabstractitemview.html#pressed
        qconnect(self._view.pressed, self.handle_item_pressed)

        # Update the text when an item is toggled
        # Model notifications carry indices and roles, not arguments for the text refresh.
        # https://doc.qt.io/qt-6/qabstractitemmodel.html#dataChanged
        qconnect(self._item_model.dataChanged, lambda: self.updateText())

        # Hide and show popup when clicking the line edit
        self._line_edit.installEventFilter(self)

        # Prevent popup from closing when clicking on an item
        self._viewport.installEventFilter(self)

    def handle_item_pressed(self, index: QModelIndex) -> None:
        """Check the pressed item if unchecked and vice versa."""
        item = self._item_model.itemFromIndex(index)
        assert item is not None, "The pressed index must refer to a populated item."
        # reverse checked state on click.
        item.setCheckState(reverse_check_state(item.checkState()))

    def resizeEvent(self, event: QResizeEvent | None) -> None:
        """Recompute text to elide as needed"""
        if event is None:
            return
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:
        """Toggle the popup for line-edit releases and keep it open for viewport releases."""
        if event is None:
            return False
        if event.type() == QEvent.Type.MouseButtonRelease:
            if obj == self.lineEdit():
                self.togglePopup()
                return True
            if obj == self._viewport:
                return True
        return False

    def togglePopup(self) -> None:
        """Show or hide the popup according to its current state."""
        if self._opened:
            self.hidePopup()
        else:
            self.showPopup()

    def showPopup(self) -> None:
        """When the popup is displayed, a click on the lineedit should close it"""
        super().showPopup()
        self._opened = True

    def hidePopup(self) -> None:
        """Hide the popup and refresh the checked labels after closing."""
        super().hidePopup()
        self._opened = False
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event: QTimerEvent | None) -> None:
        """After timeout, kill timer, and re-enable click on line-edit"""
        if event is None:
            return
        self.killTimer(event.timerId())
        self._opened = False

    def updateText(self) -> None:
        """Refresh the displayed text from the currently checked items."""
        self._line_edit.setText(", ".join(self.checkedTexts()))

    def addCheckableText(self, text: str) -> None:
        """Append an unchecked item whose text is also its user-visible label."""
        self.addCheckableItem(text)

    def addCheckableItem(self, text: str, data: Any = MISSING) -> None:
        """Append an unchecked row, optionally carrying caller-provided Qt item data."""
        item = QStandardItem()
        item.setText(text)
        item.setCheckable(True)
        item.setEnabled(True)
        item.setCheckState(Qt.CheckState.Unchecked)
        if data is not MISSING:
            item.setData(data)
        self._item_model.appendRow(item)

    def setCheckableTexts(self, texts: Iterable[str]) -> None:
        """Replace all rows with unchecked items carrying the supplied labels."""
        self.clear()
        for text in texts:
            self.addCheckableText(text)

    def items(self) -> Iterable[QStandardItem]:
        """Yield populated standard items from the current model."""
        model = self._item_model
        for row in range(model.rowCount()):
            item = model.item(row)
            assert item is not None, "CheckableComboBox rows must contain standard items."
            yield item

    def checkedItems(self) -> Sequence[QStandardItem]:
        """Return checked standard items in model order."""
        return tuple(item for item in self.items() if item.checkState() == Qt.CheckState.Checked)

    def checkedData(self) -> Sequence[Any]:
        """Return the stored Qt data of checked items in model order."""
        return tuple(item.data() for item in self.checkedItems())

    def checkedTexts(self) -> Sequence[str]:
        """Return the labels of checked items in model order."""
        return tuple(item.text() for item in self.checkedItems())

    def setCheckedTexts(self, texts: Sequence[str]) -> None:
        """Check items with matching labels and clear every other check state."""
        for item in self.items():
            item.setCheckState(Qt.CheckState.Checked if (item.text() in texts) else Qt.CheckState.Unchecked)

    def setCheckedData(self, data_items: Sequence[Any] | enum.Flag) -> None:
        """Check items selected by their stored data or membership in an enum flag."""
        for item in self.items():
            item.setCheckState(Qt.CheckState.Checked if (item.data() in data_items) else Qt.CheckState.Unchecked)

    @property
    def _line_edit(self) -> QLineEdit:
        """Return the line edit required by this editable combo box."""
        line_edit = self.lineEdit()
        assert line_edit is not None, "CheckableComboBox must remain editable."
        return line_edit

    @property
    def _item_model(self) -> QStandardItemModel:
        """Return the standard-item model installed for checkable rows."""
        model = self.model()
        assert isinstance(model, QStandardItemModel), "CheckableComboBox requires a QStandardItemModel."
        return model

    @property
    def _view(self) -> QAbstractItemView:
        view = self.view()
        assert view is not None, "CheckableComboBox requires a popup view."
        return view

    @property
    def _viewport(self) -> QWidget:
        """Return the popup viewport on which this widget filters mouse releases."""
        viewport = self._view.viewport()
        assert viewport is not None, "The popup view must have a viewport."
        return viewport


class ChkComboTryWindow(QDialog):
    items = (
        "Milk",
        "Eggs",
        "Butter",
        "Cheese",
        "Yogurt",
        "Chicken",
        "Fish",
        "Potatoes",
        "Carrots",
        "Onions",
        "Garlic",
        "Sugar",
        "Salt",
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Test playground")
        self.setLayout(main_layout := QVBoxLayout())
        combo_box = CheckableComboBox()
        print_button = QPushButton("Print Values")
        main_layout.addWidget(combo_box)
        main_layout.addWidget(print_button)
        combo_box.setCheckableTexts(self.items)
        combo_box.setCheckedTexts(self.items[3:6])
        qconnect(print_button.clicked, lambda: print("\n".join(combo_box.checkedTexts())))


def main() -> None:
    """Run the standalone checkable-combobox demonstration."""
    app = QApplication(sys.argv)
    window = ChkComboTryWindow()
    window.show()
    window.resize(480, 320)
    app.exit(app.exec())


if __name__ == "__main__":
    main()
