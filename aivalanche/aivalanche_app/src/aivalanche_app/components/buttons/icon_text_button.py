from PySide6.QtWidgets import QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_image import custom_image
from aivalanche_app.components.custom_layouts import h_layout, v_layout
from aivalanche_app.paths import image_placeholder_path

class icon_text_button(QPushButton):
    def __init__(self, parent = None, direction = 'horizontal', padding = (0, 0, 0, 0), button_width = None, button_height = None, minimum_width = None, minimum_height = None,
                 icon_path = None, icon_width = None, icon_height = None, icon_text_spacing = 5, icon_position = 'left', icon_resize = 'fit',
                 editable = False, text = None, text_alignment = None, checkable = False, on_click = None, on_text_edit = None, change_cursor: bool = False, object_name: str = None):
        super().__init__(parent)
        
        self.direction = direction
        self.padding = padding
        self.padding_horizontal = self.padding[0] + self.padding[2]
        self.padding_vertical = self.padding[1] + self.padding[3]
        self.button_width = button_width
        self.button_height = button_height
        self.minimum_width = minimum_width
        self.minimum_height = minimum_height
        self.icon_path = icon_path
        self.icon_width = icon_width
        self.icon_height = icon_height
        self.icon_text_spacing = icon_text_spacing
        self.icon_position = icon_position
        self.icon_resize = icon_resize
        self.editable = editable
        self.text = text
        self.text_alignment = text_alignment
        self.checkable = checkable
        self.on_click = on_click
        self.on_text_edit = on_text_edit    
        self.change_cursor = change_cursor
        self.object_name = object_name
        self.only_text = False
        self.only_icon = False
        
        self.create_layout()
        self.setContentsMargins(*self.padding)
        self.setCheckable(checkable)
        
        if self.icon_path is None and self.text is None:                        # When neither icon nor text is given.
            print('Warning: The button has to have either an icon or a text.')
            print('Setting the icon to a default image and text to "button".')
            self.icon_path = image_placeholder_path
            self.text = 'button'
        elif self.icon_path is None and self.text is not None:                  # When only text is given.
            self.only_text = True
            self.create_text_button()
        elif self.icon_path is not None and self.text is None:                  # When only icon is given.
            self.only_icon = True    
            self.create_icon_button()
        else:                                                                   # When both icon and text are given.
            self.create_icon_text_button()

        self.add_icon_or_text()
        self.set_button_dimensions()
        self.set_action()

        self.setLayout(self.layout)
        
        if self.object_name is not None:
            self.setObjectName(object_name)            
        
    def enterEvent(self, event):
        super().enterEvent(event)
        if self.change_cursor:
            self.setCursor(Qt.PointingHandCursor)


    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.change_cursor:
            self.setCursor(Qt.ArrowCursor)
        
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_button_dimensions()


    # Validate direction
    def validate_direction(self):
        if self.direction not in ('horizontal', 'vertical'):
            print('Warning: direction has to be either horizontal or vertical.')
            print('Setting it to horizontal')
            self.direction = 'horizontal'


    # Validate icon_position
    def validate_icon_position(self):
        # When direction is horizontal
        if self.direction == 'horizontal' and self.icon_position not in ('left', 'right'):
            print('Warning: icon_position has to be either left or right when direction is horizontal.')
            print('Setting it to left')
            self.icon_position = 'left'
        
        # When direction is vertical
        if self.direction == 'vertical' and self.icon_position not in ('top', 'bottom'):
            print('Warning: icon_position has to be either top or bottom when direction is vertical.')
            print('Setting it to top')
            self.icon_position = 'top'


    # Set text_alignment
    def set_text_alignment(self):
        if self.text_alignment is None:
            if self.direction == 'horizontal':
                self.text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            else:
                self.text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignHCenter


    # Set button dimensions
    def set_button_dimensions(self):        
        # Set width
        if self.button_width is not None:
            self.setFixedWidth(self.button_width)
        elif self.minimum_width is not None:
            self.setMinimumWidth(self.minimum_width)
        else:
            if self.only_icon:
                self.setMinimumWidth(self.icon_widget.width() + self.padding_horizontal)
            elif self.only_text:
                self.setMinimumWidth(self.text_widget.sizeHint().width() + self.padding_horizontal)
            else:      
                if self.direction == 'horizontal':
                    self.setMinimumWidth(self.icon_widget.width() + self.icon_text_spacing + self.text_widget.sizeHint().width() + self.padding_horizontal)
                else:
                    self.setMinimumWidth(max(self.icon_widget.width(), self.text_widget.sizeHint().width()) + self.padding_horizontal)
        
        # Set height
        if self.button_height is not None:
            self.setFixedHeight(self.button_height)
        elif self.minimum_height is not None:
            self.setMinimumHeight(self.minimum_height)        
        else:
            if self.only_icon:
                self.setMinimumHeight(self.icon_widget.height() + self.padding_vertical)
            elif self.only_text:
                self.setMinimumHeight(self.text_widget.sizeHint().height() + self.padding_vertical)
            else:      
                if self.direction == 'horizontal':
                    self.setMinimumHeight(max(self.icon_widget.height(), self.text_widget.sizeHint().height()) + self.padding_vertical)
                else:
                    self.setMinimumHeight(self.icon_widget.height() + self.icon_text_spacing + self.text_widget.sizeHint().height() + self.padding_vertical)
        
        
    # Add icon
    def create_icon(self):
        self.icon_widget = custom_image(self, image_path = self.icon_path, image_width = self.icon_width, image_height = self.icon_height, resize = self.icon_resize, on_click = self.click)
        if self.object_name is not None:
            self.icon_widget.setObjectName(self.object_name)
            
            
    # Add text
    def create_text(self):
        # If editable, then it cannot be clicked.
        if self.editable:
            self.text_widget = QLineEdit(parent = self)
            self.text_widget.setPlaceholderText(self.text)
        else:
            self.text_widget = QLabel(self.text, self)
            
        self.text_widget.setAlignment(self.text_alignment)
        
        if self.object_name is not None:
            self.text_widget.setObjectName(self.object_name)
        
        
    # Set action
    def set_action(self):
        if self.editable:
            if self.on_text_edit is not None:
                self.text_widget.textChanged.connect(self.on_text_edit)
        else:
            if self.on_click is not None:
                self.clicked.connect(self.on_click)
    
    
    # Create layout
    def create_layout(self):
        if self.icon_path is not None and self.text is not None:
            self.layout = h_layout(self, spacing = self.icon_text_spacing) if self.direction == 'horizontal' else v_layout(self, spacing = self.icon_text_spacing)
        else:
            self.layout = h_layout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    
    # Add icon and/or text to layout
    def add_icon_or_text(self):
        if self.only_icon:
            self.layout.addWidget(self.icon_widget)
        elif self.only_text:
            self.layout.addWidget(self.text_widget)
        else:
            if self.icon_position in ('left', 'top'):
                self.layout.addWidget(self.icon_widget, 0)
                self.layout.addWidget(self.text_widget, 1)
            elif self.icon_position in ('right', 'bottom'):
                self.layout.addWidget(self.text_widget, 1)
                self.layout.addWidget(self.icon_widget, 0)


    # Create only icon button.
    def create_icon_button(self):
        self.create_icon()
        
        
    # Create only text button.    
    def create_text_button(self):
        self.set_text_alignment()
        self.create_text()


    # Create icon and text button.
    def create_icon_text_button(self):
        self.validate_direction()
        self.validate_icon_position()
        self.set_text_alignment()                   
        self.create_icon()
        self.create_text()
