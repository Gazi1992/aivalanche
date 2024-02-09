import pyqtgraph as pg

class plot_button(pg.ButtonItem):
    
    def __init__(self, image_file_1 = None, image_file_2 = None, width = None, height = None, parent_item = None, pixmap = None):
        super().__init__(image_file_1, width, parent_item, pixmap)   
        self.image_file_1 = image_file_1
        self.image_file_2 = image_file_2        
        self.active_image = image_file_1
        if height is not None and self.pixmap.height():
            s = float(height) / self.pixmap.height()
            self.setScale(s)
        self.setOpacity(0.5)
            
    def update_image(self, image_file = None):
        if image_file is not None:
            super().setImageFile(image_file)
            
    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)
        if self.image_file_2 is not None:
            if self.active_image == self.image_file_1:
                self.update_image(self.image_file_2)
                self.active_image = self.image_file_2
            elif self.active_image == self.image_file_2:
                self.update_image(self.image_file_1)
                self.active_image = self.image_file_1
                
    def hoverEvent(self, ev):
        if not self.enabled:
            return
        if ev.isEnter():
            self.setOpacity(1.0)
        elif ev.isExit():
            self.setOpacity(0.5)