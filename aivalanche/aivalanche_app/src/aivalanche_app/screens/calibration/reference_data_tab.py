from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QTableWidget, QSplitter, QFileDialog, QScrollArea
from aivalanche_app.components.custom_layouts import h_layout, v_layout
from aivalanche_app.components.custom_checkbox import custom_checkbox
from aivalanche_app.data_store.store import store
from aivalanche_app.paths import upload_icon_path
from aivalanche_app.components.buttons.icon_text_button import icon_text_button
from aivalanche_app.resources.themes.style import style
from aivalanche_app.components.custom_table import custom_table
from reference_data import Reference_data
import pyqtgraph as pg
import numpy as np
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
        self.table = custom_table(style = self.style)
        left_layout.addWidget(self.table)
        
        # Create right layout, where plots will be shown
        right_widget = QWidget(self)
        right_layout = v_layout(spacing = 20)
        right_widget.setLayout(right_layout)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        right_layout.addWidget(scroll_area)
        
        # Create a widget to contain the GraphicsLayoutWidget
        scroll_widget = QWidget(self)
        scroll_layout = v_layout()
        scroll_widget.setLayout(scroll_layout)
        
        # Create a grid layout with 100 rows and 2 columns
        frame = pg.GraphicsLayoutWidget()
        
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
                
        # Example data for each plot
        data_sets = [
            (np.random.rand(100), np.random.rand(100)) for _ in range(100)
        ]
        
        # Create and add scatter plots to the grid layout
        for i in range(100):
            plot_item = frame.addPlot(row=i // 2, col=i % 2)
            plot_item.plot(x=data_sets[i][0], y=data_sets[i][1])
            plot_item.setMinimumHeight(100)
            # # plot_item.plot(x=data_sets[i][0], y=data_sets[i][1], pen=None, brush=(255, 0, 0, 120))
            # scatter_plot = pg.ScatterPlotItem(x=data_sets[i][0], y=data_sets[i][1], size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0, 120))
            # plot_item.addItem(scatter_plot)
                
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        
        
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
