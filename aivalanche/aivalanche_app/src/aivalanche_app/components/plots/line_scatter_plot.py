import pyqtgraph as pg, numpy as np
from PySide6.QtWidgets import QMenu
from aivalanche_app.paths import home_icon_path, log_x_icon_path, log_y_icon_path, lin_x_icon_path, lin_y_icon_path
from aivalanche_app.components.plots.plot_button import plot_button

class line_scatter_plot(pg.PlotItem):
    
    def __init__(self, title = None, style = None):
        # if title is None:
        #     super().__init__()
        # else:
        super().__init__(title = title)
        
        self.plot_colors = style.PLOT_COLORS
    
        self.items = []
        
        self.hideButtons()
        
        self.legend = self.addLegend(brush = '#0000000A')        
        self.showGrid(x = True, y = True, alpha = 0.2)
        
        # # Add plot buttons     
        # buttons_height = 20
        
        # self.scale_y_button = plot_button(image_file_1 = log_y_icon_path, image_file_2 = lin_y_icon_path, height = buttons_height, parent_item = self)
        # self.scale_y_button.clicked.connect(self.toggle_y_scale)    
        
        # self.scale_x_button = plot_button(image_file_1 = log_x_icon_path, image_file_2 = lin_x_icon_path, height = buttons_height, parent_item = self)
        # self.scale_x_button.clicked.connect(self.toggle_x_scale)   

    
    def add_scatter_plot(self, x = None, y = None, id = None, **kwargs):
        
        if x is None or y is None:
            print('WARNING: no plot is added because x or y is none.')
            return
        
        if isinstance(x, list):
            x = np.array(x)
            
        if isinstance(y, list):
            y = np.array(y)
            
        if x.shape != y.shape:
            print('WARNING: no plot is added because x or y have not the same length.')
            return
        
        if 'symbolBrush' not in kwargs.keys():
            index = len(self.items) % len(self.plot_colors)
            kwargs['symbolBrush'] = self.plot_colors[index]
    
        # Create a PlotDataItem for scatter plot
        temp = pg.PlotDataItem(x, y, pen = None, **kwargs)
        self.items.append({'id': id, 'plot': temp})
        self.addItem(temp)
        
        self.legend.addItem(temp, id)


    # def resizeEvent(self, ev):
    #     # btnRect = self.mapRectFromItem(self.scale_y_button, self.autoBtn.boundingRect())
    #     # y = self.size().height() - btnRect.height()
    #     self.scale_y_button.setPos(0, 0)
    #     self.scale_x_button.setPos(50, 0)
        
    #     super().resizeEvent(ev)
        
    #     # if self.autoBtn is None:  ## already closed down
    #     #     return
    #     # btnRect = self.mapRectFromItem(self.autoBtn, self.autoBtn.boundingRect())
    #     # y = self.size().height() - btnRect.height()
    #     # self.autoBtn.setPos(0, y)
        
        
    # def updateButtons(self):
    #     super().updateButtons()
    #     # try:
    #     #     if self._exportOpts is False and self.mouseHovering and not self.buttonsHidden and not all(self.vb.autoRangeEnabled()):
    #     #         self.autoBtn.show()
    #     #     else:
    #     #         self.autoBtn.hide()
    #     # except RuntimeError:
    #     #     pass  # this can happen if the plot has been deleted.


    # def toggle_y_scale(self):
    #     print('log_y pressed')
        
        
    # def toggle_x_scale(self):
    #     print('log_x pressed')

