from PySide6.QtWidgets import QWidget, QLabel, QSplitter
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.plots.loss_evolution_plot import loss_evolution_plot
from aivalanche_app.components.custom_table import custom_table
from aivalanche_app.components.results_text_info import results_text_info
from aivalanche_app.components.plots.heatmap_plot import heatmap_plot
from aivalanche_app.components.buttons.icon_button import icon_button
from aivalanche_app.components.custom_scroll_area import custom_scroll_area
from aivalanche_app.components.plots.plot_placeholder import plot_placeholder
from aivalanche_app.paths import refresh_icon_path, refresh_hovered_icon_path, refresh_pressed_icon_path
import pyqtgraph as pg, numpy as np

class results_progress_tab(QSplitter):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(orientation = Qt.Vertical, parent = parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.store.calibration_start.connect(self.on_calibration_start)
        self.store.calibration_progress.connect(self.on_calibration_progress)
        self.store.active_model_change_start.connect(self.on_acive_model_change)
        self.style = self.store.style
        
        self.pe_scroll_area_width = 0
        self.minimum_pe_plot_width = 40
        
        self.init_ui()
    
    def init_ui(self):
        # top splitter
        top_splitter = QSplitter(parent = self)
        
        # left widget of the top splitter
        left_widget = QWidget(parent = top_splitter)
        left_layout = v_layout(spacing = 5)
        left_widget.setLayout(left_layout)
        
        # Create the loss evolution update button
        self.loss_evol_update_button = icon_button(parent = self,
                                         icon_path = refresh_icon_path,
                                         icon_hover_path = refresh_hovered_icon_path,
                                         icon_press_path = refresh_pressed_icon_path,
                                         object_name = 'refresh',
                                         enabled = False,
                                         on_click = self.on_loss_evol_update_button_press)
        left_layout.addWidget(self.loss_evol_update_button, alignment = Qt.AlignmentFlag.AlignRight)

        # loss evolution  
        loss_evolution_widget = pg.GraphicsLayoutWidget(parent = top_splitter)
        self.le_plot = loss_evolution_plot(x_axis_label = 'Iteration', y_axis_label = 'Loss', style = self.style)
        self.le_plot .setMinimumHeight(200)
        loss_evolution_widget.addItem(self.le_plot , row = 0, col = 0)
        left_layout.addWidget(loss_evolution_widget)
        
        # evolution info
        info_widget = QWidget(parent = top_splitter)
        info_widget.setContentsMargins(20, 35, 0, 0)
        info_layout = v_layout(spacing = 5, alignment = Qt.AlignmentFlag.AlignTop)
        info_widget.setLayout(info_layout)
        
        # max nr of iterations
        self.max_nr_iteration_widget = results_text_info(parent = self,  label = 'Max. number of iterations:', value = '')
        info_layout.addWidget(self.max_nr_iteration_widget)
        
        # current iteration
        self.current_iteration_widget = results_text_info(parent = self,  label = 'Current iteration:', value = '')
        info_layout.addWidget(self.current_iteration_widget)
        
        # current best loss
        self.current_best_loss_widget = results_text_info(parent = self,  label = 'Current best loss:', value = '')
        info_layout.addWidget(self.current_best_loss_widget)
        
        # time elapsed
        self.time_elapsed_widget = results_text_info(parent = self,  label = 'Time elapsed:', value = '')
        info_layout.addWidget(self.time_elapsed_widget)
        
        # time remaining
        self.time_remaining_widget = results_text_info(parent = self,  label = 'Time remaining:', value = '')
        info_layout.addWidget(self.time_remaining_widget)
        
        top_splitter.setStretchFactor(0, 5)
        top_splitter.setStretchFactor(1, 1)
        
        # parameter evolution
        param_evol_widget = QWidget(parent = self)
        param_evol_widget.setContentsMargins(0, 0, 0, 0)
        param_evol_layout = v_layout(spacing = 5)
        param_evol_widget.setLayout(param_evol_layout)
        
        param_evol_top_layout = h_layout(spacing = 5, alignment = Qt.AlignmentFlag.AlignRight)
        param_evol_layout.addLayout(param_evol_top_layout)
        
        parameter_evolution_title = QLabel(parent = param_evol_widget, text = 'parameter evolution')
        param_evol_top_layout.addWidget(parameter_evolution_title)
        
        # Create the param evolution update button
        self.param_evol_update_button = icon_button(parent = self,
                                         icon_path = refresh_icon_path,
                                         icon_hover_path = refresh_hovered_icon_path,
                                         icon_press_path = refresh_pressed_icon_path,
                                         object_name = 'refresh',
                                         enabled = False,
                                         on_click = self.on_param_evol_update_button_press)
        param_evol_top_layout.addWidget(self.param_evol_update_button, alignment = Qt.AlignmentFlag.AlignRight)
        
        # Create a scroll area
        self.scroll_area = custom_scroll_area(parent = self, on_resize_event = self.on_scroll_area_resize_event)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        param_evol_layout.addWidget(self.scroll_area)
        
        self.pe_placeholder = plot_placeholder(parent = self)
        
        self.pe_widget = pg.GraphicsLayoutWidget()
        self.pe_widget.ci.setSpacing(0)
        self.pe_widget.ci.setContentsMargins(0, 0, 0, 0)
        
        self.set_pe_widget()
        
        self.setStretchFactor(0, 5)
        self.setStretchFactor(1, 1)
    
    def on_calibration_start(self, data: dict = None):
        if data is not None and isinstance(data, dict):
            self.max_nr_iteration_widget.update_value(data['max_iterations'])
    
    def on_calibration_progress(self, data: dict = None):
        if data is not None and isinstance(data, dict):
            if data['model_id'] == self.store.active_model['id']:
                if data['iteration'] == 1 or self.le_plot.data is None:
                    self.update_loss_evolution_plot()
                    self.set_pe_widget(data = data)
                else:
                    self.loss_evol_update_button.set_enabled(True)
                    self.param_evol_update_button.set_enabled(True)
            self.update_status(iteration = data['iteration'], best_loss = data['best_loss'])
            
    def update_status(self, iteration = '', best_loss = ''):
        self.current_iteration_widget.update_value(iteration)
        self.current_best_loss_widget.update_value(best_loss)        
            
    def update_loss_evolution_plot(self):
        loss_evolution_data = np.array(self.store.calibration_results_survivors[['iter', 'survivor_metric']]).astype(float)
        self.le_plot.update_data(loss_evolution_data)
            
    def on_loss_evol_update_button_press(self):
        self.update_loss_evolution_plot()
        self.loss_evol_update_button.set_enabled(False)
        
    def on_param_evol_update_button_press(self):
        self.update_parameter_histograms()
        self.param_evol_update_button.set_enabled(False)
        
    def on_acive_model_change(self):
        self.le_plot.clear_plot()
        
    def set_pe_widget(self, data = None):
        if data is None:
            self.scroll_area.setWidget(self.pe_placeholder)
        else:
            self.scroll_area.setWidget(self.pe_widget)
            self.update_parameter_histograms()
        self.update()
    
    def update_parameter_histograms(self):
        self.pe_widget.ci.clear()
        trials = self.store.calibration_results_trials
        columns = list(trials.columns)
        nr_parameters = len(columns)
        self.update_pe_width(nr_plots = nr_parameters)
        for i, col in enumerate(columns):
            data = np.array(trials[col])
            parameter_heatmap = heatmap_plot(data = data, style = self.style, x_axis_label = col)
            parameter_heatmap.setMinimumWidth(self.minimum_pe_plot_width)
            self.pe_widget.addItem(parameter_heatmap, 0, i)
    
    def on_scroll_area_resize_event(self, event):  
        self.pe_scroll_area_width = event.size().width()
        
    def update_pe_width(self, nr_plots = 10):
        min_plots_width = self.minimum_pe_plot_width * nr_plots
        self.pe_widget.setFixedWidth(max(self.pe_scroll_area_width, min_plots_width))
        