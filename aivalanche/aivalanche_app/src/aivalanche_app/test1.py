import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
from pyqtgraph import GraphicsLayout, GraphicsWidget

class PlotManager:
    def __init__(self, graphics_view):
        self.graphics_view = graphics_view
        self.graphics_layout = GraphicsLayout()
        self.graphics_widget = GraphicsWidget()
        self.graphics_widget.setLayout(QVBoxLayout())
        self.graphics_widget.layout.addWidget(self.graphics_layout)
        self.graphics_view.setCentralItem(self.graphics_widget)

    def add_plot(self):
        # Create a new plot and add it to the GraphicsLayoutWidget
        plot = self.graphics_layout.addPlot(title=f"Plot {len(self.graphics_layout.items)}")
        # Set minimum height for each plot
        plot.setMinimumHeight(500)
        # Adjust the layout to fit the new plot
        self.adjust_layout()

    def adjust_layout(self):
        # Calculate the number of rows and columns based on the number of plots
        num_plots = len(self.graphics_layout.items)
        num_columns = min(num_plots, 2)  # Two columns
        num_rows = (num_plots + 1) // 2  # Add 1 to round up for odd numbers

        # Set the layout of the GraphicsLayoutWidget
        self.graphics_layout.layout.setContentsMargins(0, 0, 0, 0)
        self.graphics_layout.layout.setVerticalSpacing(10)  # Set vertical spacing between plots

        # Set the layout of the QGraphicsView
        scene_rect = QtGui.QRectF(0, 0, self.graphics_layout.width(), num_rows * 500)
        self.graphics_widget.setGeometry(scene_rect.toRect())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Button to add plots
        self.button = QPushButton("Add Plot")
        self.button.clicked.connect(self.add_plot)
        self.layout.addWidget(self.button)

        # GraphicsView to contain the GraphicsLayoutWidget
        self.graphics_view = pg.GraphicsView()
        self.layout.addWidget(self.graphics_view)

        # Initialize the PlotManager
        self.plot_manager = PlotManager(self.graphics_view)

    def add_plot(self):
        # Call the PlotManager to add a new plot
        self.plot_manager.add_plot()

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()    
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

main()
