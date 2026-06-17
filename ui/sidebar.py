"""
Sidebar: Navigation panel with New/History/Favorites tabs and entry lists.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QStackedWidget, QMenu,
    QInputDialog, QMessageBox, QSizePolicy, QFrame
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont

from core import __version__
from ui.styles import COLORS, SIDEBAR_STYLESHEET


class Sidebar(QWidget):
    """
    Left sidebar with navigation buttons and entry lists.
    Provides New Conversion, History, and Favorites views.
    """

    # Signals
    new_conversion_requested = Signal()
    history_entry_selected = Signal(int)     # entry_id
    favorite_entry_selected = Signal(int)    # entry_id
    history_entry_deleted = Signal(int)      # entry_id
    favorite_entry_deleted = Signal(int)     # entry_id
    history_entry_renamed = Signal(int, str) # entry_id, new_title
    favorite_entry_renamed = Signal(int, str)# entry_id, new_title

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self.setStyleSheet(SIDEBAR_STYLESHEET)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── App Branding ──
        app_title = QLabel("粤拼生成")
        app_title.setObjectName("app_title")
        layout.addWidget(app_title)

        app_subtitle = QLabel("Jyutping Generator")
        app_subtitle.setObjectName("app_subtitle")
        layout.addWidget(app_subtitle)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {COLORS['border']};")
        layout.addWidget(sep)

        # ── Navigation Header ──
        nav_header = QLabel("导航")
        nav_header.setObjectName("sidebar_header")
        layout.addWidget(nav_header)

        # ── Navigation Buttons ──
        self._btn_new = self._create_nav_button("📝  新建转换", 0)
        self._btn_history = self._create_nav_button("📜  历史记录", 1)
        self._btn_favorites = self._create_nav_button("⭐  收藏夹", 2)

        layout.addWidget(self._btn_new)
        layout.addWidget(self._btn_history)
        layout.addWidget(self._btn_favorites)

        # ── Separator ──
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {COLORS['border']}; margin: 8px 12px;")
        layout.addWidget(sep2)

        # ── Stacked content area ──
        self._stacked = QStackedWidget()

        # Page 0: Empty (new conversion mode)
        empty_page = QWidget()
        empty_layout = QVBoxLayout(empty_page)
        empty_label = QLabel(
            "输入歌词并转换\n即可开始使用"
        )
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 13px; padding: 30px;"
        )
        empty_layout.addWidget(empty_label)
        empty_layout.addStretch()
        self._stacked.addWidget(empty_page)

        # Page 1: History list
        self._history_list = QListWidget()
        self._history_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._history_list.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(pos, 'history')
        )
        self._history_list.itemDoubleClicked.connect(self._on_history_double_click)
        self._stacked.addWidget(self._history_list)

        # Page 2: Favorites list
        self._favorites_list = QListWidget()
        self._favorites_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._favorites_list.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(pos, 'favorites')
        )
        self._favorites_list.itemDoubleClicked.connect(self._on_favorite_double_click)
        self._stacked.addWidget(self._favorites_list)

        layout.addWidget(self._stacked, stretch=1)

        # ── Footer ──
        footer = QLabel(f"v{__version__}  ·  粤语拼音自动标注")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 10px; padding: 10px;"
        )
        layout.addWidget(footer)

        # Default to new conversion
        self._select_nav(0)

    def _create_nav_button(self, text: str, index: int) -> QPushButton:
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setObjectName("nav_button")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self._select_nav(index))
        return btn

    def _select_nav(self, index: int):
        """Switch the active navigation tab."""
        # Update button states
        for i, btn in enumerate([self._btn_new, self._btn_history, self._btn_favorites]):
            btn.setChecked(i == index)

        self._stacked.setCurrentIndex(index)

        if index == 0:
            self.new_conversion_requested.emit()

    def _on_history_double_click(self, item: QListWidgetItem):
        """Handle double-click on a history entry."""
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        if entry_id is not None:
            self.history_entry_selected.emit(entry_id)

    def _on_favorite_double_click(self, item: QListWidgetItem):
        """Handle double-click on a favorites entry."""
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        if entry_id is not None:
            self.favorite_entry_selected.emit(entry_id)

    def _show_context_menu(self, pos, table: str):
        """Show right-click context menu for list items."""
        list_widget = self._history_list if table == 'history' else self._favorites_list
        item = list_widget.itemAt(pos)
        if not item:
            return

        entry_id = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)

        # Rename action
        rename_action = menu.addAction("✏️  重命名")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️  删除")

        action = menu.exec(list_widget.viewport().mapToGlobal(pos))

        if action == rename_action:
            new_title, ok = QInputDialog.getText(
                self, "重命名", "请输入新标题:", text=item.text()
            )
            if ok and new_title.strip():
                item.setText(new_title.strip())
                if table == 'history':
                    self.history_entry_renamed.emit(entry_id, new_title.strip())
                else:
                    self.favorite_entry_renamed.emit(entry_id, new_title.strip())

        elif action == delete_action:
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除「{item.text()}」吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                row = list_widget.row(item)
                list_widget.takeItem(row)
                if table == 'history':
                    self.history_entry_deleted.emit(entry_id)
                else:
                    self.favorite_entry_deleted.emit(entry_id)

    def refresh_history(self, entries: list[dict]):
        """Refresh the history list with data from the database."""
        self._history_list.clear()
        for entry in entries:
            item = QListWidgetItem(entry['title'])
            item.setData(Qt.ItemDataRole.UserRole, entry['id'])
            item.setToolTip(
                f"创建时间: {entry.get('created_at', 'N/A')}\n"
                f"双击以恢复此歌词"
            )
            self._history_list.addItem(item)

    def refresh_favorites(self, entries: list[dict]):
        """Refresh the favorites list with data from the database."""
        self._favorites_list.clear()
        for entry in entries:
            item = QListWidgetItem(entry['title'])
            item.setData(Qt.ItemDataRole.UserRole, entry['id'])
            item.setToolTip(
                f"创建时间: {entry.get('created_at', 'N/A')}\n"
                f"双击以恢复此歌词"
            )
            self._favorites_list.addItem(item)

    def switch_to_history(self):
        """Programmatically switch to history tab."""
        self._select_nav(1)

    def switch_to_favorites(self):
        """Programmatically switch to favorites tab."""
        self._select_nav(2)
