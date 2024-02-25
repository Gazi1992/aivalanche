import pyqtgraph as pg, numpy as np
from PySide6.QtWidgets import QMenu
from aivalanche_app.paths import home_icon_path, log_x_icon_path, log_y_icon_path, lin_x_icon_path, lin_y_icon_path
from aivalanche_app.components.plots.plot_button import plot_button


class line_scatter_plot(pg.PlotItem):
    
    def __init__(self, title = None, x_axis_label = None, y_axis_label = None, style = None):

        super().__init__(title = title)
        
        self.style = style        
        self.plot_colors = style.PLOT_COLORS
    
        self.clear_plot()
        
        self.hideButtons()
        
        self.legend = self.addLegend(brush = '#0000000A')        
        self.showGrid(x = True, y = True, alpha = 0.2)
        
        self.set_title(title)
        self.add_x_axis_label(x_axis_label)
        self.add_y_axis_label(y_axis_label)
        
        # # Add plot buttons     
        # buttons_height = 20
        
        # self.scale_y_button = plot_button(image_file_1 = log_y_icon_path, image_file_2 = lin_y_icon_path, height = buttons_height, parent_item = self)
        # self.scale_y_button.clicked.connect(self.toggle_y_scale)    
        
        # self.scale_x_button = plot_button(image_file_1 = log_x_icon_path, image_file_2 = lin_x_icon_path, height = buttons_height, parent_item = self)
        # self.scale_x_button.clicked.connect(self.toggle_x_scale)   

    @property
    def nr_curves(self):
        return len(self.plots.keys())
    
    
    def set_title(self, title = 'title'):
        self.title = title
        if title is not None:
            self.setTitle(title)
    
    
    def add_x_axis_label(self, label: str = 'x axis label'):
        self.x_axis_label = label
        if label is not None:
            self.setLabel('bottom', text = label)
        
        
    def add_y_axis_label(self, label: str = 'y axis label'):
        self.y_axis_label = label
        if label is not None:
            self.setLabel('left', text = label)

    
    def clear_plot(self):
        self.clearPlots()
        self.plots = {}
        self.total_nr_plots = 0
    

    def remove_curve(self, id = None):
        if id is None or id not in self.plots.keys():
            return
        
        self.removeItem(self.plots[id])
        del self.plots[id]
        
    
    def add_scatter_plot(self, x = None, y = None, id = None, add_to_legend = True, label = None, **kwargs):
        
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
            index = self.total_nr_plots % len(self.plot_colors)
            kwargs['symbolBrush'] = self.plot_colors[index]
    
        # Create a PlotDataItem for scatter plot and add it to the PlotItem
        temp = pg.PlotDataItem(x, y, pen = None, **kwargs)
        self.add_item(temp, id, add_to_legend, label)
                
    
    def add_item(self, item, id = None, add_to_legend = True, label = None,):
        self.addItem(item)
        
        # Update the plots
        if id is not None:
            self.plots[id] = item

            if add_to_legend:
                self.legend.addItem(item, label)
                
        self.total_nr_plots += 1
    
    
    def deep_copy(self):
        new_plot = line_scatter_plot(title = self.titleLabel.text, x_axis_label = self.getAxis('bottom').label.text,
                                     y_axis_label = self.getAxis('left').label.text, style = self.style)
        
        # Copy other relevant attributes or properties
        new_plot.plot_colors = self.plot_colors
        # ... (copy other attributes as needed)
    
        # Copy each scatter plot individually
        for id, plot in self.plots.items():
            new_x = np.array(plot.xData)
            new_y = np.array(plot.yData)
            new_plot.add_scatter_plot(x = new_x, y = new_y, id = id, add_to_legend = False)  # Add to legend later if needed
    
        return new_plot


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

