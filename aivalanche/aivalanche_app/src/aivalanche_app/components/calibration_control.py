from PySide6.QtWidgets import QWidget, QLabel, QProgressBar, QHBoxLayout
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import h_layout, v_layout
from aivalanche_app.components.buttons.custom_icon_button import custom_icon_button
from aivalanche_app.paths import play_icon_path, play_hover_icon_path, play_press_icon_path, \
                                 play_1_icon_path, play_1_hover_icon_path, play_1_press_icon_path, \
                                 pause_icon_path, pause_hover_icon_path, pause_press_icon_path, \
                                 stop_icon_path, stop_hover_icon_path, stop_press_icon_path

class calibration_control(QWidget):
    def __init__(self, parent = None, object_name: str = None):
        super().__init__(parent = parent)
        
        self.object_name = object_name
        if object_name is not None:
            self.setObjectName(object_name)
    
        self.init_ui()

    
    def init_ui(self):
        layout = h_layout(spacing = 5, alignment = Qt.AlignmentFlag.AlignBottom)
        self.setLayout(layout)
        
        # single simulation button
        single_simulation_button = custom_icon_button(parent = self,
                                                      icon_path = play_1_icon_path,
                                                      icon_hover_path = play_1_hover_icon_path,
                                                      icon_press_path = play_1_press_icon_path,
                                                      object_name = self.object_name,
                                                      on_click = self.on_single_simulation_button_click)
        layout.addWidget(single_simulation_button, alignment = Qt.AlignmentFlag.AlignBottom)
        
        # calibration button
        calibration_button = custom_icon_button(parent = self,
                                                icon_path = play_icon_path,
                                                icon_hover_path = play_hover_icon_path,
                                                icon_press_path = play_press_icon_path,
                                                object_name = self.object_name,
                                                on_click = self.on_calibration_button_click)
        layout.addWidget(calibration_button, alignment = Qt.AlignmentFlag.AlignBottom)
        
        # abort button
        abort_button = custom_icon_button(parent = self,
                                          icon_path = stop_icon_path,
                                          icon_hover_path = stop_hover_icon_path,
                                          icon_press_path = stop_press_icon_path,
                                          object_name = self.object_name,
                                          on_click = self.on_abort_button_click)
        layout.addWidget(abort_button, alignment = Qt.AlignmentFlag.AlignBottom)
        
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
        
        progress_info = QLabel(parent = self, text = 'Calibration progress')
        progress_text_layout.addWidget(progress_info)

        progress_text_layout.addStretch()

        progress_percentage = QLabel(parent = self, text = '30%')
        progress_text_layout.addWidget(progress_percentage)
        
        # progress bar
        progress_bar = QProgressBar(parent = self)
        progress_bar.setFixedHeight(15)
        progress_bar.setValue(30)
        progress_bar.setTextVisible(False)
        progress_layout.addWidget(progress_bar)
        
    
    def on_single_simulation_button_click(self):
        print('on_single_simulation_button_click')
        

    def on_calibration_button_click(self):
        print('on_calibration_button_click')
        
    def on_abort_button_click(self):
        print('on_abort_button_click')