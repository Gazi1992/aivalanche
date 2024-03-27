from PySide6.QtWidgets import QWidget, QLabel, QSplitter
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.plots.line_scatter_plot import line_scatter_plot
from aivalanche_app.components.custom_table import custom_table
from aivalanche_app.components.results_text_info import results_text_info
from aivalanche_app.components.plots.heatmap_plot import heatmap_plot
import pyqtgraph as pg, numpy as np

class results_progress_tab(QSplitter):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(orientation = Qt.Vertical, parent = parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.style = self.store.style
        
        self.init_ui()
        
    
    def init_ui(self):
        # top splitter
        top_splitter = QSplitter(parent = self)

        # loss evolution  
        loss_evolution_widget = pg.GraphicsLayoutWidget(parent = top_splitter)
        loss_evolution_plot = line_scatter_plot(title = 'Loss evolution', x_axis_label = 'Iteration', y_axis_label = 'Loss', style = self.style)
        loss_evolution_plot.setMinimumHeight(200)
        loss_evolution_widget.addItem(loss_evolution_plot, row = 0, col = 0)
        
        # evolution info
        info_widget = QWidget(parent = top_splitter)
        info_widget.setContentsMargins(20, 35, 0, 0)
        info_layout = v_layout(spacing = 5, alignment = Qt.AlignmentFlag.AlignTop)
        info_widget.setLayout(info_layout)
        
        # max nr of iterations
        max_nr_iteration_widget = results_text_info(parent = self,  label = 'Max. number of iterations:', value = 1000)
        info_layout.addWidget(max_nr_iteration_widget)
        
        # current iteration
        current_iteration_widget = results_text_info(parent = self,  label = 'Current iteration:', value = 175)
        info_layout.addWidget(current_iteration_widget)
        
        # current best loss
        current_best_loss_widget = results_text_info(parent = self,  label = 'Current best loss:', value = 1e-5)
        info_layout.addWidget(current_best_loss_widget)
        
        # time elapsed
        time_elapsed_widget = results_text_info(parent = self,  label = 'Time elapsed:', value = '1h : 5min : 34s')
        info_layout.addWidget(time_elapsed_widget)
        
        # time remaining
        time_remaining_widget = results_text_info(parent = self,  label = 'Time remaining:', value = '3h : 24min : 16s')
        info_layout.addWidget(time_remaining_widget)
        
        top_splitter.setStretchFactor(0, 5)
        top_splitter.setStretchFactor(1, 1)
        
        # parameter evolution
        parameter_evolution_widget = QWidget(parent = self)
        parameter_evolution_layout = v_layout(spacing = 5)
        parameter_evolution_widget.setLayout(parameter_evolution_layout)
        
        parameter_evolution_title = QLabel(parent = parameter_evolution_widget, text = 'parameter evolution')
        parameter_evolution_layout.addWidget(parameter_evolution_title)
        
        # add parameter heeatmaps
        data = np.random.random((1, 100))
        p_widget = pg.GraphicsLayoutWidget()
        parameter_heatmap = heatmap_plot(data = data, style = self.style)
        p_widget.addItem(parameter_heatmap, 0, 0)
        parameter_evolution_layout.addWidget(p_widget)
        
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 1)
    
    def on_checkbox_click(self, data: dict = None):
        row = data['row_index']
        column = data['column_index']
        column_name = data['column_name']
        state = data['state']
        self.reference_data.data.iloc[row, column] = state
        if column_name == 'plot':
            group_id = self.reference_data.data.iloc[row]['group_id']
            curve_id = self.reference_data.data.iloc[row]['curve_id']
            self.update_plots(group_id, curve_id, state)