from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush
from aivalanche_app.paths import image_placeholder_path

class custom_image(QPushButton):
    def __init__(self, parent = None,
                 image_path = image_placeholder_path, image_width = None, image_height = None, minimum_width = None, minimum_height = None, resize: str = 'cover',
                 padding_left = 0, padding_top = 0, padding_right = 0, padding_bottom = 0,
                 back_color = None, back_hover_color = None, back_click_color = None,
                 front_color = None, front_hover_color = None, front_click_color = None, on_click = None):
        super().__init__(parent = parent)
        
        self.resize = resize
        self.image_width = image_width
        self.image_height = image_height
        self.padding_left = padding_left
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom
        self.padding_right = padding_right
        self.back_color = back_color
        self.back_hover_color = back_hover_color
        self.back_click_color = back_click_color
        self.front_color = front_color
        self.front_hover_color = front_hover_color
        self.front_click_color = front_click_color
        self.image_path = image_path
        self.on_click = on_click
        
        if self.image_path is not None:
            self.image = QPixmap(image_path)
            self.image_aspect_ratio = self.image.width() / self.image.height()
                
        if minimum_width is not None:
            self.setMinimumWidth(minimum_width)
            
        if minimum_height is not None:
            self.setMinimumHeight(minimum_height)
        
        if self.image_height is not None and self.image_width is not None:
            self.setFixedSize(self.image_width, self.image_height)
        elif self.image_height is not None and self.image_width is None:
            self.setFixedHeight(self.image_height)
        elif self.image_width is not None and self.image_height is None:
            self.setFixedWidth(self.image_width)
        
        # Declare mouse events
        self.hovered = False
        self.is_clicked = False

        # Set up button properties
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        
        if self.on_click is not None:
            self.clicked.connect(self.on_click)
        
        
    def enterEvent(self, event):
        self.hovered = True
        self.update()
        

    def leaveEvent(self, event):
        self.hovered = False
        self.update()
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked = True
            self.update()
            

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked = False
            self.update()
            if self.rect().contains(event.pos()):
                self.click()
            

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        (x, y, w, h), (sx, sy, sw, sh) = self.get_dimensions()
        
        # Draw the background
        bg_color = self.get_background_color()
        if bg_color is not None:
            painter.setBrush(QBrush(bg_color, Qt.SolidPattern))
            painter.drawRect(x, y, w, h)
        
        # Draw the image
        painter.drawPixmap(x, y, w, h, self.image, sx, sy, sw, sh)
        
        # Draw the foreground
        fg_color = self.get_foreground_color()
        if fg_color is not None:
            painter.setBrush(QBrush(fg_color, Qt.SolidPattern))
            painter.drawRect(x, y, w, h)
            
        
    def get_dimensions(self):
        # Get viewport dimensions
        rect_width = self.rect().width() - self.padding_left - self.padding_right
        rect_height = self.rect().height() - self.padding_top - self.padding_bottom
        rect_aspect_ratio = rect_width / rect_height
        
        # Calculate the image width and height
        if self.image_path is None:
            image_width = rect_width
            image_height = rect_height
            self.image_aspect_ratio = rect_aspect_ratio
        elif (rect_aspect_ratio >= self.image_aspect_ratio and self.resize == 'cover') or (rect_aspect_ratio < self.image_aspect_ratio and self.resize == 'fit'):
            image_width = rect_width
            image_height = image_width / self.image_aspect_ratio
        else:
            image_height = rect_height
            image_width = image_height * self.image_aspect_ratio
        
        # Calculate the scale of the image w.r.t. the original image
        scale = image_width / self.image.width()
        
        # Calculate dimenions
        if self.resize == 'cover':
            x = self.padding_left
            y = self.padding_top
            w = rect_width
            h = rect_height
            if rect_aspect_ratio >= self.image_aspect_ratio:
                sx = 0
                sy = (image_height - rect_height) / 2 / scale
                sw = self.image.width()
                sh = self.image.height() - sy * 2
            else:
                sx = (image_width - rect_width) / 2 / scale
                sy = 0
                sw = self.image.width() - sx * 2
                sh = self.image.height()
        else:
            sx = 0
            sy = 0
            sw = self.image.width()
            sh = self.image.height()
            if rect_aspect_ratio >= self.image_aspect_ratio:
                x = self.padding_left + (rect_width - image_width) / 2
                y = self.padding_top
            else:
                x = self.padding_left
                y = self.padding_top + (rect_height - image_height) / 2
                
            w = image_width
            h = image_height
        
        return (x, y, w, h), (sx, sy, sw, sh)
    
    
    def get_background_color(self):
        if self.is_clicked and self.back_click_color is not None:
            if isinstance(self.back_click_color, tuple):
                return QColor(*self.back_click_color)
            else:
                return QColor(self.back_click_color)
        elif self.hovered and self.back_hover_color is not None:
            if isinstance(self.back_hover_color, tuple):
                return QColor(*self.back_hover_color)
            else:
                return QColor(self.back_hover_color)
        elif self.back_color is not None:
            if isinstance(self.back_color, tuple):
                return QColor(*self.back_color)
            else:
                return QColor(self.back_color)
        return None
    
    
    def get_foreground_color(self):
        if self.is_clicked and self.front_click_color is not None:
            if isinstance(self.front_click_color, tuple):
                return QColor(*self.front_click_color)
            else:
                return QColor(self.front_click_color)
        elif self.hovered and self.front_hover_color is not None:
            if isinstance(self.front_hover_color, tuple):
                return QColor(*self.front_hover_color)
            else:
                return QColor(self.front_hover_color)
        elif self.front_color is not None:
            if isinstance(self.front_color, tuple):
                return QColor(*self.front_color)
            else:
                return QColor(self.front_color)
        return None