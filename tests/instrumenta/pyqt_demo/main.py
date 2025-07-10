# main.py

import sys
from PyQt6.QtWidgets import QApplication

# Import theme settings
from theme import theme_colors, generate_stylesheet

# Import the main window class
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # Generate and apply the theme stylesheet
    try:
        style_sheet = generate_stylesheet(theme_colors)
        app.setStyleSheet(style_sheet)
    except ValueError as e:
        print(f"Error generating stylesheet: {e}", file=sys.stderr)
        # Optionally provide default styling or exit
        # For now, we'll continue without custom styling if error occurs
        pass
    except Exception as e:
        print(f"Unexpected error applying styles: {e}", file=sys.stderr)
        pass


    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
