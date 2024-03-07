from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from aivalanche_app.resources.themes.style import style

class custom_label(QLabel):
    def __init__(self, parent = None, text = '', font_size = None, opacity = 1):
        super().__init__(parent = parent)
        self.style = style()
        self.setText(text)
        self.set_font_size(font_size)
        self.set_opacity(opacity)
        
    def set_font_size(self, font_size):
        if isinstance(font_size, str):
            if font_size in self.style.FONT_SIZES.keys():
                font_size = self.style.FONT_SIZES[font_size]
            else:
                font_size = None
                
        if font_size is not None:
            try:                
                font = self.font()
                font.setPointSize(font_size)
                self.setFont(font)
            except Exception as e:
                print(e)
    
    def set_opacity(self, opacity):
        opacity_effect = QGraphicsOpacityEffect(self)
        opacity_effect.setOpacity(opacity)
        self.setGraphicsEffect(opacity_effect)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        