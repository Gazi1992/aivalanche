import pyqtgraph as pg, numpy as np, pandas as pd, math
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QTableWidget, QSplitter, QFileDialog, QScrollArea
from aivalanche_app.components.custom_layouts import h_layout, v_layout
from aivalanche_app.components.custom_checkbox import custom_checkbox
from aivalanche_app.data_store.store import store
from aivalanche_app.paths import upload_icon_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.components.plots.line_scatter_plot import line_scatter_plot
from aivalanche_app.resources.themes.style import style
from aivalanche_app.components.custom_table import custom_table
from reference_data import Reference_data

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', (0, 0, 0, 0))
pg.setConfigOption('foreground', 'k')

class reference_data_tab(QSplitter):
    
    def __init__(self, parent = None, store: store = None, style: style = None):
        super().__init__(parent)
        
        self.store = store
        self.style = style
        
        self.reference_data_file = None
        self.reference_data = None
        
        self.plots = {'group_ids': [], 'nr_plots': 0, 'min_plot_height': 500}        
        
        self.init_ui()
        
        
    def init_ui(self):
        
        # Set invisible splitter handle
        self.setHandleWidth(0)
        
        # Create left widget
        left_widget = QWidget(self)
        left_layout = v_layout(spacing = 20)
        left_widget.setLayout(left_layout)
        
        # Create load data layout
        load_data_layout = h_layout(spacing = 10)
        
        # Create drop-down widget
        self.drop_down_widget = QComboBox(parent = self)
        self.drop_down_widget.setFixedHeight(30)
        self.drop_down_widget.currentTextChanged.connect(lambda text: self.load_reference_data(text))
        load_data_layout.addWidget(self.drop_down_widget, 1)
        
        # Create load data button
        load_data_button = icon_text_button(parent = self, icon_path = upload_icon_path, icon_height = 25, on_click = self.on_load_data_button_click)
        load_data_layout.addWidget(load_data_button, 0)
        
        left_layout.addLayout(load_data_layout)
        
        # Create table
        self.table = custom_table(style = self.style,
                                  on_checkbox_click = self.on_checkbox_click)
        left_layout.addWidget(self.table)
        
        # Create right layout, where plots will be shown
        right_widget = QWidget(self)
        right_widget.setContentsMargins(10, 0, 0, 0)
        right_layout = v_layout(spacing = 20)
        right_widget.setLayout(right_layout)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(scroll_area)
        
        # Create a grid layout for plots
        self.plots_widget = pg.GraphicsLayoutWidget()
        self.plots_widget.ci.setSpacing(20)
        
        scroll_area.setWidget(self.plots_widget)
        scroll_area.setWidgetResizable(True)

        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 1)

        
    def on_load_data_button_click(self):
        response = QFileDialog.getOpenFileName(parent = self, caption = 'Select reference data file', filter = 'Json file (*.json)')
        if len(response[0]) > 0:
            ref_data_file = response[0]
            if ref_data_file != self.reference_data_file:
                self.drop_down_widget.addItem(ref_data_file)
                self.drop_down_widget.setCurrentText(ref_data_file)
            

    def load_reference_data(self, file):
        self.reference_data = Reference_data(file)
        min_group_id = self.reference_data.data['group_id'].min()
        self.reference_data.data.insert(0, 'include', True)
        self.reference_data.data['plot'] = self.reference_data.data['group_id'] == min_group_id
        self.reference_data.data['calibrate'] = True        
        self.table.update_data(self.reference_data.data)
        self.update_plots(group_id = min_group_id)
        
    
    def on_checkbox_click(self, data: dict = None):
        row = data['row_index']
        column = data['column_index']
        column_name = data['column_name']
        state = data['state']
        self.reference_data.data.iloc[row, column] = state
        if column_name == 'plot':
            group_id = self.reference_data.data.iloc[row]['group_id']
            curve_id = self.reference_data.data.iloc[row]['curve_id']
            self.update_plots(group_id, curve_id)

    
    def update_plots(self, group_id = None, curve_id = None):
    
        # filtered_data = self.reference_data.data[self.reference_data.data['group_id'] == group_id]
        if group_id in self.plots['group_ids']:
            print('kot')
        else:
            self.add_plot(group_id, curve_id)
                                
            
    def add_plot(self, group_id = None, curve_id = None):
        
        if group_id is None:
            return
        
        # get the group
        filtered_data = self.reference_data.data[self.reference_data.data['group_id'] == group_id]
        if len(filtered_data.index) == 0:
            return
        
        # filtered_data.reset_index(drop = True, inplace = True)
        
        # create the new plot
        group_name = filtered_data.iloc[0]['group_name']
        title = f"{group_name} - {group_id}"
        x_axis_label = filtered_data.iloc[0]['x_name']
        y_axis_label = filtered_data.iloc[0]['y_name']
        custom_plot =  line_scatter_plot(title = title, x_axis_label = x_axis_label, y_axis_label = y_axis_label, style = self.style)
        custom_plot.setMinimumHeight(self.plots['min_plot_height'])
        
        # add all the curves to the plot
        filtered_data.apply(lambda row: self.add_curve_to_given_plot(custom_plot, row), axis = 1)

        # add the new plot to the plot_widget
        row = self.plots['nr_plots'] / 2
        col = self.plots['nr_plots'] % 2
        self.plots_widget.addItem(custom_plot, row = row, col = col)
        
        # update self.plots
        self.plots['group_ids'].append(group_id)
        self.plots['nr_plots'] += 1

        # update the min height of the plots_widget
        if self.plots['nr_plots'] > 2:
            self.plots_widget.setFixedHeight(self.plots_widget.ci.height())
            
        # update the table plot checkboxes
        self.reference_data.update_by_condition(condition = f'group_id == {group_id}', update_columns = ['plot'], update_values = [True])
        self.table.update_by_condition(condition = f'group_id == {group_id}', update_columns = ['plot'], update_values = [True])
        # self.plots_widget.ci.setBorder(color = 'r')
        # self.plots_widget.ci.height()
        # self.plots_widget.ci.setSpacing(10)
        # self.plots_widget.setMinimumHeight(self.plots_widget.sizeHint().height())
        # self.plots_widget.getItem(0, 0).height()
        # self.plots_widget.height()
    
    def add_curve_to_given_plot(self, plot, data):
        if 'extra_var_name' in data and not pd.isna(data['extra_var_name']):
            id = f"{data['extra_var_name']} = {data['extra_var_value']}"
        else:
            id = f"{data['curve_id']}"
                
        plot.add_scatter_plot(x = data['x_values'], y = data['y_values'], id = id, symbol = 'o', symbolPen = None)