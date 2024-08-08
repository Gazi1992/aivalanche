from PySide6.QtWidgets import QWidget, QSplitter
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.plots.line_scatter_plot import line_scatter_plot
from aivalanche_app.components.custom_table import custom_table
from aivalanche_app.components.custom_scroll_area import custom_scroll_area
from aivalanche_app.components.buttons.icon_button import icon_button
from aivalanche_app.components.plots.custom_graphics_layout_widget import custom_graphics_layout_widget
from aivalanche_app.helper_functions import update_df_by_condition
from aivalanche_app.paths import refresh_icon_path, refresh_hovered_icon_path, refresh_pressed_icon_path
import pandas as pd, math, numpy as np

class results_data_tab(QSplitter):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        self.object_name = object_name
        if object_name is not None:
            self.setObjectName(object_name)
            
        self.store = store
        self.store.single_simulation_end.connect(self.on_single_simulation_finished)
        self.store.fetch_model_results_end.connect(self.on_model_results_fetched)
        self.store.calibration_progress.connect(self.on_calibration_progress)
        self.store.calibration_start.connect(self.on_calibration_start)
        self.store.overwrite_calibration_results_end.connect(self.on_calibration_results_overwrite)
        self.store.active_model_change_start.connect(self.on_acive_model_change)
        
        self.style = self.store.style
                
        self.plots = []
        self.min_plot_height = 500
        self.plot_spacing = 20
        self.plots_widget_height_array = []
        self.plots_scroll_area_height = 0
        
        self.placeholder_plot = line_scatter_plot(x_axis_label = 'x', y_axis_label = 'y', style = self.style)
        self.placeholder_plot_visible = False
        
        self._data = None
        
        self.init_ui()
   
    @property
    def nr_plots(self):
        return len(self.plots)
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value
        self.load_data()
    
    def init_ui(self):
        # Create left widget
        left_widget = QWidget(parent = self)
        left_layout = v_layout(spacing = 5)
        left_widget.setLayout(left_layout)
        
        # Create the update button
        self.update_button = icon_button(parent = self,
                                         icon_path = refresh_icon_path,
                                         icon_hover_path = refresh_hovered_icon_path,
                                         icon_press_path = refresh_pressed_icon_path,
                                         object_name = 'refresh',
                                         on_click = self.on_update_button_press)
        left_layout.addWidget(self.update_button, alignment = Qt.AlignmentFlag.AlignRight)
        
        # Create table
        self.table = custom_table(store = self.store, on_change = self.on_table_change)
        left_layout.addWidget(self.table, 1)
        
        # Create right layout, where plots will be shown
        right_widget = QWidget(parent = self)
        right_widget.setContentsMargins(10, 0, 0, 0)
        right_layout = v_layout(spacing = 20)
        right_widget.setLayout(right_layout)
        
        # Create a scroll area
        scroll_area = custom_scroll_area(parent = self, on_resize_event = self.on_scroll_area_resize_event)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(scroll_area)
        
        # Create a grid layout for plots
        self.plots_widget = custom_graphics_layout_widget()
        self.plots_widget.ci.setSpacing(self.plot_spacing)
        
        scroll_area.setWidget(self.plots_widget)
    
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 1)
        
        self.check_empty_plot_widget()
    
    def on_table_change(self, data: dict = None):
        if data['type'] == 'checkbox_click':
            self.on_checkbox_click(data)
        else:
            print(data)

    def on_checkbox_click(self, data: dict = None):
        row = data['row_index']
        column = data['column_index']
        column_name = data['column_name']
        state = data['state']
        self._data.iloc[row, column] = state
        if column_name == 'plot':
            group_id = self._data.iloc[row]['group_id']
            curve_id = self._data.iloc[row]['curve_id']
            self.update_plots(group_id, curve_id, state)
    
    def on_acive_model_change(self):
        self.clear_data()
    
    def on_scroll_area_resize_event(self, event):  
        self.plots_scroll_area_height = event.size().height()
        self.update_plots_widget_height()              
        
    def on_update_button_press(self, text):
        self.store.overwrite_calibration_results(model_id = self.store.active_model['id'])        
                
    def update_plots_widget_height(self):
        min_plots_height = (self.min_plot_height + self.plot_spacing) * math.ceil(self.nr_plots / 2) 
        self.plots_widget.setFixedHeight(max(self.plots_scroll_area_height, min_plots_height))
    
    def clear_data(self):
        self._data = None
        self.clear_all_plots()
        self.table.clear_data()
        self.check_empty_plot_widget()
    
    def load_data(self):
        if self._data is not None and not self._data.empty:
            self.clear_all_plots()
            if 'plot' not in self._data.columns:
                self._data.insert(0, 'plot', False)
            self.table.update_data(self._data)
            if not np.any(self._data['plot']): # if plots were previously visible
                min_group_id = self._data['group_id'].min()
                self._data['plot'] = self._data['group_id'] == min_group_id
                self.update_plots(group_id = min_group_id)
            else:
                group_ids = self._data.loc[self._data['plot'], 'group_id'].unique()
                for id in group_ids:
                    self.update_plots(group_id = id)
    
    def on_model_results_fetched(self):
        if self.store.calibration_results is not None:
            self.data = self.store.calibration_results
        elif self.store.single_simulation_results is not None:
            self.data = self.store.single_simulation_results
        else:
            self.clear_data()
            
    def on_calibration_progress(self, data):
        if data['model_id'] == self.store.active_model['id']:
            if data['iteration'] == 1 or self._data is None:
                self.data = self.store.calibration_results
            elif data['better_solution_found']:
                self.update_button.set_enabled(True)
                
    def on_calibration_start(self):
        self._data = None
                
    def on_single_simulation_finished(self, data):
        if data['model_id'] == self.store.active_model['id']:
            self.data = self.store.single_simulation_results
            
    def on_calibration_results_overwrite(self, data):
        if data['model_id'] == self.store.active_model['id']:
            self.data = self.store.calibration_results
            
    def check_empty_plot_widget(self):
        if self.nr_plots == 0:
            self.show_placeholder_plot()

    def show_placeholder_plot(self):
        self.plots_widget.addItem(self.placeholder_plot, row = 0, col = 0)
        self.placeholder_plot_visible = True
        self.update_plots_widget_height() # update plots_widget heights
    
    def update_plots(self, group_id = None, curve_id = None, state = None):
        if group_id in self.plots:
            if not state:
                plot_item = self.get_plot_from_group_id(group_id)
                if plot_item.nr_curves == 2:
                    self.remove_plot(group_id)
                else:
                    plot = self.get_plot_from_group_id(group_id)
                    self.remove_curve_from_plot(plot, group_id, curve_id)
            else:
                data = self._data[(self._data['group_id'] == group_id) & (self._data['curve_id'] == curve_id)]
                plot = self.get_plot_from_group_id(group_id)
                self.add_curve_to_plot(plot, data.squeeze())
        else:
            self.add_plot(group_id)
            
    def clear_all_plots(self):
        self.plots_widget.ci.clear()
        self.plots = []
        self.placeholder_plot_visible = False
        self.update_button.set_enabled(False)
    
    def add_plot(self, group_id = None):
        if self.placeholder_plot_visible:
            self.clear_all_plots()
    
        if group_id is None:
            return
    
        # get the group
        filtered_data = self._data[self._data['group_id'] == group_id]
        if len(filtered_data.index) == 0:
            return
        
        # filtered_data.reset_index(drop = True, inplace = True)
        
        # create the new plot
        group_name = filtered_data.iloc[0]['group_name']
        title = f"{group_name} - {group_id}"
        x_axis_label = filtered_data.iloc[0]['x_name']
        y_axis_label = filtered_data.iloc[0]['y_name']
        custom_plot =  line_scatter_plot(title = title, x_axis_label = x_axis_label, y_axis_label = y_axis_label,
                                         style = self.style, use_custom_legend = True, on_legend_item_click = self.on_legend_item_click)
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
        self.update_plots_widget_height()
            
        # update the table plot checkboxes
        update_df_by_condition(df = self._data, condition = f'group_id == {group_id}', update_columns = ['plot'], update_values = [True])
        self.table.update_by_condition(condition = f'group_id == {group_id}', update_columns = ['plot'], update_values = [True])

    def on_legend_item_click(self, item):
        temp = item.id.split('_')
        group_id = int(temp[0])
        curve_id = temp[1]
        curve_type = temp[2]
        if curve_type == 'line':
            scatter_plot_id = f'{group_id}_{curve_id}_scatter'
            plot_item = self.get_plot_from_group_id(group_id)
            plot_item.set_curve_visibility(scatter_plot_id, item.isVisible())
    
    def add_curve_to_plot(self, plot, data):
        if 'extra_var_name' in data and not pd.isna(data['extra_var_name']):
            label = f"{data['extra_var_name']} = {data['extra_var_value']}"
        else:
            label = f"{data['curve_id']}"
        plot.add_line_plot(x = data['x_values_simulation'], y = data['y_values_simulation'], id = f"{data['group_id']}_{data['curve_id']}_line", label = label, line_width = 2)
        plot.add_scatter_plot(x = data['x_values'], y = data['y_values'], id = f"{data['group_id']}_{data['curve_id']}_scatter", add_to_legend = False, symbol = 'o', symbolPen = 'black', symbolBrush = None)
        
    def remove_curve_from_plot(self, plot, group_id, curve_id):
        plot.remove_curve(id = f'{group_id}_{curve_id}_line')
        plot.remove_curve(id = f'{group_id}_{curve_id}_scatter')
        
    def remove_plot(self, group_id = None):
        if group_id in self.plots:
            index = self.get_plot_index_from_group_id(group_id)
            if index == self.nr_plots - 1:
                self.plots_widget.removeItem(self.get_plot_from_group_id(group_id))
                del self.plots[index]
            else:
                self.shift_plots_left(start_index = index + 1)
                
            # update plots_widget heights
            self.update_plots_widget_height()   
    
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