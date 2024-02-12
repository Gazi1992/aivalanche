import pyqtgraph as pg, numpy as np
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QTableWidget, QSplitter, QFileDialog, QScrollArea
from aivalanche_app.components.custom_layouts import h_layout, v_layout
from aivalanche_app.components.custom_checkbox import custom_checkbox
from aivalanche_app.data_store.store import store
from aivalanche_app.paths import upload_icon_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.components.plots.line_scatter_plot import line_scatter_plot
from aivalanche_app.resources.themes.style import style
from aivalanche_app.components.custom_table import custom_table
from reference_data import Reference_data
from PySide6.QtCore import Qt


# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', (0, 0, 0, 0))
pg.setConfigOption('foreground', 'k')

class reference_data_tab(QSplitter):
    
    def __init__(self, parent = None, store: store = None, style: style = None):
        super().__init__(parent)
        
        self.store = store
        self.style = style
        
        self.reference_data_file = None
        self.reference_data = None
        
        # Set invisible splitter handle
        self.setHandleWidth(0)
        
        # Create left widget
        left_widget = QWidget(self)
        left_layout = v_layout(spacing = 20)
        left_widget.setLayout(left_layout)
        
        # Create load data layout
        load_data_layout = h_layout(spacing = 10)
        
        # Create drop-down widget
        self.drop_down_widget = QComboBox(parent = self)
        self.drop_down_widget.setFixedHeight(30)
        self.drop_down_widget.currentTextChanged.connect(lambda text: self.load_reference_data(text))
        load_data_layout.addWidget(self.drop_down_widget, 1)
        
        # Create load data button
        load_data_button = icon_text_button(parent = self, icon_path = upload_icon_path, icon_height = 25, on_click = self.on_load_data_button_click)
        load_data_layout.addWidget(load_data_button, 0)
        
        left_layout.addLayout(load_data_layout)
        
        # # Add custom checkbox - test
        # checkbox = custom_checkbox(on_click = lambda x: print(x))
        # left_layout.addWidget(checkbox)
        
        # Create table
        self.table = custom_table(style = self.style,
                                  on_checkbox_click = self.on_checkbox_click,
                                  on_header_checkbox_click = self.on_header_checkbox_click)
        left_layout.addWidget(self.table)
        
        # Create right layout, where plots will be shown
        right_widget = QWidget(self)
        right_layout = v_layout(spacing = 20)
        right_widget.setLayout(right_layout)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(scroll_area)
        
        # Create a grid layout with 100 rows and 2 columns
        frame = pg.GraphicsLayoutWidget()
        frame.setFixedHeight(10*500)
        
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
                
        # Example data for each plot
        data_sets = [(np.random.rand(100), np.random.rand(100)) for _ in range(20)]
        
        # Create and add scatter plots to the grid layout
        for i in range(20):
            custom_plot =  line_scatter_plot(data_x=data_sets[i][0], data_y=data_sets[i][1], title=f"Custom Plot {i}")
            custom_plot.setContentsMargins(10, 10, 10, 10)
            custom_plot.setMinimumHeight(500)        
            frame.addItem(custom_plot, row=i // 2, col=i % 2)

        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        
    def toggle_log_y(self, plot_item, label):
        plot_item.setLogMode(y=label.text() == "log_Y")
        label.setText("linear" if label.text() == "log_Y" else "log_Y")

        
    def on_load_data_button_click(self):
        response = QFileDialog.getOpenFileName(parent = self, caption = 'Select reference data file', filter = 'Json file (*.json)')
        if len(response[0]) > 0:
            ref_data_file = response[0]
            if ref_data_file != self.reference_data_file:
                self.drop_down_widget.addItem(ref_data_file)
                self.drop_down_widget.setCurrentText(ref_data_file)
            

    def load_reference_data(self, file):
        self.reference_data = Reference_data(file)
        self.reference_data.data.insert(0, 'include', True)
        self.reference_data.data['plot'] = False
        self.reference_data.data['calibrate'] = True
        self.table.update_data(self.reference_data.data)
        
    
    def on_checkbox_click(self, data: dict = None):
        print(data)
        
    def on_header_checkbox_click(self, data: dict = None):
        print(data)
