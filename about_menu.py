# Copyright: (C) 2021 Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt import mw
from aqt.qt import *
from aqt.utils import openLink
from aqt.webview import AnkiWebView

from .consts import (
    ABOUT_MSG,
    ADDON_SERIES,
    BUTTON_HEIGHT,
    CHAT_ICON_PATH,
    COMMUNITY_LINK,
    DIALOG_NAME,
    DONATE_ICON_PATH,
    DONATE_LINK,
    ICON_SIDE_LEN,
)
from .restore_geom_dialog import AnkiSaveAndRestoreGeomDialog


def garbage_collect_on_dialog_finish(dialog: QDialog) -> None:
    """Register the dialog for cleanup when supported by the active Anki window."""
    try:
        mw.garbage_collect_on_dialog_finish(dialog)
    except AttributeError:
        pass
    else:
        print(f"dialog '{getattr(dialog, 'name', 'undefined')}' will be deleted on finish")


def disable_help_button(dialog: QDialog) -> None:
    """Hide the dialog help button on Anki versions that expose the helper."""
    try:
        from aqt.utils import disable_help_button as _disable_help_button

        _disable_help_button(dialog)
    except ImportError:
        pass


def tweak_window(dialog: QDialog) -> None:
    garbage_collect_on_dialog_finish(dialog)
    disable_help_button(dialog)


class AboutDialog(AnkiSaveAndRestoreGeomDialog):
    """Display shared add-on information while preserving the dialog's geometry."""

    name: str = "ajt__about_dialog"

    def __init__(self, parent: QWidget, *args, **kwargs) -> None:
        """Build the shared About window using the supplied Anki parent."""
        super().__init__(parent=parent or mw, *args, **kwargs)
        tweak_window(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(f"{DIALOG_NAME} {ADDON_SERIES}")
        self.setSizePolicy(self.make_size_policy())
        self.setMinimumSize(320, 240)
        self.setLayout(self.make_root_layout())

    def make_about_webview(self, html_content: str) -> AnkiWebView:
        """Create the named, nonzoomable webview used for the About message."""
        webview = AnkiWebView(parent=self)
        webview.setProperty("url", QUrl("about:blank"))
        webview.setObjectName(self.name)
        webview.stdHtml(html_content, js=[])
        webview.setMinimumSize(480, 320)
        webview.disable_zoom()
        return webview

    def make_button_box(self) -> QLayout:
        """Arrange the close button and shared community and donation links."""
        but_box = QHBoxLayout()
        but_box.addWidget(self._make_ok_button())
        but_box.addStretch()
        but_box.addWidget(self._make_community_button())
        but_box.addWidget(self._make_donate_button())

        return but_box

    def _make_ok_button(self) -> QPushButton:
        """Create the close button without passing Qt's checked flag to accept."""
        but = QPushButton("Ok")
        # The geometry-aware Python method must not receive QPushButton's checked flag.
        # https://doc.qt.io/qt-6/qabstractbutton.html#clicked
        qconnect(but.clicked, lambda: self.accept())
        but.setFixedHeight(BUTTON_HEIGHT)
        return but

    def _make_community_button(self) -> QPushButton:
        """Create the button for joining the Ajatt-Tools community."""
        return self._make_link_button("Join our community", link=COMMUNITY_LINK, icon_path=CHAT_ICON_PATH)

    def _make_donate_button(self) -> QPushButton:
        """Create the button for supporting Ajatt-Tools development."""
        return self._make_link_button("Donate", link=DONATE_LINK, icon_path=DONATE_ICON_PATH)

    @staticmethod
    def _make_link_button(text: str, *, link: str, icon_path: str) -> QPushButton:
        """Create a consistently styled button that opens its configured link."""
        but = QPushButton(text)
        # Discard clicked's checked flag. The destination is fixed for this button.
        # https://doc.qt.io/qt-6/qabstractbutton.html#clicked
        qconnect(but.clicked, lambda: openLink(link))
        but.setIcon(QIcon(icon_path))
        but.setIconSize(QSize(ICON_SIDE_LEN, ICON_SIDE_LEN))
        but.setFixedHeight(BUTTON_HEIGHT)
        return but

    def make_root_layout(self) -> QLayout:
        root_layout = QVBoxLayout()
        root_layout.addWidget(self.make_about_webview(ABOUT_MSG))
        root_layout.addLayout(self.make_button_box())
        return root_layout

    def make_size_policy(self) -> QSizePolicy:
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        return size_policy


def addon_folder_name() -> str:
    return "".join(__name__.split(".")[:1])


def menu_root_entry() -> QMenu:
    if not hasattr(mw.form, "ajt_root_menu"):
        mw.form.ajt_root_menu = QMenu(f"&{ADDON_SERIES}", mw)
        mw.form.menubar.insertMenu(mw.form.menuHelp.menuAction(), mw.form.ajt_root_menu)
        mw.form.ajt_root_menu.addAction(create_about_action(mw.form.ajt_root_menu))
        mw.form.ajt_root_menu.addSeparator()
        print(f"{addon_folder_name()} inserted a new menu.")
    return mw.form.ajt_root_menu


def create_about_action(parent: QWidget) -> QAction:
    """Create a menu action that opens the modal About dialog."""

    def open_about_dialog() -> int:
        """Open the dialog and return its modal result."""
        dialog = AboutDialog(mw)
        return dialog.exec()

    action = QAction(f"{DIALOG_NAME}...", parent)
    # Note: set menu role to prevent Anki from repositioning the menu on macOS.
    # This is a known issue that occasionally occurs with some add-ons and macOS.
    action.setMenuRole(QAction.MenuRole.NoRole)
    # QAction's checked flag is unrelated to creating the dialog.
    # https://doc.qt.io/qt-6/qaction.html#triggered
    qconnect(action.triggered, lambda: open_about_dialog())
    return action
