from datetime import datetime
from dateutil.relativedelta import relativedelta
from PySide6.QtGui import QPainter, QLinearGradient, QBrush, QColor, QFont
from PySide6.QtCore import Qt
from aivalanche_app.components.custom_image import custom_image

class project_card(custom_image):
    def __init__(self, parent = None, image_path = None, title = 'Project X', 
                 created_at = None, last_modified_at = None, on_click = None, *args, **kwargs):
        super().__init__(parent = parent, image_path = image_path, *args, **kwargs)
        
        self.title = title
        
        if created_at is not None:
            self.created_at = self.parse_date_time(created_at)
        else:
            self.created_at = None
            
        if last_modified_at is not None:
            self.last_modified_at = self.parse_date_time(last_modified_at)
        else:
            self.last_modified_at = None
        
        if on_click is not None:
            self.clicked.connect(on_click)

    def parse_date_time(self, date_time):
        time = datetime.strptime(str(date_time), "%Y-%m-%d %H:%M:%S")
        time_difference = relativedelta(datetime.now(), time)
        # parsed_date_time = {'day': time_1.day, 'month': time_1.strftime("%b"), 'year': time_1.year, 
        #                     'hour': time_1.hour, 'minute': time_1.minute, 'second': time_1.second}
        total_seconds_difference = (
            time_difference.years * 365 * 24 * 60 * 60
            + time_difference.months * 30 * 24 * 60 * 60
            + time_difference.days * 24 * 60 * 60
            + time_difference.hours * 60 * 60
            + time_difference.minutes * 60
            + time_difference.seconds
        )
        
        if total_seconds_difference > 20 * 24 * 60 *60:             # 20 days
            return f'{time.day} {time.strftime("%b")} {time.year}'
        elif total_seconds_difference > 48 * 60 * 60:               # 48 hours
            return f'{time_difference.days} days ago'
        elif total_seconds_difference > 60 * 60:                    # 60 minutes
            return f'{time_difference.hours} hours ago'
        elif total_seconds_difference > 60:
            return f'{time_difference.minutes} minutes ago'
        else:
            return f'{time_difference.seconds} seconds ago'
        

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)   
        
        # Get positions and dimensions
        (x, y, w, h), _ = self.get_dimensions()
        
        # Add the gradient rectangle   
        gradient = QLinearGradient(x, y, x, h)
        gradient.setColorAt(0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.7, QColor(255, 255, 255, 0))
        gradient.setColorAt(1, QColor(0, 0, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, y, w, h)

        # Define text margins
        left = 10
        right = 10
        bottom = 50

        # Add title text
        title_font_size = 14
        title_font_weight = QFont.Weight.Bold # bold
        title_color = 'white'
        title_x = x + left
        title_y = y + h - bottom
        title_w = w - left - right
        title_h = title_font_size * 2
        font = QFont()
        font.setPointSize(title_font_size)
        font.setWeight(title_font_weight)
        painter.setFont(font)
        painter.setPen(title_color)
        painter.drawText(title_x, title_y, title_w, title_h, Qt.TextFlag.TextWordWrap, self.title)
        
        # Add created text
        if self.created_at is not None:
            created_at_font_size = 10
            created_at_font_weight = QFont.Weight.Normal # bold
            created_at_color = 'white'
            created_at_x = x + left
            created_at_y = y + h - bottom / 2
            created_at_w = (w - left - right) / 2
            created_at_h = created_at_font_size * 2
            font = QFont()
            font.setPointSize(created_at_font_size)
            font.setWeight(created_at_font_weight)
            painter.setFont(font)
            painter.setPen(created_at_color)
            painter.drawText(created_at_x, created_at_y, created_at_w, created_at_h, Qt.TextFlag.TextWordWrap, f'created: {self.created_at}')
        
        # Add last modified text
        if self.last_modified_at is not None:
            last_modified_at_font_size = 10
            last_modified_at_font_weight = QFont.Weight.Normal # bold
            last_modified_at_color = 'white'
            last_modified_at_x = x + left + (w - left - right)  / 2
            last_modified_at_y = y + h - bottom / 2
            last_modified_at_w = (w - left - right) / 2
            last_modified_at_h = last_modified_at_font_size * 5
            font = QFont()
            font.setPointSize(last_modified_at_font_size)
            font.setWeight(last_modified_at_font_weight)
            painter.setFont(font)
            painter.setPen(last_modified_at_color)
            painter.drawText(last_modified_at_x, last_modified_at_y, last_modified_at_w, last_modified_at_h, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignRight, f'last modified: {self.last_modified_at}')