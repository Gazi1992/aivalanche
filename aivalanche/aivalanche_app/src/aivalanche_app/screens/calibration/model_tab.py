from PySide6.QtWidgets import QWidget, QScrollArea, QButtonGroup
from PySide6.QtCore import Qt, Signal
from aivalanche_app.components.custom_layouts import v_layout, h_layout, g_layout, clear_layout
from aivalanche_app.data_store.store import store
from aivalanche_app.components.combo_box_load_data import combo_box_load_data
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.components.custom_radio_button import custom_radio_button
from aivalanche_app.helper_functions import find_max_suffix
import pandas as pd, shutil
from pathlib import Path

class model_tab(QWidget):
    model_file_warning = Signal(dict)
    testbenches_warning = Signal(dict)
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)
        
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.store.fetch_model_templates_end.connect(self.update_model_templates)
        self.store.active_model_change_end.connect(self.check_model_file_and_testbenches_exists)
        self.store.fetch_available_model_files_end.connect(self.on_available_model_files_fetched)
        self.store.add_available_model_file_end.connect(self.on_available_model_file_added)
        self.store.update_model_file_id_end.connect(self.on_model_file_id_updated)
        self.store.fetch_available_testbenches_end.connect(self.on_available_testbenches_fetched)
        self.store.add_available_testbenches_end.connect(self.on_available_testbenches_added)
        self.store.update_testbenches_id_end.connect(self.on_testbenches_id_updated)
        
        self.model = None
        self.testbenches = []

        self.init_ui()
        
    def init_ui(self):       
        self.model_buttons_group = QButtonGroup(self)
        self.model_buttons_group.buttonClicked.connect(self.on_model_template_clicked)
        
        layout = h_layout(spacing = 40)
        self.setLayout(layout)

        # Create left scroll area
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Create left widget
        scroll_widget = QWidget(self)
        scroll_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        # Custom model button
        self.custom_model_button = custom_radio_button(parent = self, text = 'Custom model', group = self.model_buttons_group)
        scroll_layout.addWidget(self.custom_model_button)
        
        # Create load model combo box
        self.load_model_widget = combo_box_load_data(parent = self,
                                                     caption = 'Select model file',
                                                     filter = 'cir file (*.cir)',
                                                     placeholder = 'Select model file',
                                                     on_combo_box_changed = self.on_model_combo_box_changed,
                                                     on_import_new_file = self.on_import_new_model_file,
                                                     is_enabled = False,
                                                     object_name = 'round_combo_box',
                                                     is_editable = False)
        scroll_layout.addWidget(self.load_model_widget)
        
        # Create load testbench combo box
        self.load_testbenches_widget = combo_box_load_data(parent = self,
                                                           caption = 'Select testbenches file',
                                                           filter = 'json file (*.json)',
                                                           placeholder = 'Select testbenches file',
                                                           on_combo_box_changed = self.on_testbenches_combo_box_changed,
                                                           on_import_new_file = self.on_import_new_testbenches_file,
                                                           is_enabled = False,
                                                           object_name = 'round_combo_box',
                                                           is_editable = False)
        scroll_layout.addWidget(self.load_testbenches_widget)
        
        # Templates label
        templates_label = custom_label(parent = self, text = 'Templates', font_size = 'huge', opacity = 0.5)
        scroll_layout.addWidget(templates_label)
        
        self.model_templates_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        scroll_layout.addLayout(self.model_templates_layout)
    
    def update_model_templates(self, data):
        clear_layout(self.model_templates_layout)
        if not self.store.model_templates.empty:
            groups = self.store.model_templates.groupby('category')
            for (category), group  in groups:
                layout_temp = v_layout(spacing = 15) 
                label = custom_label(parent = self, text = category, font_size = 'normal')
                layout_temp.addWidget(label)
    
                grid_layout_temp = g_layout( vertical_spacing = 10)
                for index, row in group.iterrows():
                    button_temp = custom_radio_button(parent = self, text = row['name'], group = self.model_buttons_group)
                    row = index // 3
                    col = index % 3
                    grid_layout_temp.addWidget(button_temp, row, col)
                
                layout_temp.addLayout(grid_layout_temp)
                
                self.model_templates_layout.addLayout(layout_temp)
    
    def on_model_template_clicked(self, button):
        text = button.text()
        if text == 'Custom model':
            self.load_model_widget.set_state(True)
            self.load_testbenches_widget.set_state(True)
            self.store.model_template = None
        else:
            self.load_model_widget.set_state(False)
            self.load_testbenches_widget.set_state(False)
            self.store.model_template = text
            
    def set_active_radio_button(self, text):
        self.clear_data()
        for button in self.model_buttons_group.buttons():
            if button.text() == text:
                button.click()
    
    def clear_data(self):
        for button in self.model_buttons_group.buttons():
            button.setChecked(False)
    
    def reset_load_widgets(self):
        self.load_model_widget.set_active_item(None)
        self.load_testbenches_widget.set_active_item(None)
    
    def check_model_file_and_testbenches_exists(self):        
        self.clear_data()
        if self.store.active_model is not None:
            self.reset_load_widgets()
            
            # Model file
            if not pd.isnull(self.store.active_model['model_file_id']):
                model_file_path = self.store.available_model_files.loc[self.store.available_model_files['id'] == self.store.active_model['model_file_id'], 'path']
                model_file_name = self.store.available_model_files.loc[self.store.available_model_files['id'] == self.store.active_model['model_file_id'], 'name']
                if model_file_path.empty:
                    self.store.update_model_file_id(model_file_id = None, model_id = self.store.active_model['id'])
                else:
                    self.store.model_file_path = model_file_path.iloc[0]
                    self.load_model_widget.set_active_item(model_file_name.iloc[0], trigger_on_change_slot = False)
            
            # Testbenches file
            if not pd.isnull(self.store.active_model['testbenches_id']):
                testbenches_path = self.store.available_testbenches.loc[self.store.available_testbenches['id'] == self.store.active_model['testbenches_id'], 'path']
                testbenches_name = self.store.available_testbenches.loc[self.store.available_testbenches['id'] == self.store.active_model['testbenches_id'], 'name']
                if testbenches_path.empty:
                    self.store.update_testbenches_id(testbenches_id = None, model_id = self.store.active_model['id'])
                else:
                    self.store.testbenches_path = testbenches_path.iloc[0]
                    self.load_testbenches_widget.set_active_item(testbenches_name.iloc[0], trigger_on_change_slot = False)
            
            
            if not pd.isnull(self.store.active_model['model_template']):
                self.set_active_radio_button(self.store.active_model['model_template'])
            elif not pd.isnull(self.store.active_model['model_file_id']) or not pd.isnull(self.store.active_model['testbenches_id']):
                self.set_active_radio_button('Custom model')
    
    def on_model_combo_box_changed(self, val):
        if val is not None and len(val) > 0:
            model_file_id = self.store.available_model_files.loc[self.store.available_model_files['name'] == val,'id'].iloc[0]
            self.store.update_model_file_id(model_file_id = model_file_id, model_id = self.store.active_model['id'])
    
    def on_model_file_id_updated(self, data: dict = {}):
        if data['success']:
            if not pd.isnull(self.store.active_model['model_file_id']):
                model_file_path = self.store.available_model_files.loc[self.store.available_model_files['id'] == self.store.active_model['model_file_id'], 'path'] 
                if model_file_path.empty:
                    self.store.fetch_available_model_files(self.store.active_project['id'])
                else:
                    self.store.model_file_path = model_file_path.iloc[0]
        else:
            print(data['error'])
    
    def on_available_model_files_fetched(self, data: dict = {}):
        if data['success']:
            self.load_model_widget.update_items(self.store.available_model_files['name'].tolist())
            self.check_model_file_and_testbenches_exists()
    
    def on_available_model_file_added(self, data: dict = {}):
        if data['success']:
            self.store.update_model_file_id(model_file_id = data['data']['id'], model_id = self.store.active_model['id'])
        else:
            warning = {'title': 'Model file add error',
                       'message': 'Model file could not be added.',
                       'explanation': data['error']}
            self.model_file_warning.emit(warning)
    
    def on_import_new_model_file(self, file_path: str = None):
        if file_path is not None:            
            file_exists = False
            new_file_path = Path.joinpath(self.store.active_project_common_model_files_directory, Path(file_path).name)
            if Path.exists(new_file_path):
                if file_path in self.store.available_model_files['original_path'].tolist():
                    file_exists = True
                else:
                    new_file_path = find_max_suffix(self.store.active_project_common_model_files_directory, Path(file_path).name)
            if file_exists:
                warning = {'title': 'Model import error',
                           'message': 'File already exists',
                           'explanation': f'You already have a model file with the name {file_path} for this project. Please specify a different file.'}
                self.model_file_warning.emit(warning)
            else:
                new_file_path = str(new_file_path)
                shutil.copy(file_path, new_file_path)
                self.store.add_available_model_file(path = new_file_path, name = file_path, original_path = file_path, project_id = self.store.active_project['id'])
    
    def on_testbenches_combo_box_changed(self, val):
        if val is not None and len(val) > 0:
            testbenches_id = self.store.available_testbenches.loc[self.store.available_testbenches['name'] == val,'id'].iloc[0]
            self.store.update_testbenches_id(testbenches_id = testbenches_id, model_id = self.store.active_model['id'])
    
    def on_testbenches_id_updated(self, data: dict = {}):
        if data['success']:
            if not pd.isnull(self.store.active_model['testbenches_id']):
                testbenches_path = self.store.available_testbenches.loc[self.store.available_testbenches['id'] == self.store.active_model['testbenches_id'], 'path'] 
                if testbenches_path.empty:
                    self.store.fetch_available_testbenches(self.store.active_project['id'])
                else:
                    self.store.testbenches_path = testbenches_path.iloc[0]
        else:
            print(data['error'])
    
    def on_available_testbenches_fetched(self, data: dict = {}):
        if data['success']:
            self.load_testbenches_widget.update_items(self.store.available_testbenches['name'].tolist())
            self.check_model_file_and_testbenches_exists()                
    
    def on_available_testbenches_added(self, data: dict = {}):
        if data['success']:
            self.store.update_testbenches_id(testbenches_id = data['data']['id'], model_id = self.store.active_model['id'])
        else:
            warning = {'title': 'Testbenches add error',
                       'message': 'Testbenches could not be added.',
                       'explanation': data['error']}
            self.testbenches_warning.emit(warning)
    
    def on_import_new_testbenches_file(self, file_path: str = None):
        if file_path is not None:            
            file_exists = False
            new_file_path = Path.joinpath(self.store.active_project_common_testbenches_directory, Path(file_path).name)
            if Path.exists(new_file_path):
                if file_path in self.store.available_testbenches['original_path'].tolist():
                    file_exists = True
                else:
                    new_file_path = find_max_suffix(self.store.active_project_common_testbenches_directory, Path(file_path).name)
            if file_exists:
                warning = {'title': 'Testbenches import error',
                           'message': 'File already exists',
                           'explanation': f'You already have a testbenches file with the name {file_path} for this project. Please specify a different file.'}
                self.testbenches_warning.emit(warning)
            else:
                new_file_path = str(new_file_path)
                shutil.copy(file_path, new_file_path)
                self.store.add_available_testbenches(path = new_file_path, name = file_path, original_path = file_path, project_id = self.store.active_project['id'])