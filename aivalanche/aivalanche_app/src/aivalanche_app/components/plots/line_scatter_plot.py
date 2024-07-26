from PySide6.QtWidgets import QMenu
from aivalanche_app.paths import home_icon_path, log_x_icon_path, log_y_icon_path, lin_x_icon_path, lin_y_icon_path
from aivalanche_app.components.plots.plot_button import plot_button
from pyqtgraph import LegendItem, ItemSample, PlotDataItem, PlotItem, ViewBox
from PySide6.QtCore import Signal, Qt
import numpy as np

# Custom legend item to emit events when clicked.
class custom_legend_item(ItemSample):
    item_clicked = Signal(object)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mouseClickEvent(self, event):
        super().mouseClickEvent(event)
        self.item_clicked.emit(self.item)

# Custom legend to enable the coupled behavior of line and scatter plots.
class custom_legend(LegendItem):
    def __init__(self, *args, on_item_click: callable = None, **kwargs):
        self.on_item_click = on_item_click
        super().__init__(*args, **kwargs)

    def addItem(self, item, name):
        super().addItem(item, name)
        if self.on_item_click is not None and issubclass(self.sampleType, custom_legend_item):
            self.items[-1][0].item_clicked.connect(self.on_item_click)

# Custom plot data item to give an id to each item.
class custom_plot_data_item(PlotDataItem):
    def __init__(self, *args, id: str = None, **kwargs):
        self.id = id
        super().__init__(*args, **kwargs)

# Custom class to zoom in and out only when ctrl key is pressed.
class custom_viewbox(ViewBox):
    def wheelEvent(self, ev, axis = None):
        if ev.modifiers() == Qt.ControlModifier:
            super().wheelEvent(ev)
        else:
            ev.ignore()
            
class line_scatter_plot(PlotItem):
    def __init__(self, parent = None, title = 'title', x_axis_label = 'x axis', y_axis_label = 'y axis', show_legend: bool = True,
                 use_custom_legend: bool = False, on_legend_item_click: callable = None, style = None):

        custom_vb = custom_viewbox()
        super().__init__(parent = parent, title = title, viewBox = custom_vb)     
        
        self.show_legend = show_legend
        self.use_custom_legend = use_custom_legend
        self.on_legend_item_click = on_legend_item_click
        self.style = style        
        self.plot_colors = style.colors['plot_colors']
        self._plots = {}
        self._legend = None
        self.clear_plot()
        self.total_nr_plots = 0
                     
        self.showGrid(x = True, y = True, alpha = 0.5)
        
        self.set_title(title)
        self.add_x_axis_label(x_axis_label)
        self.add_y_axis_label(y_axis_label)
        
        self.x_axis = self.getAxis('bottom')
        self.x_axis.setPen(self.style.colors['plot_axis'])
        self.x_axis.setTextPen(self.style.colors['plot_text'])
        self.x_axis.setTickPen(self.style.colors['plot_grid'])
        
        self.y_axis = self.getAxis('left')
        self.y_axis.setPen(self.style.colors['plot_axis'])
        self.y_axis.setTextPen(self.style.colors['plot_text'])
        self.y_axis.setTickPen(self.style.colors['plot_grid'])
        
        self.hideButtons()
        
        # # Add plot buttons     
        # buttons_height = 20
        
        # self.scale_y_button = plot_button(image_file_1 = log_y_icon_path, image_file_2 = lin_y_icon_path, height = buttons_height, parent_item = self)
        # self.scale_y_button.clicked.connect(self.toggle_y_scale)    
        
        # self.scale_x_button = plot_button(image_file_1 = log_x_icon_path, image_file_2 = lin_x_icon_path, height = buttons_height, parent_item = self)
        # self.scale_x_button.clicked.connect(self.toggle_x_scale)   

    @property
    def nr_curves(self):
        return len(self.plots.keys())
    
    @property
    def plots(self):
        return self._plots

    @plots.setter
    def plots(self, value):
        self._plots = value
        self.update_legend_visibility()
        
    def clear_plot(self):
        self.clearPlots()
        self.plots = {}
    
    def addLegend(self, offset=(30, 30), **kwargs):
        if self.legend is None:
            self.legend = custom_legend(offset = offset, **kwargs)
            self.legend.setParentItem(self.vb)
        return self.legend
    
    def update_legend_visibility(self):
        if self.show_legend:
            if self.plots and not self._legend:
                if self.use_custom_legend:
                    self._legend = self.addLegend(on_item_click = self._on_legend_item_click,
                                                  sampleType = custom_legend_item,
                                                  brush = self.style.colors['plot_legend_background'],
                                                  labelTextColor = self.style.colors['plot_legend_text'])
                else:
                    self._legend = self.addLegend(brush = self.style.colors['plot_legend_background'],
                                                  labelTextColor = self.style.colors['plot_legend_text'])
            elif not self.plots and self._legend:
                self.removeItem(self._legend)
                self._legend = None
    
    def _on_legend_item_click(self, item):
        if self.on_legend_item_click is not None:
            self.on_legend_item_click(item)
        
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
        temp = custom_plot_data_item(x, y, pen = None, id = id, **kwargs)
        self.add_item(temp, id, add_to_legend, label)
        
    def add_line_plot(self, x = None, y = None, id = None, add_to_legend = True, label = None, symbol = None, line_width = 1, **kwargs):
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
        if 'pen' not in kwargs.keys():
            index = self.total_nr_plots % len(self.plot_colors)
            color = self.plot_colors[index]
            kwargs['pen'] = {'color': color, 'width': line_width}
    
        # Create a PlotDataItem for scatter plot and add it to the PlotItem
        temp = custom_plot_data_item(x, y, symbol = symbol, id = id, **kwargs)
        self.add_item(temp, id, add_to_legend, label)

    def add_item(self, item, id = None, add_to_legend = True, label = None):
        self.addItem(item)
        self.total_nr_plots += 1
        
        if id is not None:
            new_plots = self.plots.copy()
            new_plots[id] = item
            self.plots = new_plots  # This will trigger the setter
    
            if add_to_legend and self._legend:
                self._legend.addItem(item, label)
    
    def remove_curve(self, id = None):
        if id is None or id not in self.plots.keys():
            return
        self.removeItem(self.plots[id])
        new_plots = self.plots.copy()
        del new_plots[id]
        self.plots = new_plots  # This will trigger the setter
        
    def set_curve_visibility(self, id = None, visible = True):
        if id is None:
            return
        self.plots[id].setVisible(visible)
    
    # def deep_copy(self):
    #     new_plot = line_scatter_plot(title = self.titleLabel.text, x_axis_label = self.getAxis('bottom').label.text,
    #                                  y_axis_label = self.getAxis('left').label.text, style = self.style)
        
    #     # Copy other relevant attributes or properties
    #     new_plot.plot_colors = self.plot_colors
    #     # ... (copy other attributes as needed)
    
    #     # Copy each scatter plot individually
    #     for id, plot in self.plots.items():
    #         new_x = np.array(plot.xData)
    #         new_y = np.array(plot.yData)
    #         new_plot.add_scatter_plot(x = new_x, y = new_y, id = id, add_to_legend = False)  # Add to legend later if needed
    
    #     return new_plot

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