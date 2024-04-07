from aivalanche_app.paths import arrow_down_icon_path, radio_button_checked_path, radio_button_checked_hovered_path, \
                                 radio_button_checked_pressed_path, radio_button_unchecked_path, radio_button_unchecked_hovered_path, \
                                 radio_button_unchecked_pressed_path, checkbox_checked_path, checkbox_checked_hovered_path, checkbox_checked_pressed_path, \
                                 checkbox_unchecked_path, checkbox_unchecked_hovered_path, checkbox_unchecked_pressed_path

font_sizes = {'normal': 14, 'small': 12, 'large': 16, 'huge': 18, 'tiny': 10}

colors = {
    "background_1": "#f2faff",
    "background_2": "#e0f4fb",
    "text": "#062279",
    
    "drawer_background": "#ffffff",
    "drawer_button_hover": "#d9d9d9",
    "drawer_button_press": "#c9c9c9",
    "drawer_button_check": "#baf0f8",    
    
    "selection": "#ffffff",
    "selection_background": "#e95420",

    "calibration_header_button_checked": "#ffb800",
    
    "button_hover": "rgba(6, 34, 121, 50)",
    "button_press": "rgba(6, 34, 121, 125)",
    
    "scrollbar_handle": "rgba(6, 34, 121, 50)",
    "scrollbar_handle_hover": "rgba(6, 34, 121, 125)",

    "header_section_color_1": "#f2faff",
    "header_section_color_2": "#e0f4fb",
    "header_section_border": "rgba(6, 34, 121, 170)",
    
    "line_edit_background": "#ffffff",
    "line_edit_border": "rgba(6, 34, 121, 170)",
    
    "combo_box_background": "#ffffff",
    "combo_box_border": "#062279",
    "combo_box_selection": "rgba(6, 34, 121, 50)",
    
    "table_background": "#f2faff",
    "table_border": "#062279",
    "table_even_rows": "rgba(6, 34, 121, 20)",
    "table_gridline": "rgba(6, 34, 121, 50)",
    
    "modal_button_color_1": "#f2faff",
    "modal_button_color_2": "#e0f4fb",
    "modal_button_border": "rgba(6, 34, 121, 170)",
    
    "button_1_color_1": "#f2faff",
    "button_1_color_2": "#e0f4fb",
    "button_1_border": "rgba(6, 34, 121, 170)",
    
    "progress_bar_background": "rgba(6, 34, 121, 20)",
    "progress_bar_chunk": "#339313",
    
    "error_text": "#ff0000",
    
    "plot_colors": ["#0075FF", "#FF5C00", "#19B100", "#EB00FF", "#FFD600"],
    "plot_text": "#062279",
    "plot_axis": "#062279",
    "plot_legend_background": "#06227914",
    "plot_legend_text": "#062279",
    "plot_grid": "#062279",
}

stylesheet = f"""
    QWidget {{background-color: transparent; border: none;}}
    QFrame {{background-color: transparent; border: none;}}
    QSplitter {{background-color: transparent; border: none;}}
    QSplitter::handle {{width: 0px; height: 0px;}}
    QStackedWidget {{background-color: transparent; border: none;}}
    QTabWidget {{background-color: transparent; border: none;}}
    QScrollArea {{background-color: transparent; border: none;}}
    
    QScrollBar:handle {{background-color: rgba(6, 34, 121, 50);}}
    QScrollBar:handle:hover {{background-color: rgba(6, 34, 121, 100);}}
    QScrollBar:vertical {{width: 10px; border: none; border-radius: 5px;}}
    QScrollBar:horizontal {{height: 10px; border: none; border-radius: 5px;}}
    QScrollBar:sub-line {{border: none;}}
    QScrollBar:add-line {{border: none;}}
    QScrollBar:sub-page {{border: none;}}
    QScrollBar:add-page {{border: none;}}
    
    QMenu {{background-color: {colors['background_1']}; color: {colors['text']};}}
    QLabel {{
        background-color: transparent;
        border: none;
        color: {colors['text']};
        }}
    QDialog {{min-width: 500px; background-color: {colors['background_1']};}}
    
    /* Button */
    QPushButton:hover {{background: {colors['button_hover']};}}
    QPushButton:pressed {{background: {colors['button_press']};}}
    QDialog QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['modal_button_color_1']}, stop:1 {colors['modal_button_color_2']});
        border: 1px solid {colors['modal_button_border']};
        padding: 5px;
        }} 
    
    /* Line edit */
    QLineEdit {{
        background: {colors['line_edit_background']};
        border: 1px solid {colors['line_edit_border']};
        padding: 5px;
        color: {colors['text']};
        selection-color: {colors['selection']};
        selection-background-color: {colors['selection_background']};
        }}
                                                     
    /* Table view */
    QTableView {{
        background: {colors['table_background']};
        border: 1px solid {colors['table_border']};
        color: {colors['text']};
        gridline-color: {colors['table_gridline']};
        }}
    QTableCornerButton::section {{
        background: {colors['table_background']};
        border-width: 0px 1px 1px 0px;
        border-style: solid;
        border-color: {colors['header_section_border']};
        }}
    
    /* Header view */
    QHeaderView {{background: {colors['background_1']}; color: {colors['text']}}}
    QHeaderView:section:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {colors['header_section_color_1']}, stop:1 {colors['header_section_color_2']});
        border-width: 0px 1px 1px 0px;
        border-style: solid;
        border-color: rgba(6, 34, 121, 170);
        padding: 2px 4px;
        }}
    QHeaderView:section:vertical {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['header_section_color_1']}, stop:1 {colors['header_section_color_2']});
        border-width: 0px 1px 1px 0px;
        border-style: solid;
        border-color: rgba(6, 34, 121, 170);
        padding: 2px 4px;
        }}
    
    /* Combo box */
    QComboBox {{
        background-color: {colors['combo_box_background']};
        border: 1px solid {colors['combo_box_border']};
        color: {colors['text']};
        padding: 5px;
        }}
    QComboBox:down-arrow {{image: url({arrow_down_icon_path}); width: 20px;}}
    QComboBox:drop-down:button {{border: none; width: 20px; padding-right: 5px}}
    
    /* Radio button */
    QRadioButton:indicator {{width: 15px; height: 15px;}}
    QRadioButton:indicator::unchecked {{image: url({radio_button_unchecked_path});}}
    QRadioButton:indicator:unchecked:hover {{image: url({radio_button_unchecked_hovered_path});}}
    QRadioButton:indicator:unchecked:pressed {{image: url({radio_button_unchecked_pressed_path});}}
    QRadioButton:indicator::checked {{image: url({radio_button_checked_path});}}
    QRadioButton:indicator:checked:hover {{image: url({radio_button_checked_hovered_path});}}
    QRadioButton:indicator:checked:pressed {{image: url({radio_button_checked_pressed_path});}}
    
    /* Checkbox */
    QCheckBox:indicator {{width: 15px; height: 15px;}}
    QCheckBox:indicator::unchecked {{image: url({checkbox_unchecked_path});}}
    QCheckBox:indicator:unchecked:hover {{image: url({checkbox_unchecked_hovered_path});}}
    QCheckBox:indicator:unchecked:pressed {{image: url({checkbox_unchecked_pressed_path});}}
    QCheckBox:indicator::checked {{image: url({checkbox_checked_path});}}
    QCheckBox:indicator:checked:hover {{image: url({checkbox_checked_hovered_path});}}
    QCheckBox:indicator:checked:pressed {{image: url({checkbox_checked_pressed_path});}}
    
    /* Progress bar */
    QProgressBar {{background-color: {colors['progress_bar_background']};}}
    QProgressBar:chunk {{background-color: {colors['progress_bar_chunk']};}}
    
    /* Main window */
    QWidget#main_window {{background-color: {colors['background_1']};}}
    
    /* Drawer */
    QFrame#drawer {{background-color: {colors['drawer_background']};}}
    QPushButton#drawer_button:hover {{background-color: {colors['drawer_button_hover']};}}
    QPushButton#drawer_button:pressed {{background-color: {colors['drawer_button_press']};}}
    QPushButton#drawer_button:checked {{background-color: {colors['drawer_button_check']};}}

    /* New project card */
    QPushButton#new_project {{background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #E0F4FB); border: 1px solid #062279;}}
    QPushButton#new_project:hover {{background-color: #d5e8ee;}}
    QPushButton#new_project:pressed {{background-color: #cadce2;}}
    
    /* New model card */
    QPushButton#new_model {{background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #E0F4FB); border: 1px solid #062279;}}
    QPushButton#new_model:hover {{background-color: #d5e8ee;}}
    QPushButton#new_model:pressed {{background-color: #cadce2;}}
    
    /* Navigation header */
    QPushButton#navigation_header:hover {{background-color: transparent;}}
    QPushButton#navigation_header:pressed {{background-color: transparent;}}
    QLabel#navigation_header:hover {{color: #ff0000;}}
    QLabel#navigation_header:pressed {{color: #ff00ff;}}
    
    /* Search bar */
    QWidget#search_bar {{background-color: white; border-radius: 20px;}}
    QLineEdit#search_bar {{background: transparent; border: none;}}

    /* Modal */
    QWidget#modal {{background-color: {colors['background_1']}; color: {colors['text']};}}
    QLineEdit#modal {{min-width: 500px;}}
    QLabel#modal_message {{font-size: 11pt;}}
    QLabel#modal_explanation {{color: #067934; font-size: 9pt;}}
    
    /* Calibration header */
    QFrame#calibration_header_frame {{background-color: white;}}
    QPushButton#calibration_header_button:checked {{background-color: {colors['calibration_header_button_checked']};}}
    
    /* Parameters tab button */
    QPushButton#parameters_tab, QPushButton#log_in_button {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['button_1_color_1']}, stop:1 {colors['button_1_color_2']});
        border: 1px solid {colors['button_1_border']};
        }} 
    QPushButton#parameters_tab:hover, QPushButton#log_in_button:hover {{background: {colors['button_hover']};}}
    QPushButton#parameters_tab:pressed, QPushButton#log_in_button:pressed {{background: {colors['button_press']};}}
    
    /* Calibration control buttons */
    QPushButton#calibration_control {{icon-size: 30px 30px;}}
    QPushButton#calibration_control:hover {{background-color: transparent;}}
    QPushButton#calibration_control:pressed {{background-color: transparent;}}
    
    /* Round combo box */
    QComboBox#round_combo_box {{border-radius: 15px; padding-left: 10px; height: 20px;}}
    
    /* Loss card */
    QFrame#loss_card {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['button_1_color_1']}, stop:1 {colors['button_1_color_2']});
        border: 1px solid {colors['button_1_border']};
        padding: 10px;
        }}
    QPushButton#add_loss_card_button {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['button_1_color_1']}, stop:1 {colors['button_1_color_2']});
        border: 1px solid {colors['button_1_border']};
        }}
    QPushButton#add_loss_card_button:hover {{background: {colors['button_hover']};}}
    QPushButton#add_loss_card_button:pressed {{background: {colors['button_press']};}}
    
    /* Add group type */
    QPushButton#add_group_type {{icon-size: 25px 25px;}}
    QPushButton#add_group_type:hover {{background-color: transparent;}}
    QPushButton#add_group_type:pressed {{background-color: transparent;}}
    
    /* Error label */
    QLabel#error {{color: {colors['error_text']}; padding-left: 50px; padding-right: 50px; }}
"""