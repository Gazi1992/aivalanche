from PySide6.QtWidgets import QMenu
from aivalanche_app.paths import home_icon_path, log_x_icon_path, log_y_icon_path, lin_x_icon_path, lin_y_icon_path
from aivalanche_app.components.plots.plot_button import plot_button
import pyqtgraph as pg, numpy as np

class heatmap_plot(pg.PlotItem):
    
    def __init__(self, parent = None, data = None, title = None, x_axis_label = None, y_axis_label = None, style = None):

        super().__init__(parent = parent, title = title)
        
        self.data = data
        self.style = style        
        self.plot_colors = style.colors['plot_colors']
        
        self.hideButtons()
                     
        self.image = pg.ImageItem(image = self.data)
        self.addItem(self.image)
        
        self.set_title(title)
        self.add_x_axis_label(x_axis_label)
        self.add_y_axis_label(y_axis_label)
        self.hide_ticks()
        
        # # Add plot buttons     
        # buttons_height = 20
        
        # self.scale_y_button = plot_button(image_file_1 = log_y_icon_path, image_file_2 = lin_y_icon_path, height = buttons_height, parent_item = self)
        # self.scale_y_button.clicked.connect(self.toggle_y_scale)    
        
        # self.scale_x_button = plot_button(image_file_1 = log_x_icon_path, image_file_2 = lin_x_icon_path, height = buttons_height, parent_item = self)
        # self.scale_x_button.clicked.connect(self.toggle_x_scale)   


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
            
            
    def hide_ticks(self):
        # Get the X and Y axes of the plot
        x_axis = self.getAxis('bottom')
        y_axis = self.getAxis('left')

        # Hide ticks on X and Y axes
        x_axis.setTicks([])
        y_axis.setTicks([])
        
        # Hide axis line on X and Y axes
        x_axis.setPen(pg.mkPen(color=(0, 0, 0, 0)))  # Transparent pen
        y_axis.setPen(pg.mkPen(color=(0, 0, 0, 0)))  # Transparent pen
        
        # Set limits to X and Y axes
        x_axis.setRange(0, 1)
        y_axis.setRange(0, len(self.data) - 1)