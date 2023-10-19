from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

class shadow_button(QPushButton):
    def __init__(self, parent = None, text = 'text', blur_radius = 10, shadow_color = QColor(0, 0, 0, 100)):
        super().__init__(parent = parent, text = text)

        # Create a QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)  # Set blur radius (adjust as needed)
        shadow.setColor(shadow_color)  # Set shadow color and alpha

        # Apply the drop shadow effect to the button
        self.setGraphicsEffect(shadow)

