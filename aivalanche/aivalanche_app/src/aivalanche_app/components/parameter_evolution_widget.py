from PySide6.QtWidgets import QScrollArea
from aivalanche_app.components.plots.heatmap_plot import heatmap_plot
import pandas as pd, pyqtgraph as pg, numpy as np

class parameter_evolution_widget(QScrollArea):
    def __init__(self, parent = None, style = None, data: pd.DataFrame = None):
        super().__init__(parent = parent)
        self.style = style
        self._data = None
        self.init_ui()
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        
    def init_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setWidgetResizable(True)

        self.plots_widget = pg.GraphicsLayoutWidget()
        self.update_plots()
    
    def update_plots(self):
        data = np.random.random((1, 100))
        for i in range(10):
            parameter_heatmap = heatmap_plot(data = data, style = self.style)
            parameter_heatmap.setMinimumWidth(200)
            self.plots_widget.addItem(parameter_heatmap, i, 0)
    
        
        
        
        
        
        
        
        

        
        
        

            
        