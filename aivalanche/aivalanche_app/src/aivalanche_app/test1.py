import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QScrollArea
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableView, QCheckBox, QStyledItemDelegate
import numpy as np
import sys

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create a scroll area
        scroll_area = QScrollArea()
        central_widget.layout().addWidget(scroll_area)

        # Create a widget to contain the GraphicsLayoutWidget
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        # Create a grid layout with 100 rows and 2 columns
        grid_layout = pg.GraphicsLayoutWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)
        
        # Wrap the GraphicsLayoutWidget in a QWidget
        wrapper_widget = QWidget()
        wrapper_layout = QVBoxLayout(wrapper_widget)
        wrapper_layout.addWidget(grid_layout)
        scroll_content_layout.addWidget(wrapper_widget)

        # Example data for each plot
        data_sets = [
            (np.random.rand(100), np.random.rand(100)) for _ in range(100)
        ]

        # Create and add scatter plots to the grid layout
        for i in range(100):
            plot_item = grid_layout.addPlot(row=i // 2, col=i % 2)

            # Get the ViewBox associated with the PlotItem
            view_box = plot_item.getViewBox()

            # Set the background color of the ViewBox to be transparent
            view_box.setBackgroundColor('w')  # 'w' stands for white; you can use 'w' for white or (0, 0, 0, 0) for transparent

            # Set a fixed height for each plot (minimum height of 200 pixels)
            plot_item.setMaximumHeight(200)

            scatter_plot = pg.ScatterPlotItem(x=data_sets[i][0], y=data_sets[i][1], size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0, 120))
            plot_item.addItem(scatter_plot)

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()    
    
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())

main()
