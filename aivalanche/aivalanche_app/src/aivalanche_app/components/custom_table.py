import pandas as pd
from PySide6.QtWidgets import QTableView, QStyledItemDelegate, QHeaderView, QStyle, QStyleOption, QCheckBox, QAbstractItemView, QTextEdit
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QRect
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush
from aivalanche_app.resources.themes.style import style
from aivalanche_app.paths import ascending_icon_path, descending_icon_path, arrow_down_icon_path       

class CustomHeader(QHeaderView):
    def paintSection(self, painter, rect, logicalIndex):
        # painter.save()

        # # Get the section text
        # section_text = self.model().headerData(logicalIndex, Qt.Horizontal)

        # if section_text == 'include':
        #     # Draw a checkbox next to the header text
        #     checkbox = QCheckBox(self)
        #     checkbox.setGeometry(rect.left(), rect.top(), 20, rect.height())
        #     checkbox.setChecked(True)
        #     checkbox.show()

        #     # Adjust the text rect to the right of the checkbox
        #     text_rect = rect.adjusted(25, 0, 0, 0)
        #     super(CustomHeader, self).paintSection(painter, text_rect, logicalIndex)
        # else:
        #     # Draw the section text as usual
        #     super(CustomHeader, self).paintSection(painter, rect, logicalIndex)

        # painter.restore()
        
        painter.save()

        # Custom background gradient for the header
        gradient = QBrush(QColor(100, 100, 255))
        painter.fillRect(rect, gradient)
        
        # Set font for header text
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        
        # Determine section text
        text = self.model().headerData(logicalIndex, Qt.Horizontal)
        
        if text == 'include':
            # Draw a checkbox if the section text is 'include'
            checkbox = QCheckBox(self)
            checkbox.setGeometry(rect.right() - 30, rect.top(), 30, rect.height())
            checkbox.setChecked(True)
            checkbox.setStyleSheet("QCheckBox::indicator {width: 20px; height: 20px;}")
            checkbox.show()
            
            # Adjust the rectangle for the header text
            rect.setRight(rect.right() - 30)
        
        # Draw the header text
        painter.drawText(rect.adjusted(10, 0, -10, 0), Qt.AlignLeft | Qt.AlignVCenter, text)
        
        painter.restore()
        

class custom_table_model(QAbstractTableModel):
    def __init__(self, data = None, default_nr_col = 6, default_nr_row = 10):
        super().__init__()
        if data is None:#
            empty_columns = [f'{i+1}' for i in range(default_nr_col)] 
            data = pd.DataFrame(columns = empty_columns, data = [[''] * default_nr_col for _ in range(default_nr_row)])
        self._data = data

    def rowCount(self, parent = QModelIndex()):
        return len(self._data)

    def columnCount(self, parent = QModelIndex()):
        return len(self._data.columns)

    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None


class custom_table(QTableView):
    def __init__(self, data = None, style: style = None):       
        super().__init__()
        self.setModel(custom_table_model(data))
        self.setHorizontalHeader(CustomHeader(Qt.Horizontal, self))
        self.horizontalHeader().setStretchLastSection(True)  # Make columns stretch to the full width
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

    
    def update_data(self, data):
        self.model()._data = data
        self.model().layoutChanged.emit()