import pandas as pd
from copy import deepcopy
from PySide6.QtWidgets import QTableView, QStyledItemDelegate, QHeaderView, QStyle, QStyleOption, QCheckBox, QAbstractItemView, QTextEdit
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QRect, QItemSelection, QItemSelectionModel
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QFont, QLinearGradient, QPen, QMouseEvent
from aivalanche_app.resources.themes.style import style
from aivalanche_app.paths import ascending_icon_path, descending_icon_path, checkbox_checked_path, checkbox_unchecked_path

class table_horizontal_header(QHeaderView):
    def __init__(self, parent):
        
        super().__init__(Qt.Horizontal, parent)
        
        # Define checkbox icon dimension
        self.checkbox_width = 16
        self.checkbox_height = 16
        
        # Define filter icon dimensions
        self.filter_width = 16
        self.filter_height = 16
        
        # Define padding
        self.padding_left = 4
        self.padding_right = 4
        self.padding_between = 4

        # Set up button properties
        self.setMouseTracking(True)
        
        self.clicked_section = None
        self.hovered_section = None
        self.pressed_section = None
        self.last_entered_section = None
        
        # Checkbox rects
        self.checkbox_rects = [QRect(0, 0, 0, 0)] * self.parent().model().columnCount()

    def update_section(self, logical_index):
        if logical_index is not None:
            self.updateSection(logical_index)
        

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if self.rect().contains(event.pos()):
            if self.pressed_section is None:
                logical_index = self.logicalIndexAt(event.pos())
                if logical_index != self.hovered_section:
                    self.update_section(self.last_entered_section)
                    self.last_entered_section = logical_index
                    self.hovered_section = logical_index
                    self.update_section(self.hovered_section)
                if self.checkbox_rects[logical_index].contains(event.pos()):
                    print('checkbox hovered')


    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hovered_section = None
        self.pressed_section = None
        self.update_section(self.last_entered_section)
        self.last_entered_section = None


    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.pos()):            
                logical_index = self.logicalIndexAt(event.pos())
                self.pressed_section = logical_index
                self.update_section(self.pressed_section)
                
                # Check if it's a header section click
                if logical_index != -1:
                    # Select the entire column
                    selectionModel = self.parent().selectionModel()
                    selectionModel.select(
                        QItemSelection(self.parent().model().index(0, logical_index),
                                       self.parent().model().index(self.parent().model().rowCount() - 1, logical_index)),
                        QItemSelectionModel.ClearAndSelect
                    )

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.pos()):
                logical_index = self.logicalIndexAt(event.pos())
                if logical_index == self.pressed_section:
                    self.clicked_section = logical_index
                    self.update_section(self.clicked_section)
                else:
                    self.update_section(self.pressed_section)
            else:
                self.update_section(self.pressed_section)
            self.pressed_section = None
            self.hovered_section = None
            self.last_entered_section = None
                
                
    def paintSection(self, painter, rect, logicalIndex):        
        painter.save()
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get section text
        text = self.model().headerData(logicalIndex, Qt.Horizontal)
        
        # Get header dimensions
        self.x = rect.x()
        self.y = rect.y()
        self.width = rect.width()
        self.height = rect.height()
        
        # Check if section contains checkbox
        has_checkbox = self.model().checkbox_header[logicalIndex]
        
        # Calculate checkbox icon position
        if has_checkbox:
            checkbox_x = self.x + self.width - self.padding_right - self.checkbox_width
            checkbox_y = self.y + (self.height - self.checkbox_height) / 2
            checkbox_rect = QRect(checkbox_x, checkbox_y, self.checkbox_width, self.checkbox_height)
            self.checkbox_rects[logicalIndex] = checkbox_rect
        
        # Calculate text position
        text_x = self.x + self.padding_left
        text_y = self.y
        text_height = self.height
        if has_checkbox:
            text_width = self.width - self.padding_left - self.padding_right - self.checkbox_width - self.padding_between
        else:
            text_width = self.width - self.padding_left - self.padding_right
        text_rect = QRect(text_x, text_y, text_width, text_height)
        
        # Calculate filter icon position

        # Set font to bold if is a cell corresponding to the header is selected, otherwise normal font.
        if self.parent():
           selected_columns = {index.column() for index in self.parent().selectedIndexes()}
           
           # Determine if the column is selected
           is_selected = logicalIndex in selected_columns

           # Customize the font and appearance of the header
           font = QFont()
           font.setBold(is_selected)  # Set the font to bold if the column is selected
           painter.setFont(font)

        # Get the default pen
        default_pen = QPen(painter.pen())

        # Set the background
        gradient = QLinearGradient(rect.x(), rect.y(), rect.x(), rect.y() + rect.height())
        gradient.setColorAt(0, 'white')
        gradient.setColorAt(1, '#F3F3F3')
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)

        if self.hovered_section == logicalIndex:
            brush = QBrush(QColor(255, 0, 0, 255))
            painter.setBrush(brush)
            painter.drawRect(rect)
            
        if self.pressed_section == logicalIndex:
            brush = QBrush(QColor(0, 255, 0, 255))
            painter.setBrush(brush)
            painter.drawRect(rect)
        
        # Create a pen for the border and draw the border
        border_pen = QPen(QColor(0, 0, 0, 127))
        border_pen.setWidth(1)
        border_pen.setStyle(Qt.SolidLine)
        painter.setPen(border_pen)
        painter.drawLine(self.x, self.y, self.x, self.y + self.height)                              # Left side
        painter.drawLine(self.x, self.y + self.height, self.x + self.width, self.y + self.height)   # Bottom side
   
        # Reset pen to its default
        painter.setPen(default_pen)
            
        # Draw text
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)
        
        # Draw checkbox
        if has_checkbox:
            painter.drawPixmap(checkbox_rect, QPixmap(checkbox_checked_path))
        
        painter.restore()
        

class custom_table_model(QAbstractTableModel):
    def __init__(self, data = None, default_nr_col = 6, default_nr_row = 10, checkbox_columns = None):
        super().__init__()
        self.default_nr_col = default_nr_col
        self.default_nr_row = default_nr_row
        
        self.set_data(data)        
        self.set_checkboxes(checkbox_columns)
        
    
    def set_data(self, data = None):
        if data is None:
            empty_columns = [f'{i+1}' for i in range(self.default_nr_col)] 
            data = pd.DataFrame(columns = empty_columns, data = [[''] * self.default_nr_col for _ in range(self.default_nr_row)])
        self._data = data
    
    def set_checkboxes(self, checkbox_columns = None):
        if checkbox_columns is None:
            checkbox_columns = [{'name': 'include', 'check_all': True},
                                {'name': 'plot', 'check_all': False},
                                {'name': 'calibrate', 'check_all': True}]
        
        self.checkbox_header = []
        self.checkbox_data = []
        
        if len(checkbox_columns) == 0:
            self.checkbox_header = [False] * self.columnCount()
            self.checkbox_data = [False] * self.rowCount()
        else:
            checkbox_columns_names = [item['name'] for item in checkbox_columns]
            checkbox_columns_check_all = [item['check_all'] for item in checkbox_columns]
            for item in self._data.columns:
                if item in checkbox_columns_names:
                    self.checkbox_data.append(True)
                    self.checkbox_header.append(True if checkbox_columns_check_all[checkbox_columns_names.index(item)] else False)
                else:
                    self.checkbox_header.append(False)
                    self.checkbox_data.append(False)
                    
                    
    def rowCount(self, parent = QModelIndex()):
        return len(self._data)

    def columnCount(self, parent = QModelIndex()):
        return len(self._data.columns)

    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role = Qt.DisplayRole):
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
        self.setHorizontalHeader(table_horizontal_header(parent = self))
        self.horizontalHeader().setStretchLastSection(True)  # Make columns stretch to the full width
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)


    def update_data(self, data = None, checkbox_columns = None):
        self.model().set_data(data)
        self.model().set_checkboxes(checkbox_columns)
        self.model().layoutChanged.emit()