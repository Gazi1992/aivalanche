from aivalanche_app.paths import arrow_down_icon_path

MAIN_BACKGROUND_COLOR = '#f2faff'

THEME = {
    "home": """
        QWidget { background-color: %s; color: #062279 }
    """ % MAIN_BACKGROUND_COLOR,
    "drawer": """
        QFrame {background-color: white; }
        QPushButton { background-color: transparent; color: #000000; border: none; }
        QPushButton:hover { background-color: #D9D9D9; }
        QPushButton:pressed { background-color: #C9C9C9; }
        QPushButton:checked { background-color: #BAF0F8; }
        QLabel { background-color: transparent; }
    """,
    "main_tabs": """
        QWidget { border: none; }
        QScrollBar:handle { background-color: rgba(6, 34, 121, 50); }
        QScrollBar:handle:hover { background-color: rgba(6, 34, 121, 100); }
        QScrollBar:vertical { width: 10px; border: none; border-radius: 5px; }
        QScrollBar:horizontal {height: 10px; border: none; border-radius: 5px; }
        QScrollBar:sub-line { border: none; }",
        QScrollBar:add-line { border: none; }",
        QScrollBar:sub-page { border: none; }",
        QScrollBar:add-page { border: none; }"
    """,
    "new_project_button": """
        QPushButton { background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #E0F4FB); border: 1px solid #062279; }
        QPushButton:hover { background-color: #D5E8EE; }
        QPushButton:pressed { background-color: #CADCE2; }
        QLabel { background-color: transparent; }
    """,
    "new_model_button": """
        QPushButton { background-color: #E0F4FB; border: 1px solid #062279; }
        QPushButton:hover { background-color: #D5E8EE; }
        QPushButton:pressed { background-color: #CADCE2; }
        QLabel { background-color: transparent; }
    """,
    "modal_1": """
        QPushButton { background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #EAEAEA); border-radius: 5; border: 1px solid #062279; padding: 5 10; }
        QPushButton:hover { background-color: #D5E8EE; }
        QPushButton:pressed { background-color: #CADCE2; }
        QLineEdit { background-color: white; border: 1px solid #062279; padding: 5; width: 500}
        QLabel { background-color: transparent; }
        QLabel#message { font-size: 11pt; }
        QLabel#explanation { color: #067934; font-size: 9pt; }
    """,
    "calibration_tabs": """
        QWidget { border: none; }
        QFrame#buttons { background-color: rgba(6, 34, 121, 50); border-radius: 0; border: 1px solid rgba(6, 34, 121, 255); }
        QScrollBar:handle { background-color: rgba(6, 34, 121, 50); }
        QScrollBar:handle:hover { background-color: rgba(6, 34, 121, 100); }
        QScrollBar:vertical { width: 10px; border: none; border-radius: 5px; }
        QScrollBar:horizontal {height: 10px; border: none; border-radius: 5px; }
        QScrollBar:sub-line { border: none; }
        QScrollBar:add-line { border: none; }
        QScrollBar:sub-page { border: none; }
        QScrollBar:add-page { border: none; }
        QPushButton { background-color: transparent; color: #000000; border: none; border-radius: 0 }
        QPushButton:hover { background-color: rgba(6, 34, 121, 75); }
        QPushButton:pressed { background-color: rgba(6, 34, 121, 100); }
        QPushButton:checked { background-color: #FFD600; }
        QLabel { background-color: transparent; }
        QComboBox { background-color: white; border: 1px solid #062279; border-radius: 15px; selection-background-color: rgba(6, 34, 121, 50); padding-left: 10; }
        QComboBox:down-arrow { image: url(%s); width: 20px; }
        QComboBox:drop-down:button { border: none; width: 20px; padding-right: 5px }
        QTableView { background: transparent; border: 1px solid #062279;}
        QHeaderView:section { padding: 2px 4px; }
    """ % arrow_down_icon_path,
    "header": """
        QWidget#search_bar { background-color: white; border-radius: 20; }
        QPushButton#navigation { background-color: transparent; border: none; }
    """,
}
