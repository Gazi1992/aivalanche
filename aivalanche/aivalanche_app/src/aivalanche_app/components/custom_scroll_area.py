from PySide6.QtWidgets import QScrollArea

class custom_scroll_area(QScrollArea):
    def __init__(self, parent = None, on_resize_event: callable = None):
        super().__init__(parent)
        self.on_resize_event = on_resize_event
        self.setWidgetResizable(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)        
        if self.on_resize_event is not None:
            self.on_resize_event(event)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        