from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from aivalanche_app.components.custom_layouts import v_layout, h_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.combo_box_load_data import combo_box_load_data
from aivalanche_app.components.custom_table import custom_table
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from parameters.Parameters import Parameters
from aivalanche_app.helper_functions import find_max_suffix
import pandas as pd
from pathlib import Path

class parameters_tab(QWidget):
    parameters_warning = Signal(dict)
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)

        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.store.fetch_available_parameters_end.connect(self.on_available_parameters_fetched)
        self.store.add_available_parameters_end.connect(self.on_available_parameters_added)
        self.store.update_parameters_id_end.connect(self.on_parameters_id_updated)
        self.store.active_model_changed.connect(self.check_parameters_exists)
                
        self.init_ui()
        
    def init_ui(self):
        # main layout
        layout = v_layout(spacing = 30)
        self.setLayout(layout)

        # top layout
        top_layout = h_layout(spacing = 20)
        layout.addLayout(top_layout)
        
        # Create load data combo box
        self.load_data_widget = combo_box_load_data(parent = self,
                                                    caption = 'Select parameters file',
                                                    filter = 'CSV and Json files (*.csv *.json)',
                                                    placeholder = 'Select parameters file',
                                                    on_combo_box_changed = self.on_combo_box_changed,
                                                    on_import_new_file = self.on_import_new_ref_data_file,
                                                    object_name = 'round_combo_box',
                                                    is_editable = False)       
        top_layout.addWidget(self.load_data_widget, 0)
        top_layout.addSpacing(20)
        
        # Save parameter to file button
        save_button = icon_text_button(parent = self, text = 'Save parameters to file', padding = (10, 5, 10, 5),
                                       on_click = self.save_parameters_to_file, object_name = 'parameters_tab')
        top_layout.addWidget(save_button)
        
        # Save parameter to file button
        import_default_button = icon_text_button(parent = self, text = 'Import default values', padding = (10, 5, 10, 5),
                                                 on_click = self.import_default_values, object_name = 'parameters_tab')
        top_layout.addWidget(import_default_button)
        
        # Create table
        self.table = custom_table(store = self.store, column_width_mode = 'Stretch')
        layout.addWidget(self.table, 1)

    def clear_data(self):
        self.table.clear_data()
        self.load_data_widget.set_active_item(None)

    def load_parameters(self):
        if 'include' not in self.store.parameters.columns:
            self.store.parameters.all_parameters.insert(0, 'include', True)
        self.table.update_data(self.store.parameters.all_parameters)
    
    def on_combo_box_changed(self, val):
        if val is not None and len(val) > 0:
            parameters_id = self.store.available_parameters.loc[self.store.available_parameters['name'] == val,'id'].iloc[0]
            self.store.update_parameters_id(parameters_id = parameters_id, model_id = self.store.active_model['id'])
    
    def on_parameters_id_updated(self, data: dict = {}):
        if data['success']:
            if not pd.isnull(self.store.active_model['parameters_id']):
                parameters_path = self.store.available_parameters.loc[self.store.available_parameters['id'] == self.store.active_model['parameters_id'], 'path'] 
                if parameters_path.empty:
                    self.store.fetch_available_parameters(self.store.active_project['id'])
                else:
                    self.store.parameters = Parameters(parameters_path.iloc[0])
                    self.load_parameters()
        else:
            print(data['error'])
    
    def on_available_parameters_fetched(self, data: dict = {}):
        if data['success']:
            self.load_data_widget.update_items(self.store.available_parameters['name'].tolist())
            self.check_parameters_exists()
        
    def check_parameters_exists(self):
        self.clear_data()
        if self.store.active_model is not None:
            if not pd.isnull(self.store.active_model['parameters_id']):
                parameters_path = self.store.available_parameters.loc[self.store.available_parameters['id'] == self.store.active_model['parameters_id'], 'path']
                parameters_name = self.store.available_parameters.loc[self.store.available_parameters['id'] == self.store.active_model['parameters_id'], 'name']
                if parameters_path.empty:
                    self.store.update_parameters_id(parameters_id = None, model_id = self.store.active_model['id'])
                else:
                    self.store.parameters = Parameters(parameters_path.iloc[0])
                    self.load_data_widget.set_active_item(parameters_name.iloc[0], trigger_on_change_slot = False)
                    self.load_parameters()
    
    def on_import_new_ref_data_file(self, file_path: str = None):
        if file_path is not None:
            # Check if the file is readable
            try:
                file_valid = True
                file_exists = False
                self.store.parameters = Parameters(file_path)
            except Exception:
                file_valid = False
            
            # If the file is valid, load it, otherwise show a warning message
            if file_valid:
                new_file_path = Path.joinpath(self.store.active_project_common_parameters_directory_path, Path(file_path).name)
                if Path.exists(new_file_path):
                    if file_path in self.store.available_parameters['original_path'].tolist():
                        file_exists = True
                    else:
                        new_file_path = find_max_suffix(self.store.active_project_common_parameters_directory_path, Path(file_path).name)
                if file_exists:
                    warning = {'title': 'Parameters import error',
                               'message': 'File already exists',
                               'explanation': f'You already have a parameters file with the name {file_path} for this project. Please specify a different file.'}
                    self.parameters_warning.emit(warning)
                else:
                    new_file_path = str(new_file_path)
                    self.store.parameters.write_to_file(new_file_path)
                    self.store.add_available_parameters(path = file_path, name = file_path, original_path = file_path, project_id = self.store.active_project['id'])
            else:
                warning = {'title': 'Parameters import error',
                           'message': 'File could not be read',
                           'explanation': f'The file {file_path} is not a valid parameters file. Please see the documentation about the correct format of the parameters file.'}
                self.parameters_warning.emit(warning)                
            
    def on_available_parameters_added(self, data: dict = {}):
        if data['success']:
            self.store.update_parameters_id(parameters_id = data['data']['id'], model_id = self.store.active_model['id'])
        else:
            warning = {'title': 'Parameters data add error',
                       'message': 'Parameters data could not be added.',
                       'explanation': data['error']}
            self.parameters_warning.emit(warning)

    def save_parameters_to_file(self):
        print('save parameters to file')
        
    def import_default_values(self):
        print('import default values')