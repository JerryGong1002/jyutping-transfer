"""
Jyutping Generator — 粤拼生成桌面程序
Entry point for the application.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from core import __version__


def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("粤拼生成")
    app.setApplicationDisplayName("粤拼生成 — Jyutping Generator")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("JyutpingTools")

    # Set default font
    default_font = QFont("PingFang SC", 10, QFont.Weight.Bold)
    default_font.insertSubstitutions("PingFang SC", ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei"])
    default_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(default_font)

    # Import and show main window
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
