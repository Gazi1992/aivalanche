import pandas as pd
import numpy as np
from PySide6.QtWidgets import QLineEdit, QTableView, QStyledItemDelegate, QHeaderView, QStyle
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QRect, QItemSelection, QItemSelectionModel
from PySide6.QtGui import QPalette, QColor, QPixmap, QPainter, QBrush, QFont, QLinearGradient, QPen, QMouseEvent
from aivalanche_app.resources.themes.style import style
from aivalanche_app.paths import ascending_icon_path, descending_icon_path, checkbox_checked_path, checkbox_unchecked_path
from aivalanche_app.components.custom_checkbox import custom_checkbox

class item_delegate(QStyledItemDelegate):
    
    def __init__(self, parent, style):
        
        super().__init__(parent)
        
        # Define checkbox icon dimension
        self.checkbox_width = 16
        self.checkbox_height = 16
        self.alternate_row_background_color = QColor(0, 0, 0, 25)
        self.style = style
    
    
    def commit_and_close_editor_checkbox(self, state):
        editor = self.sender()
        print('closing editor:', editor)
        # self.parent().model().on_checkbox_click(index)
        self.commitData.emit(editor)

        # self.closeEditor.emit(editor)
        
    
    def createEditor(self, parent, option, index):
        if self.parent().model().edit_data[index.column()]:
            editor = QLineEdit(parent = parent)
            return editor
        elif self.parent().model().checkbox_data[index.column()]:
            editor = custom_checkbox(parent = parent, state = index.data(Qt.EditRole), on_click = lambda state: self.parent().model().on_checkbox_click(state, index),
                                     checkbox_height = self.checkbox_height, checkbox_width = self.checkbox_width)
            editor.stateChanged.connect(self.commit_and_close_editor_checkbox)
            # editor.stateChanged.connect(lambda state: self.commit_and_close_editor_checkbox(state, index))
            return editor
        return super().createEditor(parent, option, index)
    

    def setEditorData(self, editor, index):
        if self.parent().model().edit_data[index.column()]:
            editor.setText(index.data(Qt.DisplayRole))
        elif self.parent().model().checkbox_data[index.column()]:
            editor.set_checked(index.data(Qt.DisplayRole))
        else:
            super().setEditorData(editor, index)

    
    def setModelData(self, editor, model, index):
        if self.parent().model().edit_data[index.column()]:
            model.setData(index, editor.text(), Qt.EditRole)
        elif self.parent().model().checkbox_data[index.column()]:
            model.setData(index, editor.checkbox_checked, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    
    def paint(self, painter, option, index):
        rect = option.rect    
        model = index.model()

        # If checkbox, then use the custom checkbox paint
        if model.checkbox_data[index.column()]:
            if option.state & QStyle.State_Selected:
                painter.fillRect(rect, QColor(self.style.MAIN_BACKGROUND_COLOR))
            editor = custom_checkbox(parent = self.parent(), state = index.data(Qt.EditRole), checkbox_height = self.checkbox_height, checkbox_width = self.checkbox_width)
            editor.paint(painter, rect)           
        else:        
            super().paint(painter, option, index)            
        
        # Set background color
        if index.row() % 2 == 1:
            painter.fillRect(rect, self.alternate_row_background_color)
            
            
    def editorEvent(self, event, model, option, index):
        if event.type() == QMouseEvent.MouseMove:
            if index.isValid():
                col = index.column()
                if model.checkbox_data[col]:
                    if index != model.last_mouse_move_index:
                        model.last_mouse_move_index = index
                        self.parent().setCurrentIndex(index)
                        self.parent().edit(index)
                        return True
                else:
                    if model.last_mouse_move_index is not None:
                        model.last_mouse_move_index = None
                        
        super().editorEvent(event, model, option, index)



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
        
        # Initialize bookkeeping variables
        self.reset_bookkeeping_variables()
        
        # Initialize rects
        self.initialize_checkbox_rects()
    
    
    def initialize_checkbox_rects(self):
        self.checkbox_rects = [QRect(-1, -1, 0, 0)] * self.parent().model().columnCount()


    def update_section(self, logical_index):
        if logical_index is not None:
            self.updateSection(logical_index)


    def reset_bookkeeping_variables(self):
        self.checkbox_hovered_section = None
        self.checkbox_pressed_section = None
        self.pressed_section = None


    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if self.checkbox_pressed_section is None and self.pressed_section is None:
            if self.rect().contains(event.pos()):
                logical_index = self.logicalIndexAt(event.pos())
                if logical_index != -1:
                    try:
                        if self.checkbox_rects[logical_index].contains(event.pos()):
                            if logical_index != self.checkbox_hovered_section:
                                self.checkbox_hovered_section = logical_index
                                self.update_section(logical_index)
                        else:
                            if self.checkbox_hovered_section is not None:
                                self.checkbox_hovered_section = None
                                self.update_section(logical_index)
                    except Exception as e:
                        print(e)


    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.checkbox_hovered_section is not None:
            temp = self.checkbox_hovered_section
            self.reset_bookkeeping_variables()
            self.update_section(temp)


    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:            
            if self.rect().contains(event.pos()):
                logical_index = self.logicalIndexAt(event.pos())   
                
                # Check if the checkbox is pressed
                if self.checkbox_rects[logical_index].contains(event.pos()):
                    self.checkbox_pressed_section = logical_index
                    self.update_section(logical_index)
                else:
                    self.pressed_section = logical_index
                    # Select the entire column
                    selectionModel = self.parent().selectionModel()
                    selectionModel.select(QItemSelection(self.parent().model().index(0, logical_index),
                                                         self.parent().model().index(self.parent().model().rowCount() - 1, logical_index)),
                                          QItemSelectionModel.ClearAndSelect)


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.pos()) and self.checkbox_pressed_section is not None:
                logical_index = self.logicalIndexAt(event.pos())
                if logical_index == self.checkbox_pressed_section and self.checkbox_rects[logical_index].contains(event.pos()):
                        self.model().on_checkbox_header_click(self.checkbox_pressed_section)
                
            temp = self.checkbox_pressed_section
            self.reset_bookkeeping_variables()
            self.update_section(temp)


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
        gradient = QLinearGradient(rect.x(), rect.y() + rect.height(), rect.x() + rect.width(), rect.y())
        gradient.setColorAt(0, 'white')
        gradient.setColorAt(1, '#F3F3F3')
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)
        
        # # Create a pen for the border and draw the border
        # border_pen = QPen(QColor(0, 0, 0, 127))
        # border_pen.setWidth(1)
        # border_pen.setStyle(Qt.SolidLine)
        # painter.setPen(border_pen)
        # painter.drawLine(self.x, self.y, self.x, self.y + self.height)                              # Left side
        # painter.drawLine(self.x, self.y + self.height, self.x + self.width, self.y + self.height)   # Bottom side
   
        # Reset pen to its default
        painter.setPen(default_pen)
            
        # Draw text
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)
        
        # Draw checkbox
        if has_checkbox:
            checkbox_icon = QPixmap(checkbox_checked_path) if self.model().checkbox_header_status[logicalIndex] else QPixmap(checkbox_unchecked_path)
            painter.drawPixmap(checkbox_rect, checkbox_icon)
            
            if self.checkbox_pressed_section == logicalIndex:
                brush = QBrush(QColor(0, 0, 0, 100))
                painter.setBrush(brush)
                painter.drawRect(checkbox_rect)
            elif self.checkbox_hovered_section == logicalIndex:
                brush = QBrush(QColor(255, 255, 255, 100))
                painter.setBrush(brush)
                painter.drawRect(checkbox_rect)
        
        painter.restore()


class custom_table_model(QAbstractTableModel):
    def __init__(self, data = None, default_nr_col = 6, default_nr_row = 10, checkbox_columns = None, no_edit_columns = None):
        super().__init__()
        
        self.last_mouse_move_index = None
        
        self.default_nr_col = default_nr_col
        self.default_nr_row = default_nr_row
        
        self.initialize_table(data, checkbox_columns)
        
    def flags(self, index):
        flags = super().flags(index)
        col = index.column()
        if self.edit_data[col] or self.checkbox_data[col]:
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
    
        
    def initialize_table(self, data = None, checkbox_columns = None,  no_edit_columns = None):
        self.set_data(data)
        self.initialize_checkboxes(checkbox_columns)
        self.initialize_checkbox_header_status()
        self.initialize_edit_data(no_edit_columns)
        self.last_mouse_move_index = None
    
    
    def set_data(self, data = None):
        if data is None:
            empty_columns = [f'{i+1}' for i in range(self.default_nr_col)] 
            data = pd.DataFrame(columns = empty_columns, data = [[''] * self.default_nr_col for _ in range(self.default_nr_row)])
        self._data = data
    
    
    def initialize_checkboxes(self, checkbox_columns = None):
        if checkbox_columns is None:
            checkbox_columns = [{'name': 'include', 'check_all': True},
                                {'name': 'plot', 'check_all': False},
                                {'name': 'calibrate', 'check_all': True}]
        
        self.checkbox_header = [False] * self.columnCount()
        self.checkbox_data = [False] * self.rowCount()
        
        checkbox_columns_names = [item['name'] for item in checkbox_columns]
        checkbox_columns_check_all = [item['check_all'] for item in checkbox_columns]
        for index, item in enumerate(self._data.columns):
            if item in checkbox_columns_names:
                self.checkbox_data[index] = True
                self._data[item] = self._data[item].astype(bool)
                # self._data[item] = True if (self._data[item] == 'True' or self._data[item] == 1) else False
                self.checkbox_header[index] = True if checkbox_columns_check_all[checkbox_columns_names.index(item)] else False


    def initialize_edit_data(self, no_edit_columns = None):
        if no_edit_columns is None:
            no_edit_columns = ['x_values', 'y_values']
        
        # By default, all data is editable
        self.edit_data = [True] * self.columnCount()
        
        # Set edit flag to False in case it is specified by the user or it is a checkbox column
        for index, item in enumerate(self._data.columns):
            if item in no_edit_columns or self.checkbox_data[index]:
                self.edit_data[index] = False


    def initialize_checkbox_header_status(self):
        self.checkbox_header_status = [False] * self.columnCount()
        
    
    def on_checkbox_header_click(self, index):
        self.checkbox_header_status[index] = not self.checkbox_header_status[index]
        print('index: ', index)
        print('status: ', self.checkbox_header_status[index])
        print('column: ', self._data.columns[index])
        
        
    def on_checkbox_click(self, state, index):
        print('row: ', index.row(), 'column: ', index.column())
        print('col: ', self._data.columns[index.column()])


class custom_table(QTableView):
    def __init__(self, data = None, style: style = None):       
        super().__init__()
        
        # Set model
        self.setModel(custom_table_model(data))
        
        # Set header options
        self.setHorizontalHeader(table_horizontal_header(parent = self))
        self.horizontalHeader().setStretchLastSection(True)  # Make columns stretch to the full width
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.setItemDelegate(item_delegate(parent = self, style = style))
        
        self.setMouseTracking(True)
        
        self.last_mouse_move_index = None
        self.current_editor = None
        
    def update_data(self, data = None, checkbox_columns = None):
        self.model().layoutAboutToBeChanged.emit()
        self.model().initialize_table(data, checkbox_columns)
        self.horizontalHeader().initialize_checkbox_rects()
        self.model().layoutChanged.emit()
        
    
    # def mouseMoveEvent(self, event):
    #     index = self.indexAt(event.pos())      
    #     if index.isValid():
    #         col = index.column()
    #         if self.model().checkbox_data[col]:
    #             if index != self.last_mouse_move_index:
    #                 if self.last_mouse_move_index is not None:
    #                     self.closePersistentEditor(self.last_mouse_move_index)
    #                 self.last_mouse_move_index = index
    #                 self.openPersistentEditor(self.last_mouse_move_index)
    #         else:
    #             if self.last_mouse_move_index is not None:
    #                 self.closePersistentEditor(self.last_mouse_move_index)
    #                 self.last_mouse_move_index = None

    #     super().mouseMoveEvent(event)