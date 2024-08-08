from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import Qt
from aivalanche_app.screens.main_window import main_window
from aivalanche_app.paths import fonts_path
from aivalanche_app.resources.themes.style import style
from aivalanche_app.data_store.store import store
import sys, pyqtgraph as pg, os

import traceback
from PySide6.QtCore import QBasicTimer

def debug_start(self, msec, timerType=Qt.TimerType.CoarseTimer):
    print("QBasicTimer.start called:")
    traceback.print_stack()
    original_start(self, msec, timerType)

original_start = QBasicTimer.start
QBasicTimer.start = debug_start

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias = True)
pg.setConfigOption('background', (255, 255, 255, 0))
pg.setConfigOption('foreground', 'k')

# # Loop through all files in the specified folder
# for dir_name in os.listdir(fonts_path):
#     if dir_name == 'KoHo':
#         for file_name in os.listdir(os.path.join(fonts_path, dir_name)):
#             if file_name.lower().endswith(('.ttf', '.otf')):
#                 font_path = os.path.join(fonts_path, dir_name, file_name)
#                 id = QFontDatabase.addApplicationFont(font_path)
#                 with open(font_path, 'rb') as f:
#                     print(f.readlines())
#                 # kot = QFont.applicationFontFamilies(id)

def load_fonts_from_directory(path):
    font_families = {}
    for dir_name in os.listdir(path):
        font_families[dir_name] = []
        for file_name in os.listdir(os.path.join(path, dir_name)):
            if file_name.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(path, dir_name, file_name)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    font_families[dir_name].extend(families)
                else:
                    print(f"Failed to load font: {font_path}")
    return font_families

# TODO Make sure to close the app once the GUI closes.
# This problem appeared when migrated from PyQt6 to PySide6.
if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

app.setAttribute(Qt.AA_UseStyleSheetPropagationInWidgetStyles, True)

# # Set font
# font_families = load_fonts_from_directory(fonts_path)
# if font_families:
#     custom_font = QFont(font_families['KoHo'][1])
# else:
#     print("No custom fonts loaded.")
#     custom_font = QFont()
# app.setFont(custom_font)

style = style()
db_type = 'local_files' # possible values are [local_files, local_mysql_db]
store = store(db_type = db_type, style = style)
app.setStyleSheet(style.stylesheet)

window = main_window(store = store)    
window.show()
sys.exit(app.exec())
