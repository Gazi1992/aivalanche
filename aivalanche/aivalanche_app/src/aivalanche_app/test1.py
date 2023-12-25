import pandas as pd
import sys
from copy import deepcopy
from PySide6.QtWidgets import QComboBox, QLineEdit, QApplication, QTableView, QStyledItemDelegate, QHeaderView, QStyle, QStyleOption, QCheckBox, QAbstractItemView, QTextEdit, QStyleOptionViewItem
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QRect, QItemSelection, QItemSelectionModel, QEvent
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QFont, QLinearGradient, QPen, QMouseEvent, QStandardItemModel, QStandardItem
from aivalanche_app.resources.themes.style import style
from aivalanche_app.paths import ascending_icon_path, descending_icon_path, checkbox_checked_path, checkbox_unchecked_path


class CustomComboBoxDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() in [2, 4]:  # Specify columns where you want comboboxes
            combo = QComboBox(parent)
            combo.addItems(["Option 1", "Option 2", "Option 3"])  # Customize this list with your combobox options
            return combo
        return super().createEditor(parent, option, index)

class CustomComboBoxModel(QStandardItemModel):
    def __init__(self, data=None, checkbox_columns=None):
        super().__init__()

        self.initialize_table(data, checkbox_columns)

    def initialize_table(self, data=None, checkbox_columns=None):
        self.setColumnCount(len(data.columns))
        self.setRowCount(len(data))

        for row in range(len(data)):
            for col in range(len(data.columns)):
                item = QStandardItem(data.iloc[row, col])
                self.setItem(row, col, item)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self.itemFromIndex(index).setText(str(value))
            return True
        return super().setData(index, value, role)

class custom_table(QTableView):
    def __init__(self, data=None, style=None):
        super().__init__()

        # Set custom combobox delegate for all columns
        delegate = CustomComboBoxDelegate(self)
        self.setItemDelegate(delegate)

        # Set header options
        self.horizontalHeader().setStretchLastSection(True)  # Make columns stretch to the full width
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Create the custom model
        self.setModel(CustomComboBoxModel(data))

# Example usage:
data = pd.DataFrame({'Column1': ['Option 1', 'Option 2', 'Option 3'],
                     'Column2': ['Value 1', 'Value 2', 'Value 3'],
                     'Column3': ['Option 1', 'Option 2', 'Option 3']})

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()
    
table = custom_table(data)
table.show()

app.exec_()

