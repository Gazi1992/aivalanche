from PySide6.QtWidgets import QWidget, QLabel, QProgressBar, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from aivalanche_app.components.custom_layouts import h_layout, v_layout
from aivalanche_app.components.buttons.icon_button import icon_button
from aivalanche_app.data_store.store import store
from aivalanche_app.paths import play_icon_path, play_hover_icon_path, play_press_icon_path, \
                                 play_1_icon_path, play_1_hover_icon_path, play_1_press_icon_path, \
                                 pause_icon_path, pause_hover_icon_path, pause_press_icon_path, \
                                 stop_icon_path, stop_hover_icon_path, stop_press_icon_path

class calibration_control(QWidget):
    single_simulation_button_press = Signal()
    calibration_button_press = Signal()
    abort_button_press = Signal()
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent = parent)
        
        self.store = store
        self.store.update_model_status_end.connect(self.on_simulation_and_calibration_signals)
        self.store.active_model_change_start.connect(self.on_active_model_about_to_change)
        self.store.active_model_change_end.connect(self.on_active_model_changed)
        self.store.calibration_progress.connect(self.on_calibration_progress)
        
        self.single_simulation_button_press.connect(self.store.start_single_simulation)
        self.calibration_button_press.connect(self.store.start_calibration)
        self.abort_button_press.connect(self.store.abort_calibration)
        
        self.object_name = object_name
        if object_name is not None:
            self.setObjectName(object_name)
        
        self.progress_value = 10
        self.progress_min = 0
        self.progress_max = 100
        self._status = None
    
        self.init_ui()
        
    @property
    def progress_percentage(self):
        return f'{self.progress_value}%'
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if self._status != value:
            self._status = value
        self.update_ui_based_on_status()
        
    def init_ui(self):
        layout = h_layout(spacing = 5, alignment = Qt.AlignmentFlag.AlignBottom)
        self.setLayout(layout)
        
        # single simulation button
        self.single_simulation_button = icon_button(parent = self,
                                                    icon_path = play_1_icon_path,
                                                    icon_hover_path = play_1_hover_icon_path,
                                                    icon_press_path = play_1_press_icon_path,
                                                    object_name = self.object_name,
                                                    on_click = lambda: self.single_simulation_button_press.emit())
        layout.addWidget(self.single_simulation_button, alignment = Qt.AlignmentFlag.AlignBottom)
        
        # calibration button
        self.calibration_button = icon_button(parent = self,
                                              icon_path = play_icon_path,
                                              icon_hover_path = play_hover_icon_path,
                                              icon_press_path = play_press_icon_path,
                                              object_name = self.object_name,
                                              on_click = lambda: self.calibration_button_press.emit())
        layout.addWidget(self.calibration_button, alignment = Qt.AlignmentFlag.AlignBottom)
        
        # abort button
        self.abort_button = icon_button(parent = self,
                                        icon_path = stop_icon_path,
                                        icon_hover_path = stop_hover_icon_path,
                                        icon_press_path = stop_press_icon_path,
                                        object_name = self.object_name,
                                        on_click = lambda: self.abort_button_press.emit())
        layout.addWidget(self.abort_button, alignment = Qt.AlignmentFlag.AlignBottom)
        
        # add some space between the buttons and the progress bar
        layout.addSpacing(10)
        
        # progress widget
        progress_widget = QWidget()
        progress_widget.setMaximumWidth(400)
        layout.addWidget(progress_widget, alignment = Qt.AlignmentFlag.AlignBottom)

        progress_layout = v_layout(spacing = 2)
        progress_widget.setLayout(progress_layout)
        
        # progress text
        progress_text_layout = h_layout(spacing = 5)
        progress_layout.addLayout(progress_text_layout)
        
        self.progress_info_label = QLabel(parent=self, text = 'Calibration progress')
        progress_text_layout.addWidget(self.progress_info_label)
    
        progress_text_layout.addStretch()

        self.progress_percentage_label = QLabel(parent=self, text = self.progress_percentage)
        progress_text_layout.addWidget(self.progress_percentage_label)
        
        # progress bar
        self.progress_bar = QProgressBar(parent = self)
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setValue(self.progress_value)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

    def on_active_model_about_to_change(self):
        self.setVisible(False)

    def update_progress(self, value):
        if self.progress_value != value:
            self.progress_value = value
            
    def on_active_model_changed(self):
        if self.store.active_model is not None:
            self.status = self.store.active_model['status']
        else:
            self.status = None
        
    def update_ui_based_on_status(self):
        if not self.isVisible():
            self.setVisible(True)
        self.progress_bar.setRange(self.progress_min, self.progress_max)
        self.progress_percentage_label.setVisible(False)
        
        if self.status is None:
            self.update_progress(0)
            self.progress_info_label.setText("Model setup")
            self.progress_bar.setValue(self.progress_value)
            return
        
        if self.status == 'setup':
            self.update_progress(0)
            self.progress_info_label.setText("Model setup")
            self.progress_bar.setValue(self.progress_value)
        elif self.status == 'single simulation in progress':
            self.progress_bar.setRange(0, 0)  # This makes the progress bar enter "busy" mode, i.e. loading
            self.progress_info_label.setText("Simulation in progress...")
        elif self.status == 'single simulation finished':
            self.update_progress(100)
            self.progress_info_label.setText("Simulation finished")
            self.progress_bar.setValue(self.progress_value)
        elif self.status == 'starting calibration':
            self.progress_bar.setRange(0, 0)  # This makes the progress bar enter "busy" mode
            self.progress_info_label.setText("Starting calibration...")
        elif self.status == 'calibration in progress':
            progress = round((int(self.store.active_model['iteration']) / int(self.store.active_model['max_iterations'])) * 100, 1)
            self.update_progress(progress)
            self.progress_info_label.setText("Calibration in progress...")
            self.progress_bar.setValue(self.progress_value)
            self.progress_percentage_label.setText(self.progress_percentage)
            self.progress_percentage_label.setVisible(True)
        elif self.status == 'calibration aborted':
            self.update_progress(100)
            self.progress_info_label.setText("Calibration aborted")
            self.progress_bar.setValue(self.progress_value)
            self.progress_percentage_label.setText(self.progress_percentage)
            self.progress_percentage_label.setVisible(True)
        elif self.status == 'aborting calibration':
            self.progress_bar.setRange(0, 0)  # This makes the progress bar enter "busy" mode, i.e. loading
            self.progress_info_label.setText("Aborting calibration...")
        elif self.status == 'calibration finished':
            self.update_progress(100)
            self.progress_info_label.setText("Calibration finished")
            self.progress_bar.setValue(self.progress_value)
            self.progress_percentage_label.setText(self.progress_percentage)
            self.progress_percentage_label.setVisible(True)
        else:
            self.update_progress(0)
            self.progress_info_label.setText("Model setup")
            self.progress_bar.setValue(self.progress_value)
            
        self.update_buttons()
            
    def on_simulation_and_calibration_signals(self, data):
        if data['model_id'] == self.store.active_model['id']:
            self.status = self.store.active_model['status']
            
    def on_calibration_progress(self, data):
        if data['model_id'] == self.store.active_model['id']:
            progress = round((int(data['iteration']) / int(data['max_iterations'])) * 100, 1)
            self.update_progress(progress)
            self.progress_info_label.setText("Calibration in progress...")
            self.progress_bar.setValue(self.progress_value)
            self.progress_percentage_label.setText(self.progress_percentage)
            self.progress_percentage_label.setVisible(True)
            
    def update_buttons(self):
        if self.status in ['starting calibration', 'aborting calibration']:
            self.calibration_button.setEnabled(False)
            self.single_simulation_button.set_enabled(False)
            self.abort_button.set_enabled(False)
        elif self.status == 'calibration in progress':
            self.calibration_button.setEnabled(False)
            self.single_simulation_button.set_enabled(False)
            self.abort_button.set_enabled(True)
        else:
            self.calibration_button.setEnabled(True)
            self.single_simulation_button.set_enabled(True)
            self.abort_button.set_enabled(False)
        
        # try:
        #     if self.store.model_calibration_running():
        #         self.calibration_button.setEnabled(False)
        #         self.single_simulation_button.set_enabled(False)
        #         self.abort_button.set_enabled(True)
        #     else:
        #         self.calibration_button.setEnabled(True)
        #         self.single_simulation_button.set_enabled(True)
        #         self.abort_button.set_enabled(False)
        # except:
        #     pass
        
        # try:
        #     if self.store.single_simulation and self.store.single_simulation.is_running():
        #         self.single_simulation_button.set_enabled(False)
        #         self.calibration_button.setEnabled(False)
        #     else:
        #         self.single_simulation_button.set_enabled(True)
        #         self.calibration_button.setEnabled(True)
        # except:
        #     pass