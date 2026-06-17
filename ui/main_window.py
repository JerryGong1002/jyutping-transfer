"""
Main Window: Assembles all UI components and connects business logic.
"""

import os
import re
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QDesktopServices

from core.converter import convert_lyrics, tokens_to_json, tokens_from_json, LyricsToken
from core.database import LyricsDatabase
from ui.sidebar import Sidebar
from ui.input_panel import InputPanel
from ui.result_panel import ResultPanel
from ui.styles import MAIN_STYLESHEET, COLORS


class MainWindow(QMainWindow):
    """
    Main application window for the Jyutping Lyrics Converter.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("粤拼生成 — Jyutping Generator")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # Initialize database
        self._db = LyricsDatabase()

        # Current state
        self._current_tokens: list[LyricsToken] = []
        self._current_raw_text: str = ""

        # Apply global stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)

        self._setup_ui()
        self._connect_signals()
        self._refresh_sidebar_data()

        # Disable export buttons initially
        self._input_panel.set_export_enabled(False)

        # Show status
        self.statusBar().showMessage("就绪 — 请输入歌词并点击「开始转换」")

    def _setup_ui(self):
        """Build the main window layout."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        self._sidebar = Sidebar()
        main_layout.addWidget(self._sidebar)

        # ── Main Work Area ──
        work_area = QWidget()
        work_area.setStyleSheet(f"background-color: {COLORS['bg_darkest']};")
        work_layout = QVBoxLayout(work_area)
        work_layout.setContentsMargins(16, 12, 16, 8)
        work_layout.setSpacing(8)

        # Splitter between input and result panels
        self._splitter = QSplitter(Qt.Orientation.Vertical)
        self._splitter.setHandleWidth(3)

        self._input_panel = InputPanel()
        self._result_panel = ResultPanel()

        self._splitter.addWidget(self._input_panel)
        self._splitter.addWidget(self._result_panel)
        self._splitter.setStretchFactor(0, 2)
        self._splitter.setStretchFactor(1, 3)

        work_layout.addWidget(self._splitter)

        main_layout.addWidget(work_area, stretch=1)

        # ── Status Bar ──
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

    def _connect_signals(self):
        """Wire up all signals between components."""
        # Input panel signals
        self._input_panel.convert_requested.connect(self._on_convert)
        self._input_panel.favorite_requested.connect(self._on_save_favorite)
        self._input_panel.export_png_requested.connect(self._on_export_png)
        self._input_panel.export_pdf_requested.connect(self._on_export_pdf)
        self._input_panel.spacing_mode_changed.connect(self._on_spacing_mode_changed)
        self._input_panel.font_mode_changed.connect(self._on_font_mode_changed)

        # Result panel signals
        self._result_panel.token_changed.connect(self._on_token_changed)

        # Sidebar signals
        self._sidebar.history_entry_selected.connect(self._on_load_history)
        self._sidebar.favorite_entry_selected.connect(self._on_load_favorite)
        self._sidebar.history_entry_deleted.connect(
            lambda eid: self._db.delete_history(eid)
        )
        self._sidebar.favorite_entry_deleted.connect(
            lambda eid: self._db.delete_favorite(eid)
        )
        self._sidebar.history_entry_renamed.connect(
            lambda eid, title: self._db.update_title('history', eid, title)
        )
        self._sidebar.favorite_entry_renamed.connect(
            lambda eid, title: self._db.update_title('favorites', eid, title)
        )

    def _refresh_sidebar_data(self):
        self._sidebar.refresh_history(self._db.get_history())
        self._sidebar.refresh_favorites(self._db.get_favorites())

    # ──────────────────── Spacing Mode ────────────────────

    def _on_spacing_mode_changed(self, mode: str):
        """Switch the result panel spacing mode live."""
        self._result_panel.set_spacing_mode(mode)

    def _on_font_mode_changed(self, mode: str):
        """Switch the result panel font live."""
        self._result_panel.set_font_mode(mode)

    # ──────────────────── Conversion ────────────────────

    def _on_convert(self, text: str, cc_mode: str):
        self.statusBar().showMessage("正在转换...")
        QApplication.processEvents()

        try:
            tokens = convert_lyrics(text, cc_mode)
            self._current_tokens = tokens
            self._current_raw_text = text

            # Apply current spacing mode
            self._result_panel.set_spacing_mode(self._input_panel.get_spacing_mode())
            self._result_panel.render_tokens(tokens)
            self._input_panel.set_export_enabled(True)

            # Auto-save to history
            title = self._generate_sidebar_title(text)
            tokens_json = tokens_to_json(tokens)
            self._db.save_history(title, text, tokens_json)
            self._refresh_sidebar_data()

            total = sum(1 for t in tokens if not t.is_punctuation)
            poly = sum(1 for t in tokens if t.is_polyphonic)
            self.statusBar().showMessage(
                f"转换完成 — {total} 个汉字，{poly} 个多音字"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "转换错误",
                f"转换过程中发生错误：\n\n{str(e)}\n\n"
                f"请检查输入内容后重试。"
            )
            self.statusBar().showMessage("转换失败")

    def _on_token_changed(self, token_index: int, new_jyutping: str):
        self.statusBar().showMessage(
            f"已更新：第 {token_index + 1} 个字的读音为 {new_jyutping}"
        )

    # ──────────────────── History & Favorites ────────────────────

    def _on_load_history(self, entry_id: int):
        self._load_entry('history', entry_id)

    def _on_load_favorite(self, entry_id: int):
        self._load_entry('favorites', entry_id)

    def _load_entry(self, table: str, entry_id: int):
        entry = self._db.load_entry(table, entry_id)
        if not entry:
            QMessageBox.warning(self, "错误", "无法找到该记录。")
            return

        self._input_panel.set_text(entry['raw_content'])
        self._current_raw_text = entry['raw_content']

        saved_title = entry['title']
        first_line = entry['raw_content'].strip().split('\n')[0].strip() if entry['raw_content'].strip() else ""
        first_line_short = first_line[:15] + "..." if len(first_line) > 15 else first_line
        
        if " - " in saved_title:
            parts = saved_title.split(" - ", 1)
            self._input_panel.set_meta_info(parts[0], parts[1])
        elif saved_title != first_line_short and saved_title != first_line and saved_title != "未命名歌词":
            self._input_panel.set_meta_info(saved_title, "")
        else:
            self._input_panel.set_meta_info("", "")

        try:
            tokens = tokens_from_json(entry['converted_json'])
            self._current_tokens = tokens
            self._result_panel.set_spacing_mode(self._input_panel.get_spacing_mode())
            self._result_panel.render_tokens(tokens)
            self._input_panel.set_export_enabled(True)

            self.statusBar().showMessage(
                f"已恢复「{entry['title']}」的编辑状态"
            )
        except Exception as e:
            QMessageBox.warning(
                self, "恢复错误",
                f"恢复转换结果时出错：\n{str(e)}"
            )

    def _on_save_favorite(self):
        if not self._current_tokens:
            QMessageBox.information(
                self, "提示", "请先转换歌词后再收藏。"
            )
            return

        title = self._generate_sidebar_title(self._current_raw_text)
        tokens_json = tokens_to_json(self._current_tokens)
        self._db.save_favorite(title, self._current_raw_text, tokens_json)
        self._refresh_sidebar_data()

        self.statusBar().showMessage(f"已收藏「{title}」")

    # ──────────────────── Export ────────────────────

    def _on_export_png(self, font_mode: str, spacing: float, spacing_mode: str):
        if not self._current_tokens:
            QMessageBox.information(self, "提示", "请先转换歌词后再导出。")
            return

        try:
            from export.image_export import export_to_png
            from PySide6.QtWidgets import QFileDialog

            default_title = self._generate_sidebar_title(self._current_raw_text)
            safe_title = re.sub(r'[\\/*?:"<>|]', "", default_title)

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出为图片",
                os.path.expanduser(f"~/Desktop/{safe_title}_Jyutping.png"),
                "PNG 图片 (*.png)"
            )
            if file_path:
                export_title = self._generate_export_title()
                export_to_png(
                    self._current_tokens, file_path,
                    font_mode=font_mode,
                    line_spacing_multiplier=spacing,
                    spacing_mode=spacing_mode,
                    title=export_title
                )
                self.statusBar().showMessage(f"图片已导出至 {file_path}")
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.critical(
                self, "导出错误",
                f"导出图片时发生错误：\n{str(e)}"
            )

    def _on_export_pdf(self, font_mode: str, spacing: float, spacing_mode: str):
        if not self._current_tokens:
            QMessageBox.information(self, "提示", "请先转换歌词后再导出。")
            return

        try:
            from export.pdf_export import export_to_pdf
            from PySide6.QtWidgets import QFileDialog

            default_title = self._generate_sidebar_title(self._current_raw_text)
            safe_title = re.sub(r'[\\/*?:"<>|]', "", default_title)

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出为PDF",
                os.path.expanduser(f"~/Desktop/{safe_title}_Jyutping.pdf"),
                "PDF 文件 (*.pdf)"
            )
            if file_path:
                export_title = self._generate_export_title()
                export_to_pdf(
                    self._current_tokens, file_path,
                    font_mode=font_mode,
                    line_spacing_multiplier=spacing,
                    spacing_mode=spacing_mode,
                    title=export_title
                )
                self.statusBar().showMessage(f"PDF已导出至 {file_path}")
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.critical(
                self, "导出错误",
                f"导出PDF时发生错误：\n{str(e)}"
            )

    # ──────────────────── Helpers ────────────────────

    def _generate_export_title(self) -> str:
        """
        Generate title for export (PNG/PDF).
        Returns empty string if user didn't input song/artist,
        so no title header is rendered in the output.
        """
        song, artist = self._input_panel.get_meta_info()
        if song and artist:
            return f"{song} - {artist}"
        elif song:
            return song
        return ""  # no title in export if nothing was entered

    def _generate_sidebar_title(self, text: str) -> str:
        """
        Generate title for sidebar history/favorites.
        Uses song/artist if provided, otherwise first line of lyrics.
        """
        song, artist = self._input_panel.get_meta_info()
        if song and artist:
            return f"{song} - {artist}"
        elif song:
            return song

        first_line = text.strip().split('\n')[0].strip()
        if len(first_line) > 15:
            return first_line[:15] + "..."
        return first_line or "未命名歌词"
