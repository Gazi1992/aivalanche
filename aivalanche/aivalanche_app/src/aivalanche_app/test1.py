import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
from pyqtgraph import GraphicsLayout, GraphicsWidget

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

# Create a GraphicsLayoutWidget
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('PyQtGraph Example')

# Create some sample data
x = [1, 2, 3, 4, 5]
y = [2, 4, 1, 7, 3]

# Create plots at various positions
plot_00 = win.addPlot(row=0, col=0, title="Plot (0, 0)")
plot_00.plot(x, y)

plot_10 = win.addPlot(row=1, col=0, title="Plot (1, 0)")
plot_10.plot(x, [i * 2 for i in y])

plot_01 = win.addPlot(row=0, col=1, title="Plot (0, 1)")
plot_01.plot(x, [i * 3 for i in y])

plot_11 = win.addPlot(row=1, col=1, title="Plot (1, 1)")
plot_11.plot(x, [i * 4 for i in y])

plot_to_delete = win.getItem(0,1)

if plot_to_delete:
    # Find the plots at (1, 0) and (1, 1)
    plot_10 = win.getItem(1,0)
    plot_11 = win.getItem(1,1)

    # Move the plots to rearrange the layout
    if plot_10:
        win.removeItem(plot_10)
        win.addItem(plot_10, row=0, col=1)

    if plot_11:
        win.removeItem(plot_11)
        win.addItem(plot_11, row=1, col=0)

    # Delete the plot at (0, 1)
    win.removeItem(plot_to_delete)

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()    
win.show()
app.exec_()

