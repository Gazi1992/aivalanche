from aivalanche_app.paths import arrow_down_icon_path, radio_button_checked_path, radio_button_checked_hovered_path, \
                                 radio_button_checked_pressed_path, radio_button_unchecked_path, radio_button_unchecked_hovered_path, \
                                 radio_button_unchecked_pressed_path
                                 
MAIN_BACKGROUND_COLOR = '#f2faff'
SECOND_BACKGROUND_COLOR = '#e0f4fb'
TEXT_COLOR = '#062279'
PLOT_COLORS = ['#0075FF', '#FF5C00', '#19B100', '#EB00FF', '#FFD600']
FONT_SIZES = {'normal': 14, 'small': 12, 'large': 16, 'huge': 18, 'tiny': 10}

theme = """
    QWidget {background-color: transparent; border: none;}
    QFrame {background-color: transparent; border: none;}
    QSplitter {background-color: transparent; border: none;}
    QStackedWidget {background-color: transparent; border: none;}
    QTabWidget {background-color: transparent; border: none;}
    QScrollArea {background-color: transparent; border: none;}
    
    QScrollBar:handle {background-color: rgba(6, 34, 121, 50);}
    QScrollBar:handle:hover {background-color: rgba(6, 34, 121, 100);}
    QScrollBar:vertical {width: 10px; border: none; border-radius: 5px;}
    QScrollBar:horizontal {height: 10px; border: none; border-radius: 5px;}
    QScrollBar:sub-line {border: none;}
    QScrollBar:add-line {border: none;}
    QScrollBar:sub-page {border: none;}
    QScrollBar:add-page {border: none;}
    
    QDialog QPushButton {background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f2faff, stop:1 #e0f4fb); border: 1px solid rgba(6, 34, 121, 170); padding: 5px;} 
    QPushButton:hover {background: rgba(6, 34, 121, 50);}
    QPushButton:pressed {background: rgba(6, 34, 121, 125);}
    
    QLineEdit {background: white; border: 1px solid rgba(6, 34, 121, 170); padding: 5px;}
                                                     
    QWidget#home {background-color: %s;}
    QMenu {background-color: %s; color: %s;}

    QLabel {background-color: transparent; border: none; color: %s}
    QDialog {min-width: 500px; background-color: %s;}
    
    QTableView {background: %s; border: 1px solid #062279; color: %s; gridline-color: rgba(6, 34, 121, 50);}
    QTableCornerButton::section {background: %s; border-width: 0px 1px 1px 0px; border-style: solid; border-color: rgba(6, 34, 121, 170);}
    QHeaderView {background: %s; color: %s}
    QHeaderView:section:horizontal {background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f2faff, stop:1 #e0f4fb); border-width: 0px 1px 1px 0px; border-style: solid; border-color: rgba(6, 34, 121, 170); padding: 2px 4px;}
    QHeaderView:section:vertical {background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f2faff, stop:1 #e0f4fb);  border-width: 0px 1px 1px 0px; border-style: solid; border-color: rgba(6, 34, 121, 170); padding: 2px 4px;}
    
    QComboBox {background-color: white; border: 1px solid #062279; border-radius: 15px; selection-background-color: rgba(6, 34, 121, 50); padding-left: 10; color: %s;}
    QComboBox:down-arrow {image: url(%s); width: 20px;}
    QComboBox:drop-down:button {border: none; width: 20px; padding-right: 5px}
    
    QRadioButton:indicator {width: 15px; height: 15px;}
    QRadioButton:indicator::unchecked {image: url(%s);}
    QRadioButton:indicator:unchecked:hover {image: url(%s);}
    QRadioButton:indicator:unchecked:pressed {image: url(%s);}
    QRadioButton:indicator::checked {image: url(%s);}
    QRadioButton:indicator:checked:hover {image: url(%s);}
    QRadioButton:indicator:checked:pressed {image: url(%s);}
    
    QFrame#drawer {background-color: white;}
    QPushButton#drawer_button {background-color: transparent; color: #000000; border: none;}
    QPushButton#drawer_button:hover {background-color: #D9D9D9;}
    QPushButton#drawer_button:pressed {background-color: #C9C9C9;}
    QPushButton#drawer_button:checked {background-color: #BAF0F8;}

    QPushButton#new_project {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #E0F4FB); border: 1px solid #062279;}
    QPushButton#new_project:hover {background-color: #D5E8EE;}
    QPushButton#new_project:pressed {background-color: #CADCE2;}
    
    QPushButton#new_model {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #E0F4FB); border: 1px solid #062279;}
    QPushButton#new_model:hover {background-color: #D5E8EE;}
    QPushButton#new_model:pressed {background-color: #CADCE2;}
    
    QWidget#search_bar {background-color: white; border-radius: 20px;}
    QLineEdit#search_bar {background: transparent; border: none;}

    QWidget#modal {background-color: %s; color: #062279;}
    QPushButton#modal {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #EAEAEA); border-radius: 5; border: 1px solid #062279; padding: 5 10;}
    QPushButton#modal:hover {background-color: #D5E8EE;}
    QPushButton#modal:pressed {background-color: #CADCE2;}
    QLineEdit#modal {min-width: 500px;}
    QLabel#modal_message {font-size: 11pt;}
    QLabel#modal_explanation {color: #067934; font-size: 9pt;}

""" % (MAIN_BACKGROUND_COLOR, MAIN_BACKGROUND_COLOR, TEXT_COLOR, TEXT_COLOR, MAIN_BACKGROUND_COLOR, MAIN_BACKGROUND_COLOR,
        TEXT_COLOR, MAIN_BACKGROUND_COLOR, MAIN_BACKGROUND_COLOR, TEXT_COLOR, TEXT_COLOR, arrow_down_icon_path, radio_button_unchecked_path,
        radio_button_unchecked_hovered_path, radio_button_unchecked_pressed_path,
        radio_button_checked_path, radio_button_checked_hovered_path, radio_button_checked_pressed_path, MAIN_BACKGROUND_COLOR)







THEME = {    
    "home": """
        QWidget {background-color: %s; color: #062279;}
    """ % MAIN_BACKGROUND_COLOR,
    "drawer": """
        QFrame {background-color: white;}
        QPushButton {background-color: transparent; color: #000000; border: none;}
        QPushButton:hover {background-color: #D9D9D9;}
        QPushButton:pressed {background-color: #C9C9C9;}
        QPushButton:checked {background-color: #BAF0F8;}
        QLabel {background-color: transparent;}
    """,
    "main_tabs": """       
        QTabWidget {background-color: transparent; border: none;}
        QTabBar {background-color: transparent; border: none;}
    """,
    "projects_tab": """
        QWidget {background-color: transparent; border: none;}
    """,
    "running_tab": """
        QWidget {background-color: transparent; border: none;}
    """,
    "new_project_button": """
        QPushButton {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #E0F4FB); border: 1px solid #062279;}
        QPushButton:hover {background-color: #D5E8EE;}
        QPushButton:pressed {background-color: #CADCE2;}
        QLabel {background-color: transparent;}
    """,
    "new_model_button": """
        QPushButton {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #E0F4FB); border: 1px solid #062279;}
        QPushButton:hover {background-color: #D5E8EE;}
        QPushButton:pressed {background-color: #CADCE2;}
        QLabel {background-color: transparent;}
    """,
    "my_projects": """
        QWidget {background-color: transparent; border: none;}
        QScrollBar:handle {background-color: rgba(6, 34, 121, 50);}
        QScrollBar:handle:hover {background-color: rgba(6, 34, 121, 100);}
        QScrollBar:vertical {width: 10px; border: none; border-radius: 5px;}
        QScrollBar:horizontal {height: 10px; border: none; border-radius: 5px;}
        QScrollBar:sub-line {border: none;}"
        QScrollBar:add-line {border: none;}"
        QScrollBar:sub-page {border: none;}"
        QScrollBar:add-page {border: none;}"
    """,
    "my_models": """
        QWidget {background-color: transparent; border: none;}
        QScrollBar:handle {background-color: rgba(6, 34, 121, 50);}
        QScrollBar:handle:hover {background-color: rgba(6, 34, 121, 100);}
        QScrollBar:vertical {width: 10px; border: none; border-radius: 5px;}
        QScrollBar:horizontal {height: 10px; border: none; border-radius: 5px;}
        QScrollBar:sub-line {border: none;}"
        QScrollBar:add-line {border: none;}"
        QScrollBar:sub-page {border: none;}"
        QScrollBar:add-page {border: none;}"
    """,
    "my_calibration": """
        QWidget {background-color: transparent; border: none;}
        QFrame#buttons {background-color: rgba(6, 34, 121, 50); border-radius: 0; border: 1px solid rgba(6, 34, 121, 255);}
        QPushButton {background-color: transparent; color: #000000; border: none; border-radius: 0}
        QPushButton:hover {background-color: rgba(6, 34, 121, 75);}
        QPushButton:pressed {background-color: rgba(6, 34, 121, 100);}
        QPushButton:checked {background-color: #FFD600;}
        QLabel {background-color: transparent;}
    """,
    "calibration_tabs": """
        QTabWidget {background-color: rgba(6, 34, 121, 0); border: none;}
    """,
    "reference_data_tab": """
        QWidget {background-color: %s; border: none;}
        QScrollBar:handle {background-color: rgba(6, 34, 121, 50);}
        QScrollBar:handle:hover {background-color: rgba(6, 34, 121, 100);}
        QScrollBar:vertical {width: 10px; border: none; border-radius: 5px;}
        QScrollBar:horizontal {height: 10px; border: none; border-radius: 5px;}
        QScrollBar:sub-line {border: none;}
        QScrollBar:add-line {border: none;}
        QScrollBar:sub-page {border: none;}
        QScrollBar:add-page {border: none;}
        QTableView {background: transparent; border: 1px solid #062279;}
        QHeaderView {background: rgba(6, 34, 121, 0);}
        QHeaderView:section {padding: 2px 4px;}
        QComboBox {background-color: white; border: 1px solid #062279; border-radius: 15px; selection-background-color: rgba(6, 34, 121, 50); padding-left: 10;}
        QComboBox:down-arrow {image: url(%s); width: 20px;}
        QComboBox:drop-down:button {border: none; width: 20px; padding-right: 5px}
    """ % (MAIN_BACKGROUND_COLOR, arrow_down_icon_path),
    "model_tab": """
        QWidget {background-color: %s; border: none;}
        QScrollBar:handle {background-color: rgba(6, 34, 121, 50);}
        QScrollBar:handle:hover {background-color: rgba(6, 34, 121, 100);}
        QScrollBar:vertical {width: 10px; border: none; border-radius: 5px;}
        QScrollBar:horizontal {height: 10px; border: none; border-radius: 5px;}
        QScrollBar:sub-line {border: none;}
        QScrollBar:add-line {border: none;}
        QScrollBar:sub-page {border: none;}
        QScrollBar:add-page {border: none;}
        QTableView {background: transparent; border: 1px solid #062279;}
        QHeaderView {background: transparent;}
        QHeaderView:section {padding: 2px 4px;}
        QComboBox {background-color: white; border: 1px solid #062279; border-radius: 15px; selection-background-color: rgba(6, 34, 121, 50); padding-left: 10;}
        QComboBox:down-arrow {image: url(%s); width: 20px;}
        QComboBox:drop-down:button {border: none; width: 20px; padding-right: 5px}
        QRadioButton:indicator {width: 15px; height: 15px;}
        QRadioButton:indicator::unchecked {image: url(%s);}
        QRadioButton:indicator:unchecked:hover {image: url(%s);}
        QRadioButton:indicator:unchecked:pressed {image: url(%s);}
        QRadioButton:indicator::checked {image: url(%s);}
        QRadioButton:indicator:checked:hover {image: url(%s);}
        QRadioButton:indicator:checked:pressed {image: url(%s);}
    """ % (MAIN_BACKGROUND_COLOR, arrow_down_icon_path, radio_button_unchecked_path,
            radio_button_unchecked_hovered_path, radio_button_unchecked_pressed_path,
            radio_button_checked_path, radio_button_checked_hovered_path, radio_button_checked_pressed_path),
    "header": """
        QWidget#search_bar {background-color: white; border-radius: 20;}
        QLabel {background-color: transparent;}
        QPushButton#navigation {background-color: transparent; border: none;}
    """,
    "modal_1": """
        QWidget {background-color: %s; color: #062279;}
        QPushButton {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #EAEAEA); border-radius: 5; border: 1px solid #062279; padding: 5 10;}
        QPushButton:hover {background-color: #D5E8EE;}
        QPushButton:pressed {background-color: #CADCE2;}
        QLineEdit {background-color: white; border: 1px solid #062279; padding: 5; width: 500}
        QLabel {background-color: transparent;}
        QLabel#message {font-size: 11pt;}
        QLabel#explanation {color: #067934; font-size: 9pt;}
    """ % MAIN_BACKGROUND_COLOR,
}
