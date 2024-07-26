from pyqtgraph import PlotItem, ViewBox, PlotDataItem
from PySide6.QtCore import Qt
import numpy as np

# Custom class to zoom in and out only when ctrl key is pressed.
class custom_viewbox(ViewBox):
    def wheelEvent(self, ev, axis = None):
        if ev.modifiers() == Qt.ControlModifier:
            super().wheelEvent(ev)
        else:
            ev.ignore()
            
class loss_evolution_plot(PlotItem):
    def __init__(self, parent = None, x_axis_label = 'x axis', y_axis_label = 'y axis', style = None):

        custom_vb = custom_viewbox()
        super().__init__(parent = parent, viewBox = custom_vb)
        
        self._data = None
        self.clearPlots()
        self.style = style
                            
        self.showGrid(x = True, y = True, alpha = 0.5)
                
        self.x_axis = self.getAxis('bottom')
        self.x_axis.setPen(self.style.colors['plot_axis'])
        self.x_axis.setTextPen(self.style.colors['plot_text'])
        self.x_axis.setTickPen(self.style.colors['plot_grid'])
        
        self.y_axis = self.getAxis('left')
        self.y_axis.setPen(self.style.colors['plot_axis'])
        self.y_axis.setTextPen(self.style.colors['plot_text'])
        self.y_axis.setTickPen(self.style.colors['plot_grid'])
        
        self.setLogMode(y = True)
        
        self.hideButtons()        
        
        self.add_x_axis_label(x_axis_label)
        self.add_y_axis_label(y_axis_label)
    
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.clearPlots()
        self.plot_data()
        self.update_x_axis()
        
    def set_title(self, title = 'title'):
        self.title = title
        if title is not None:
            self.setTitle(title, color = self.style.colors['plot_text'])

    def add_x_axis_label(self, label: str = 'x axis label'):
        self.x_axis_label = label
        if label is not None:
            self.setLabel('bottom', text = label, color = self.style.colors['plot_text'])

    def add_y_axis_label(self, label: str = 'y axis label'):
        self.y_axis_label = label
        if label is not None:
            self.setLabel('left', text = label, color = self.style.colors['plot_text'])

    def plot_data(self, **kwargs): 
        if self._data is not None:
            # Create a PlotDataItem for scatter plot and add it to the PlotItem
            x = self._data[:, 0]
            y = self._data[:, 1]
            temp = PlotDataItem(x, y, pen = None, symbolPen = None, symbolSize = 10, symbolBrush = (255, 92, 0, 200), **kwargs)
            self.addItem(temp)
        
    def update_data(self, data):
        self.data = data

    def update_x_axis(self):
        if self._data is not None and len(self._data) > 0:
            x = self._data[:, 0]
            x_min, x_max = np.min(x), np.max(x)
            padding = (x_max - x_min) * 0.05  # Add 5% padding on each side
            self.setXRange(x_min - padding, x_max + padding, padding=0)
            
    def clear_plot(self):
        self.data = None