from PySide6.QtWidgets import QWidget, QSplitter, QScrollArea
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_layouts import v_layout
from aivalanche_app.components.custom_label import custom_label
from aivalanche_app.components.custom_combo_box import custom_combo_box
from aivalanche_app.components.combo_box_load_data import combo_box_load_data
from aivalanche_app.components.optimization_parameters import optimization_parameters
from aivalanche_app.components.loss_part_card import loss_part_card
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.data_store.store import store
import uuid, functools


class optimization_tab(QWidget):
    
    def __init__(self, parent = None, store: store = None, object_name: str = None):
        super().__init__(parent)

        if object_name is not None:
            self.setObjectName(object_name)
        
        self.store = store
        self.optimizers = self.store.optimizers
        self.simulators = self.store.simulators
        self.active_optimizer = None
        self.active_simulator = None
        self.loss_parts = {}
                
        self.init_ui()
        
        
    def init_ui(self):
        layout = v_layout()        
        self.setLayout(layout)
        
        splitter = QSplitter(parent = self)
        splitter.setHandleWidth(0)
        layout.addWidget(splitter, 1)
        
        # Create left scroll area
        left_scroll_area = QScrollArea(parent = splitter)
        left_scroll_area.setWidgetResizable(True)
        
        # Create left widget
        left_widget = QWidget(self)
        left_widget.setContentsMargins(0, 0, 10, 0)
        left_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        left_widget.setLayout(left_layout)
        left_scroll_area.setWidget(left_widget)
        
        # Optimizer configuration label
        optimizer_config_label = custom_label(parent = self, text = 'Optimizer configuration', font_size = 'huge', opacity = 0.5)
        left_layout.addWidget(optimizer_config_label)
        
        # Optimizer selection
        optimizer_selection_widget = custom_combo_box(parent = self,
                                                      items = [item['name'] for item in self.optimizers],
                                                      is_editable = False,
                                                      object_name = 'round_combo_box',
                                                      placeholder = 'Select optimizer')
        self.active_optimizer = optimizer_selection_widget.active_item
        left_layout.addWidget(optimizer_selection_widget)
        
        # Optimizer parameters
        optimizer_parameters_widget = optimization_parameters(parent = self, parameters = self.get_optimizer_parameters())
        left_layout.addWidget(optimizer_parameters_widget)
        
        left_layout.addSpacing(50)
        
        # Simulator configuration label
        simulator_config_label = custom_label(parent = self, text = 'Simulator configuration', font_size = 'huge', opacity = 0.5)
        left_layout.addWidget(simulator_config_label)
        
        # Simulator selection
        simulator_selection_widget = custom_combo_box(parent = self,
                                                      items = [item['name'] for item in self.simulators],
                                                      is_editable = False,
                                                      object_name = 'round_combo_box',
                                                      placeholder = 'Select simulator')
        self.active_simulator = simulator_selection_widget.active_item
        left_layout.addWidget(simulator_selection_widget)
        
        # Simulator parameters
        simulator_parameters_widget = optimization_parameters(parent = self, parameters = self.get_simulator_parameters())
        left_layout.addWidget(simulator_parameters_widget)
        
        # Create right scroll area
        right_scroll_area = QScrollArea(parent = splitter)
        right_scroll_area.setContentsMargins(0, 0, 0, 0)
        right_scroll_area.setWidgetResizable(True)
        
        # Create right widget
        right_widget = QWidget(self)
        self.right_layout = v_layout(spacing = 20, alignment = Qt.AlignmentFlag.AlignTop)
        right_widget.setLayout(self.right_layout)
        right_widget.setContentsMargins(10, 0, 10, 0)
        right_scroll_area.setWidget(right_widget)
        
        # loss funtion configuration label
        loss_function_config_label = custom_label(parent = self, text = 'Loss function configuration', font_size = 'huge', opacity = 0.5)
        self.right_layout.addWidget(loss_function_config_label)
        
        # Create load data combo box
        custom_loss_widget = combo_box_load_data(parent = self,
                                                    caption = 'Select loss function file',
                                                    filter = 'Python file (*.py)',
                                                    placeholder = 'Select loss function file',
                                                    on_combo_box_changed = self.load_custom_loss_function,
                                                    object_name = 'round_combo_box')       
        self.right_layout.addWidget(custom_loss_widget)
                
        # Save parameter to file button
        add_part_button = icon_text_button(parent = self, text = 'Add loss part', padding = (10, 5, 10, 5), object_name = 'add_loss_card_button', on_click = self.on_add_loss_part_click)
        self.right_layout.addWidget(add_part_button, alignment = Qt.AlignmentFlag.AlignLeft)
        
        # add the first loos part
        self.on_add_loss_part_click()
        
        # set the left and right widgets to equal width initially
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        

    def load_custom_loss_function(self, text):
        print(text)
        
    def get_optimizer_parameters(self):
        optimizer = [item for item in self.optimizers if item['name'] == self.active_optimizer][0]
        return optimizer['parameters']
    
    def get_simulator_parameters(self):
        simulator = [item for item in self.simulators if item['name'] == self.active_simulator][0]
        return simulator['parameters']
    
    def on_add_loss_part_click(self):
        id = uuid.uuid4()
        loss_part_widget = loss_part_card(object_name = 'loss_card',
                                          on_delete_button_clicked = functools.partial(self.on_delete_loss_part, id))
        self.loss_parts[id] = loss_part_widget
        self.right_layout.insertWidget(self.right_layout.count() - 1, loss_part_widget)
        
    def on_delete_loss_part(self, id):
        self.right_layout.removeWidget(self.loss_parts[id])
        self.loss_parts[id].deleteLater()
        del self.loss_parts[id]
        
        
        
        
        
        
        
        
        
        
        