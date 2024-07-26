from PySide6.QtWidgets import QMenu
from aivalanche_app.paths import home_icon_path, log_x_icon_path, log_y_icon_path, lin_x_icon_path, lin_y_icon_path
from aivalanche_app.components.plots.plot_button import plot_button
import pyqtgraph as pg, numpy as np
from pyqtgraph import PlotItem, ViewBox

class heatmap_plot(PlotItem):
    
    def __init__(self, parent = None, data = None, title = None, x_axis_label = None, y_axis_label = None, style = None):
        
        vb = ViewBox(enableMenu = False, enableMouse = False, defaultPadding = 0)
        super().__init__(parent = parent, viewBox = vb)
        
        self.data = data
        self.style = style        
        self.plot_colors = style.colors['plot_colors']
        
        self.hideButtons()
        
        self.hist, edges = np.histogram(self.data, bins = 100, range = (0, 1))
        self.image = pg.ImageItem(image = self.hist.reshape(1,-1))
        self.image.setColorMap('CET-R4')
        self.addItem(self.image)
        
        self.set_title(title)
        self.add_x_axis_label(x_axis_label)
        self.hide_ticks()
        
    def set_title(self, title = 'title'):
        self.title = title
        if title is not None:
            self.setTitle(title, color = self.style.colors['plot_text'])
            
    def add_x_axis_label(self, label: str = 'x axis label'):
        self.x_axis_label = label
        if label is not None:
            self.setLabel('bottom', text = label, color = self.style.colors['plot_text'])
            
    def hide_ticks(self):
        x_axis = self.getAxis('bottom')
        x_axis.setStyle(showValues = False, tickLength = 0)
        x_axis.setPen((0, 0, 0, 0))
        
        self.showAxis('left', show=False)
