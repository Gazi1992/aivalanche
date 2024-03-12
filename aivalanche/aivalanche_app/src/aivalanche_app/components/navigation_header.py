from PySide6.QtWidgets import QWidget, QLabel
from aivalanche_app.components.custom_layouts import h_layout, v_layout, clear_layout
from aivalanche_app.components.calibration_control import calibration_control
from aivalanche_app.constants.dimensions import HEADER_PADDING_LEFT, HEADER_PADDING_RIGHT, HEADER_PADDING_TOP, HEADER_PADDING_BOTTOM, SEARCH_BAR_HEIGHT, SEARCH_BAR_WIDTH, SEARCH_ICON_HEIGHT, SEARCH_ICON_WIDTH
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.paths import search_icon_path

class navigation_header(QWidget):
    def __init__(self, parent = None, navigation_path: list[dict] = None, on_search_text_changed: callable = None, labels: list[str] = None, show_calibration_buttons: bool = False, object_name: str = None):
        super().__init__(parent = parent)
        
        self.navigation_path = navigation_path
        if object_name is not None:
            self.setObjectName(object_name)
        
        main_layout = v_layout(padding = (HEADER_PADDING_LEFT, HEADER_PADDING_TOP, HEADER_PADDING_RIGHT, HEADER_PADDING_BOTTOM))
        self.setLayout(main_layout)

        # Top layout
        layout_top = h_layout()
        
        # Add navigation paths
        if self.navigation_path is not None:
            self.layout_top_left = h_layout(spacing = 5)
            self.update_navigation_path(self.navigation_path)
            layout_top.addLayout(self.layout_top_left)
                
        layout_top.addStretch()
        layout_top.addStretch()

        # Add search bar
        if on_search_text_changed is not None:
            search_bar = icon_text_button(parent = self, icon_path = search_icon_path, button_height = SEARCH_BAR_HEIGHT, button_width = SEARCH_BAR_WIDTH,
                                          padding = (20, 0, 50, 0), icon_text_spacing = 20,
                                          icon_width = SEARCH_ICON_WIDTH, icon_height = SEARCH_ICON_HEIGHT,
                                          text = "Search", editable = True, on_text_edit = on_search_text_changed, object_name = 'search_bar')
            layout_top.addWidget(search_bar)
        
        # Add calibration buttons
        if show_calibration_buttons:
            calibration_control_widget = calibration_control(parent = self, object_name = 'calibration_control')
            layout_top.addWidget(calibration_control_widget)        
        
        # Add the top layout
        main_layout.addLayout(layout_top)
    
        # Bottom layout
        layout_bottom = h_layout()        
        
        # Add labels
        if labels is not None:
            text = QLabel('Labes:')
            layout_bottom.addWidget(text)
        
        # Add bottom layout
        main_layout.addLayout(layout_bottom)
        
    
    def update_navigation_path(self, navigation_path):
        clear_layout(self.layout_top_left)
        self.navigation_path = navigation_path
        for i, item in enumerate(self.navigation_path):
            if i > 0:
                self.layout_top_left.addWidget(QLabel('>'))
            temp = icon_text_button(parent = self, text = item['text'], on_click = item['on_click'], change_cursor = True, checkable = False, object_name = 'navigation_header')
            self.layout_top_left.addWidget(temp)