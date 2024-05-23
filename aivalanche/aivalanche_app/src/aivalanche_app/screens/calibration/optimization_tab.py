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
        self.store.fetch_available_optimizers_end.connect(self.update_optimizers)
        self.store.fetch_available_simulators_end.connect(self.update_simulators)
        
        self.active_optimizer = None
        self.active_simulator = None
        self.loss_parts = {}
                
        self.init_ui()
        
        
    def init_ui(self):
        layout = v_layout()        
        self.setLayout(layout)
        
        self.splitter = QSplitter(parent = self)
        layout.addWidget(self.splitter, 1)
        
        # Create left scroll area
        left_scroll_area = QScrollArea(parent = self.splitter)
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
        self.optimizer_selection_widget = custom_combo_box(parent = self, is_editable = False, object_name = 'round_combo_box',
                                                           placeholder = 'Select optimizer', on_change = self.on_optimizer_change)
        left_layout.addWidget(self.optimizer_selection_widget)
        
        # Optimizer parameters
        self.optimizer_parameters_widget = optimization_parameters(parent = self)
        left_layout.addWidget(self.optimizer_parameters_widget)
        
        left_layout.addSpacing(50)
        
        # Simulator configuration label
        simulator_config_label = custom_label(parent = self, text = 'Simulator configuration', font_size = 'huge', opacity = 0.5)
        left_layout.addWidget(simulator_config_label)
        
        # Simulator selection
        self.simulator_selection_widget = custom_combo_box(parent = self, is_editable = False, object_name = 'round_combo_box',
                                                           placeholder = 'Select simulator', on_change = self.on_simulator_change)
        left_layout.addWidget(self.simulator_selection_widget)
        
        # Simulator parameters
        self.simulator_parameters_widget = optimization_parameters(parent = self)
        left_layout.addWidget(self.simulator_parameters_widget)
        
        # Create right scroll area
        right_scroll_area = QScrollArea(parent = self.splitter)
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
        
        # Add the first loos part
        self.on_add_loss_part_click()
    
        # Set the initial stretches
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 1)
    
    def update_optimizers(self):
        items = list(set(self.store.available_optimizers['optimizer'].to_list()))
        items.sort()
        self.optimizer_selection_widget.update_items(items = items, active_item = items[0])
        self.update_optimizer_parameters()
    
    def update_optimizer_parameters(self):
        self.active_optimizer = self.optimizer_selection_widget.active_item
        parameters = self.store.available_optimizers[(self.store.available_optimizers['optimizer'] == self.active_optimizer) & (self.store.available_optimizers['category'] == 'normal')]
        parameters.reset_index(drop = True, inplace = True)
        self.optimizer_parameters_widget.update_parameters(parameters)
        
    def on_optimizer_change(self, val):
        self.update_optimizer_parameters()

    def update_simulators(self):
        items = list(set(self.store.available_simulators['simulator'].to_list()))
        items.sort()
        self.simulator_selection_widget.update_items(items = items, active_item = items[0])
        self.update_simulator_parameters()
        
    def update_simulator_parameters(self):
        self.active_simulator = self.simulator_selection_widget.active_item
        parameters = self.store.available_simulators[(self.store.available_simulators['simulator'] == self.active_simulator) & (self.store.available_simulators['category'] == 'normal')]
        parameters.reset_index(drop = True, inplace = True)
        self.simulator_parameters_widget.update_parameters(parameters)
        
    def on_simulator_change(self, val):
        self.update_simulator_parameters()

    def load_custom_loss_function(self, text):
        print(text)
    
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