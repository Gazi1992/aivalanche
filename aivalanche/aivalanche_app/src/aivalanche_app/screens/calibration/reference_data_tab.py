from PySide6.QtWidgets import QWidget, QSplitter, QScrollArea
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.plots.line_scatter_plot import line_scatter_plot
from aivalanche_app.components.combo_box_load_data import combo_box_load_data
from aivalanche_app.components.custom_table import custom_table
from reference_data import Reference_data
import pyqtgraph as pg, pandas as pd, os

class reference_data_tab(QSplitter):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        self.object_name = object_name
        if object_name is not None:
            self.setObjectName(object_name)
            
        self.store = store
        self.style = self.store.style
        
        self.reference_data_file = None
        self.reference_data = None
        
        self.plots = []
        self.min_plot_height = 500
        self.plots_widget_height_array = []
        
        self.placeholder_plot = line_scatter_plot(x_axis_label = 'x', y_axis_label = 'y', style = self.style)
        self.placeholder_plot_visible = False
        
        self.init_ui()
    
    
    @property
    def nr_plots(self):
        return len(self.plots)
    

    def init_ui(self):
        # Create left widget
        left_widget = QWidget(parent = self)
        left_layout = v_layout(spacing = 20)
        left_widget.setLayout(left_layout)
        
        # Create load data combo box
        self.load_data_widget = combo_box_load_data(parent = self,
                                                    caption = 'Select reference data file',
                                                    filter = 'Json file (*.json)',
                                                    on_combo_box_changed = self.load_reference_data,
                                                    placeholder = 'Select reference data file',
                                                    object_name = 'round_combo_box')       
        left_layout.addWidget(self.load_data_widget, 0)
        
        # Create table
        self.table = custom_table(store = self.store,
                                  on_checkbox_click = self.on_checkbox_click)
        left_layout.addWidget(self.table, 1)
        
        # Create right layout, where plots will be shown
        right_widget = QWidget(parent = self)
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
        
        self.check_empty_plot_widget()
            
    
    def check_empty_plot_widget(self):
        if self.nr_plots == 0:
            self.show_placeholder_plot()
            

    def show_placeholder_plot(self):
        self.plots_widget.addItem(self.placeholder_plot, row = 0, col = 0)
        self.placeholder_plot_visible = True
        if len(self.plots_widget_height_array) > 0:
            self.plots_widget.setFixedHeight(self.plots_widget_height_array[0])


    def load_reference_data(self, file):
        if os.path.exists(file):
            self.clear_all_plots()
            self.reference_data = Reference_data(file)
            min_group_id = self.reference_data.data['group_id'].min()
            self.reference_data.data.insert(0, 'include', True)
            self.reference_data.data.insert(1, 'plot', False)
            self.reference_data.data.insert(2, 'calibrate', True)
            self.reference_data.data['plot'] = self.reference_data.data['group_id'] == min_group_id
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
            self.update_plots(group_id, curve_id, state)

    
    def update_plots(self, group_id = None, curve_id = None, state = None):
        if group_id in self.plots:
            if not state:
                plot_item = self.get_plot_from_group_id(group_id)
                if plot_item.nr_curves == 1:
                    self.remove_plot(group_id)
                else:
                    plot = self.get_plot_from_group_id(group_id)
                    self.remove_curve_from_plot(plot, curve_id)
            else:
                data = self.reference_data.data[(self.reference_data.data['group_id'] == group_id) & (self.reference_data.data['curve_id'] == curve_id)]
                plot = self.get_plot_from_group_id(group_id)
                self.add_curve_to_plot(plot, data.squeeze())
        else:
            self.add_plot(group_id)
            
            
    def clear_all_plots(self):
        self.plots_widget.ci.clear()
        self.plots = []
        self.placeholder_plot_visible = False
        
            
    def add_plot(self, group_id = None):
        
        if self.placeholder_plot_visible:
            self.clear_all_plots()
        
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
        custom_plot.setMinimumHeight(self.min_plot_height)
        
        # add all the curves to the plot
        filtered_data.apply(lambda row: self.add_curve_to_plot(custom_plot, row), axis = 1)

        # add the new plot to the plot_widget
        index = self.nr_plots
        row, col = self.get_plot_row_col_from_index(index)
        self.plots_widget.addItem(custom_plot, row = row, col = col)
        
        # add to self.plots
        self.plots.append(group_id)

        # update plots_widget heights
        if self.nr_plots > len(self.plots_widget_height_array):
            self.plots_widget_height_array.append(self.plots_widget.ci.height())

        self.plots_widget.setFixedHeight(self.plots_widget_height_array[self.nr_plots - 1])
            
        # update the table plot checkboxes
        self.reference_data.update_by_condition(condition = f'group_id == {group_id}', update_columns = ['plot'], update_values = [True])
        self.table.update_by_condition(condition = f'group_id == {group_id}', update_columns = ['plot'], update_values = [True])
        
        # self.plots_widget.ci.setBorder(color = 'r')
        # self.plots_widget.ci.height()
        # self.plots_widget.ci.setSpacing(10)
        # self.plots_widget.setMinimumHeight(self.plots_widget.sizeHint().height())
        # self.plots_widget.getItem(0, 0).height()
        # self.plots_widget.height()
           
    
    def add_curve_to_plot(self, plot, data):
        if 'extra_var_name' in data and not pd.isna(data['extra_var_name']):
            label = f"{data['extra_var_name']} = {data['extra_var_value']}"
        else:
            label = f"{data['curve_id']}"
                
        plot.add_scatter_plot(x = data['x_values'], y = data['y_values'], id = data['curve_id'], label = label, symbol = 'o', symbolPen = None)
        
    
    def remove_curve_from_plot(self, plot, curve_id):
        plot.remove_curve(id = curve_id)
        
    
    def remove_plot(self, group_id = None):
        if group_id in self.plots:
            index = self.get_plot_index_from_group_id(group_id)
            if index == self.nr_plots - 1:
                self.plots_widget.removeItem(self.get_plot_from_group_id(group_id))
                del self.plots[index]
            else:
                self.shift_plots_left(start_index = index + 1)
                
            self.plots_widget.setFixedHeight(self.plots_widget_height_array[self.nr_plots - 1])
    
            self.check_empty_plot_widget()

        
    def shift_plots_left(self, start_index = -1):
        if start_index > 0:
            index = start_index
            
            # remove first the plot which is to be deleted from the layout
            plot_to_remove = self.get_plot_from_index(index - 1)
            self.plots_widget.removeItem(plot_to_remove) 
            
            # shift left all the following plots
            while index < self.nr_plots:
                
                new_row, new_col = self.get_plot_row_col_from_index(index - 1) # row and col of the element to the left
                new_plot = self.get_plot_from_index(index)
                
                self.plots_widget.removeItem(new_plot) # remove first the item on the left
                self.plots_widget.addItem(new_plot, new_row, new_col) # duplicate the current item by adding it to the left, which will be also overwriten by the next loop iteration

                self.plots[index - 1] = self.plots[index] # update the self.plots
                    
                index += 1 # increment the index
            
            # delete the last element of the plots, since it is duplicated to the left
            del self.plots[-1]
                       
    
    def get_plot_from_index(self, index = -1):
        if index >= 0:
            return self.get_plot_from_group_id(self.plots[index])
    
    
    def get_plot_from_group_id(self, group_id = None):
        if group_id in self.plots:
            index = self.get_plot_index_from_group_id(group_id)
            row, col = self.get_plot_row_col_from_index(index)
            return self.plots_widget.getItem(row, col)
        
        
    def get_plot_index_from_group_id(self, group_id = None):
        if group_id in self.plots:
            return self.plots.index(group_id)
        return -1
        
    
    def get_plot_row_col_from_index(self, index):
        row = index // 2
        col = index % 2
        return row, col
    
    

            