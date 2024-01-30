import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableView, QCheckBox, QStyledItemDelegate
from PySide6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PySide6.QtGui import QColor
import numpy as np
import pandas as pd

class item_delegate(QStyledItemDelegate):
    
    def __init__(self, parent):
        
        super().__init__(parent)
        
        # Define checkbox icon dimension
        self.checkbox_width = 16
        self.checkbox_height = 16
        self.alternate_row_background_color = QColor(0, 0, 0, 25)
        
    
    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = QCheckBox(parent)
            editor.setChecked(index.data(Qt.EditRole))
            return editor
        return super().createEditor(parent, option, index)
    

    def setEditorData(self, editor, index):
        if index.column() == 0:
            editor.setChecked(index.data(Qt.EditRole))
        else:
            super().setEditorData(editor, index)

    
    def setModelData(self, editor, model, index):
        if index.column() == 0:
            model.setData(index, editor.isChecked(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    
    def paint(self, painter, option, index):
        rect = option.rect    
       
        super().paint(painter, option, index)            
        
        # Set background color
        if index.row() % 2 == 1:
            painter.fillRect(rect, self.alternate_row_background_color)
            

class custom_table_model(QAbstractTableModel):
    def __init__(self, data = None):
        super().__init__()
        
        if data is None:
            data = pd.DataFrame()
            
        self._data = data
                
    def flags(self, index):
        flags = super().flags(index)
        flags |= Qt.ItemIsEditable
        return flags
        
    
    def rowCount(self, parent = QModelIndex()):
        return len(self._data)


    def columnCount(self, parent = QModelIndex()):
        return len(self._data.columns)


    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            result = self._data.iloc[index.row(), index.column()]
            if not isinstance(result, (bool, np.bool_)):
                result = str(result)
            else:
                result = bool(result)
            return result
        return None

    
    def setData(self, index, value, role = Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            return True
        return super().setData(index, value, role)


    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None
    

class custom_table(QTableView):
    def __init__(self, data = None):       
        super().__init__()
        
        # Init data
        self.initialize_data()
        
        # Set model
        self.setModel(custom_table_model(self.data))

        # Set item delegate
        self.setItemDelegate(item_delegate(parent = self))
        
        
    def initialize_data(self):
        self.data = pd.DataFrame({
                        'include': [True, True, True, True],
                        'x': [1, 12, 50, 65],
                        'animal': ['dog', 'cat', 'cow', 'horse']
                        })    
                

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Minimal PySide6 Example")

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create the drawer widget and add it to the layout
        table = custom_table()
        layout.addWidget(table)
        

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()    
    
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

main()
