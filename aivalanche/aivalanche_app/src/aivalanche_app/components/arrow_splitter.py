from PySide6.QtWidgets import QSplitter
from PySide6.QtGui import QPainter, QColor, QBrush, QPen

class arrow_splitter(QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paintEvent(self, event):
        super().paintEvent(event)

        # Create a QPainter to draw on the splitter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set the color and thickness of the arrow
        arrow_color = QColor(255, 0, 0)
        arrow_pen = QPen(arrow_color)
        arrow_pen.setWidth(2)
        painter.setPen(arrow_pen)
        painter.setBrush(QBrush(arrow_color))

        # Calculate the position of the dots along the splitter handle
        handle_rect = self.handle(1).geometry()
        arrow_size = 10
        arrow_x = handle_rect.center().x() - arrow_size // 2
        arrow_y = handle_rect.center().y() - arrow_size // 2

        # Draw an arrow on the splitter border
        painter.drawLine(arrow_x, arrow_y, arrow_x - arrow_size, arrow_y + arrow_size)
