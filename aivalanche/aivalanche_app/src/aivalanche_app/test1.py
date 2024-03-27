import numpy as np, sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView
import pyqtgraph as pg

class HeatmapWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create random 2D data for heatmap
        data = np.random.rand(100, 100)  # Example 100x100 grid with random values

        # Create a GraphicsView to display the heatmap
        self.view = pg.GraphicsView()
        self.setCentralWidget(self.view)

        # Create a PlotItem and add it to the view
        self.plot_item = pg.PlotItem()
        self.view.setCentralItem(self.plot_item)

        # Create an ImageItem to display the heatmap
        self.image_item = pg.ImageItem()
        self.plot_item.addItem(self.image_item)

        # Set colormap (optional)
        # self.image_item.setLookupTable(pg.colorMaps['viridis'])

        # Set data for the ImageItem
        self.image_item.setImage(data)

def main():
    # Create the application
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # Create the main window
    window = HeatmapWindow()
    window.show()

    # Start the event loop
    app.exec()

if __name__ == "__main__":
    main()
