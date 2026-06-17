"""
Custom FlowLayout that wraps child widgets like text in a paragraph.
Based on the Qt FlowLayout example, adapted for PySide6.
"""

from PySide6.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QWidget
from PySide6.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """
    A layout that arranges widgets horizontally, wrapping to the next line
    when there isn't enough horizontal space. Similar to CSS flexbox with
    flex-wrap: wrap.
    """

    def __init__(self, parent=None, h_spacing=4, v_spacing=4):
        super().__init__(parent)
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._item_list: list[QLayoutItem] = []

    def addItem(self, item: QLayoutItem):
        self._item_list.append(item)

    def count(self) -> int:
        return len(self._item_list)

    def itemAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def horizontalSpacing(self) -> int:
        return self._h_spacing

    def verticalSpacing(self) -> int:
        return self._v_spacing

    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom()
        )
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        """
        Arrange items within the given rect.

        Args:
            rect: The available rectangle to lay out widgets in.
            test_only: If True, don't actually move widgets, just calculate height.

        Returns:
            The total height needed for the layout.
        """
        margins = self.contentsMargins()
        effective_rect = rect.adjusted(
            margins.left(), margins.top(),
            -margins.right(), -margins.bottom()
        )

        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._item_list:
            widget = item.widget()

            # Check for line-break markers
            if widget and widget.property("is_line_break"):
                # Force a new line
                x = effective_rect.x()
                y += line_height + self._v_spacing
                line_height = 0
                if not test_only:
                    # Hide the line-break widget (it's just a spacer)
                    widget.setGeometry(QRect(x, y, 0, 0))
                continue

            item_size = item.sizeHint()
            h_space = self._h_spacing
            v_space = self._v_spacing

            # Check if we need to wrap to next line
            next_x = x + item_size.width() + h_space
            if next_x - h_space > effective_rect.right() + 1 and line_height > 0:
                x = effective_rect.x()
                y += line_height + v_space
                line_height = 0
                next_x = x + item_size.width() + h_space

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item_size))

            x = next_x
            line_height = max(line_height, item_size.height())

        return y + line_height - rect.y() + margins.bottom()

    def clear(self):
        """Remove and delete all items from the layout."""
        while self.count():
            item = self.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()
