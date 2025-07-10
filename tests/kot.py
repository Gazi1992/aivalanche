import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QComboBox, QFrame, QGraphicsDropShadowEffect,
    QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt6.QtGui import QPalette, QColor


# --- Custom Hover Menu Widget ---
class HoverMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        # --- Make the OUTER QWidget transparent ---
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose) # Clean up memory
        # No setAutoFillBackground needed for outer widget

        # --- Main Layout for the Transparent Outer Widget ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # No margins for the outer layout

        # --- Inner Container Frame (This gets styled) ---
        self.container_frame = QFrame()
        self.container_frame.setObjectName("HoverContainerFrame") # For specific styling
        self.main_layout.addWidget(self.container_frame) # Add frame to outer layout

        # --- Layout for the Content INSIDE the Frame ---
        self.content_layout = QVBoxLayout(self.container_frame) # Set layout on the frame
        self.content_layout.setContentsMargins(10, 10, 10, 10) # Padding inside the styled frame
        self.content_layout.setSpacing(5)

        # --- Add Checkboxes to the Frame's Layout ---
        self.cb_option1 = QCheckBox("Show Grid")
        self.cb_option1.setChecked(True)
        self.cb_option2 = QCheckBox("Enable Zoom")
        self.cb_option2.setChecked(False)
        self.cb_option3 = QCheckBox("Log Scale Y")
        self.cb_option3.setChecked(False)

        self.content_layout.addWidget(self.cb_option1)
        self.content_layout.addWidget(self.cb_option2)
        self.content_layout.addWidget(self.cb_option3)
        # --- --- --- --- --- --- --- --- --- --- --- --

        # Initial style update applies style to the container_frame now
        self.update_style(is_dark=False)

        self._hide_timer = QTimer(self)
        self._hide_timer.setInterval(300)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    # enterEvent and leaveEvent apply to the outer HoverMenu widget
    def enterEvent(self, event: QEvent):
        # Cancel self-hide timer if mouse re-enters menu
        self._hide_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        # Start timer ONLY when mouse leaves the menu itself
        self._hide_timer.start()
        super().leaveEvent(event)

    def connect_signals(self, slot_option1, slot_option2, slot_option3):
        # Convenience method to connect checkbox signals from outside
        self.cb_option1.stateChanged.connect(slot_option1)
        self.cb_option2.stateChanged.connect(slot_option2)
        self.cb_option3.stateChanged.connect(slot_option3)

    def update_style(self, is_dark):
        # Set Alpha for 50% transparency (128 / 255)
        bg_alpha = 200

        if is_dark:
             bg_color_str = f"rgba(50, 50, 50, {bg_alpha})" # String for stylesheet
             border_color = "#666"
             text_color = "#ccc"
        else:
             bg_color_str = f"rgba(255, 255, 255, {bg_alpha})" # String for stylesheet
             border_color = "lightgray"
             text_color = "black"

        # --- Apply stylesheet specifically to the INNER FRAME ---
        self.container_frame.setStyleSheet(f"""
            QFrame#HoverContainerFrame {{
                background-color: {bg_color_str};
                border: 1px solid {border_color};
                border-radius: 4px; /* Rounded corners should work on QFrame */
            }}
            /* Style checkboxes within this context */
            QFrame#HoverContainerFrame QCheckBox {{
                background-color: transparent;
                border: none;
                color: {text_color};
            }}
        """)


# --- Main Window ---
class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Single Plot Interactive Demo")
        self.setGeometry(100, 100, 950, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Crucial: Allow the central widget to draw its background using the palette
        central_widget.setAutoFillBackground(True)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Global theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        controls_layout.addWidget(self.theme_combo)
        controls_layout.addStretch(1)
        main_layout.addLayout(controls_layout)

        plot_grid_layout = QGridLayout()
        plot_grid_layout.setSpacing(25)
        main_layout.addLayout(plot_grid_layout)

        # --- Generate Sample Data ---
        x = np.linspace(0, 10, 300)
        # Adjusted Y data to be clearly positive for log scale testing
        y_offset = 2.0
        y_amplitude = 1.0
        y = y_offset + y_amplitude * (np.sin(x * 1.5) + np.random.normal(0, 0.08, size=x.shape))

        self.plot_widgets = []
        self.plot_frames = []
        self.menu_buttons = {} # Store buttons {index: button}
        self.hover_menus = {}  # Store menus {index: menu}
        plot_titles = ["Plot 1", "Plot 2", "Plot 3", "Plot 4"]
        positions = [(i, j) for i in range(2) for j in range(2)]

        self.transparent_pen = pg.mkPen(None) # Pen for ViewBox border

        for i, pos in enumerate(positions):
            # --- Create Frame ---
            plot_frame = QFrame()
            plot_frame.setObjectName(f"PlotFrame_{i}")
            plot_frame.setFrameShape(QFrame.Shape.StyledPanel)
            # Install event filter on frame for resize handling *early*
            plot_frame.installEventFilter(self)

            # --- Graphics Effect ---
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(18)
            shadow.setOffset(5, 5)
            shadow.setColor(QColor(0, 0, 0, 65)) # Initial shadow color
            plot_frame.setGraphicsEffect(shadow)

            # --- Layout Inside Frame ---
            frame_layout = QVBoxLayout(plot_frame)
            frame_layout.setContentsMargins(15, 15, 15, 15) # Internal padding
            frame_layout.setSpacing(0)

            # --- Plot Widget ---
            plot_widget = pg.PlotWidget()
            plot_widget.setStyleSheet("QFrame { border: 0px; }") # Remove its own frame
            frame_layout.addWidget(plot_widget)

            plot_item = plot_widget.getPlotItem()
            view_box = plot_item.getViewBox()
            view_box.setBorder(self.transparent_pen) # Remove ViewBox border

            plot_item.setLabel('left', "Amplitude")
            plot_item.setLabel('bottom', "Time (s)")

            # --- Create "..." Button ---
            menu_button = QPushButton("...", parent=plot_frame) # Parent to frame
            menu_button.setFixedSize(20, 20)
            menu_button.setObjectName(f"MenuButton_{i}") # Unique name
            # Style set during theme change

            # Position button initially (will be updated on frame resize)
            margin = 8
            # Initial frame width might be small, use max() to avoid negative coords
            # Get geometry AFTER parenting might be slightly more reliable
            initial_button_x = plot_frame.geometry().width() - menu_button.width() - margin
            menu_button.move(max(margin, initial_button_x), margin)
            menu_button.raise_() # Ensure button is on top
            menu_button.show()   # Make sure it's visible

            # --- Create Hover Menu ---
            hover_menu = HoverMenu()
            # Connect checkbox signals TO SPECIFIC SLOTS PER PLOT
            hover_menu.connect_signals(
                # Pass check state directly as bool
                lambda state, p=plot_item: self.toggle_grid(state == Qt.CheckState.Checked.value, p),
                lambda state, v=view_box: self.toggle_zoom(state == Qt.CheckState.Checked.value, v),
                # Pass menu widget reference for unchecking logic
                lambda state, p=plot_item, menu_widget=hover_menu: self.toggle_log_y(state == Qt.CheckState.Checked.value, p, menu_widget)
            )

            # --- Link Button and Menu for Hover Logic ---
            menu_button._hover_menu = hover_menu # Store ref for easy access in filter
            menu_button.installEventFilter(self) # Let main window handle button hover

            # --- Store references ---
            self.plot_widgets.append(plot_widget)
            self.plot_frames.append(plot_frame)
            self.menu_buttons[i] = menu_button
            self.hover_menus[i] = hover_menu

            # --- Plot data ---
            self.line_pen = pg.mkPen(color=(218, 143, 43), width=2)
            plot_item.plot(x, y, pen=self.line_pen)

            # Add frame to the main grid layout
            plot_grid_layout.addWidget(plot_frame, pos[0], pos[1])

        # Apply the initial theme right after setup
        self.change_theme(self.theme_combo.currentText())

    # --- Handle Events using Event Filter ---
    def eventFilter(self, obj, event):
        # --- Button Hover ---
        if isinstance(obj, QPushButton) and obj.objectName().startswith("MenuButton_"):
            # Find the associated menu using the index from the button's name
            try:
                idx = int(obj.objectName().split('_')[-1])
                menu = self.hover_menus.get(idx)
                if not menu: return False # No menu found for this button
            except (ValueError, IndexError):
                 return False # Failed to parse index

            if event.type() == QEvent.Type.Enter:
                # Mouse entered button: stop menu's hide timer
                menu._hide_timer.stop() # Stop menu from hiding if timer was running

                # --- Initial Position & Show ---
                # Calculate an initial estimate (might be slightly off first time)
                menu_width_hint = menu.sizeHint().width()
                button_pos = obj.mapToGlobal(QPoint(0, 0)) # Button's top-left
                initial_x = button_pos.x() - menu_width_hint - 5
                initial_y = button_pos.y() + obj.height()
                # Adjusted logic for positioning below and right-aligned
                # menu.move(QPoint(initial_x, initial_y)) # Move to estimated position

                menu.show() # Show the menu (this triggers layout calculation)
                menu.raise_() # Ensure menu is on top

                # --- Reposition After Layout (Timer Trick) ---
                # Use a zero-delay timer to run *after* the current event processing
                def reposition_menu():
                    actual_menu_width = menu.width() # Use actual width now
                    # Recalculate button pos in case something moved slightly?
                    current_button_pos = obj.mapToGlobal(QPoint(0, 0))
                    final_x = current_button_pos.x() - actual_menu_width - 5
                    final_y = current_button_pos.y()
                    menu.move(QPoint(final_x, final_y))

                QTimer.singleShot(0, reposition_menu)
                # --- --- --- --- --- --- --- --- --- --- ---

                return super().eventFilter(obj, event)

            elif event.type() == QEvent.Type.Leave:
                menu._hide_timer.start()
                return super().eventFilter(obj, event)

        # --- Frame Resize ---
        # Handles repositioning the '...' button when the frame is resized
        elif isinstance(obj, QFrame) and obj.objectName().startswith("PlotFrame_"):
             if event.type() == QEvent.Type.Resize:
                 # Find the corresponding button
                 try:
                     idx = int(obj.objectName().split('_')[-1])
                     button = self.menu_buttons.get(idx)
                     if button:
                         margin = 8
                         new_x = obj.width() - button.width() - margin
                         button.move(max(margin, new_x), margin) # Use max to avoid negative coords
                 except (ValueError, IndexError):
                     pass
                 # Don't return True here, allow default resize processing for the frame

        # Pass on unhandled events to the parent class
        return super().eventFilter(obj, event)

    # --- Example Slot Functions for Checkboxes ---
    def toggle_grid(self, is_checked, plot_item):
        # print(f"Toggle Grid: {is_checked} for Plot: {plot_item.titleLabel.text}")
        plot_item.showGrid(x=True, y=is_checked)

    def toggle_zoom(self, is_checked, view_box):
        # print(f"Toggle Zoom: {is_checked} for ViewBox: {view_box}")
        # Enable/disable mouse interaction for zooming/panning
        view_box.setMouseEnabled(x=True, y=is_checked)

    # Modified to accept menu reference to uncheck box
    def toggle_log_y(self, is_checked, plot_item, menu_widget):
        # print(f"Toggle Log Y: {is_checked} for Plot: {plot_item.titleLabel.text}")
        # Basic check: Ensure plot range is positive before setting log scale
        current_range = plot_item.getViewBox().viewRange()
        # Check if lower bound of Y range is non-positive
        if is_checked and current_range[1][0] <= 1e-9: # Use small epsilon instead of 0
             print(f"Warning: Cannot set log scale for {plot_item.titleLabel.text} with non-positive Y data visible.")
             plot_item.setLogMode(x=False, y=False) # Ensure it's off
             # Block signals temporarily to prevent infinite loop if stateChanged triggers this again
             menu_widget.cb_option3.blockSignals(True)
             menu_widget.cb_option3.setChecked(False)
             menu_widget.cb_option3.blockSignals(False)
             return # Stop here
        plot_item.setLogMode(x=False, y=is_checked)

    # --- Theme Change Handler ---
    def change_theme(self, theme):
        # Get Central Widget and its Palette
        cw = self.centralWidget()
        pal = cw.palette()
        is_dark = (theme == "Dark")

        border_radius = 8
        if not is_dark: # Light theme settings
            # PyQtGraph global settings
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')
            # Specific colors used in loop
            plot_bg_color = 'w'
            axis_fg_color = 'k'
            grid_alpha = 0.3
            # Frame stylesheet
            frame_style = f"""
                QFrame[objectName^="PlotFrame_"] {{
                    border: 1px solid lightgray;
                    border-radius: {border_radius}px;
                    background-color: white;
                }}
            """
            # Shadow color
            shadow_color = QColor(0, 0, 0, 65)
            # Main window background
            pal.setColor(QPalette.ColorRole.Window, QColor('white'))
            # Button stylesheet
            button_style = """
                QPushButton {
                    border: 1px solid lightgray; border-radius: 10px;
                    background-color: white; color: black; font-weight: bold; padding-bottom: 3px;
                } QPushButton:hover { background-color: #eee; } """

        else: # Dark theme settings
            # PyQtGraph global settings
            pg.setConfigOption('background', '#333333')
            pg.setConfigOption('foreground', '#cccccc')
            # Specific colors used in loop
            plot_bg_color = '#333333'
            axis_fg_color = '#cccccc'
            grid_alpha = 0.2
            # Frame stylesheet
            frame_style = f"""
                QFrame[objectName^="PlotFrame_"] {{
                    border: 1px solid #555555;
                    border-radius: {border_radius}px;
                    background-color: black;
                }}
            """
            # Shadow color
            shadow_color = QColor(150, 150, 150, 50) # Lighter shadow for dark theme
             # Main window background
            pal.setColor(QPalette.ColorRole.Window, QColor('#2e2e2e')) # Dark gray background
            # Button stylesheet
            button_style = """
                 QPushButton {
                    border: 1px solid #666; border-radius: 10px;
                    background-color: #222; color: #ccc; font-weight: bold; padding-bottom: 3px;
                } QPushButton:hover { background-color: #444; } """

        # Apply the main window background palette
        cw.setPalette(pal)

        # --- Loop through plots and apply theme changes ---
        plot_titles = ["Plot 1", "Plot 2", "Plot 3", "Plot 4"]
        for i, plot_widget in enumerate(self.plot_widgets):
            # Get corresponding elements
            plot_frame = self.plot_frames[i]
            button = self.menu_buttons.get(i)
            menu = self.hover_menus.get(i)

            # Apply styles
            plot_frame.setStyleSheet(frame_style) # Apply border/background style
            if button:
                button.setStyleSheet(button_style)
                button.raise_() # Ensure button stays on top after style change
            if menu:
                 menu.update_style(is_dark) # Update menu appearance

            # Update Shadow Color
            shadow_effect = plot_frame.graphicsEffect()
            if isinstance(shadow_effect, QGraphicsDropShadowEffect):
                shadow_effect.setColor(shadow_color)

            # Update Plot Elements
            plot_item = plot_widget.getPlotItem()
            view_box = plot_item.getViewBox()
            view_box.setBorder(self.transparent_pen) # Ensure ViewBox border stays off

            plot_widget.setStyleSheet("QFrame { border: 0px; }") # Ensure PlotWidget border stays off
            plot_widget.setBackground(plot_bg_color)

            # Update Title and Axes
            title = plot_titles[i]
            plot_item.setTitle(title, color=axis_fg_color, size='10pt')

            axis_pen = pg.mkPen(color=axis_fg_color)
            text_pen = pg.mkPen(color=axis_fg_color)
            for axis_name in ('left', 'bottom', 'right', 'top'):
                axis = plot_item.getAxis(axis_name)
                axis.setPen(axis_pen)
                axis.setTextPen(text_pen)

            # Refresh plot features based on current checkbox state from menu
            if menu:
                grid_state = menu.cb_option1.checkState()
                zoom_state = menu.cb_option2.checkState()
                log_state = menu.cb_option3.checkState()

                plot_item.showGrid(x=True, y=(grid_state == Qt.CheckState.Checked))
                view_box.setMouseEnabled(x=True, y=(zoom_state == Qt.CheckState.Checked))

                # Re-apply log check during theme change too
                is_log = (log_state == Qt.CheckState.Checked)
                current_range = view_box.viewRange()
                if is_log and current_range[1][0] <= 1e-9:
                    # Don't print warning again, just ensure log is off
                    plot_item.setLogMode(x=False, y=False)
                    if menu.cb_option3.isChecked(): # Only uncheck if needed
                        menu.cb_option3.blockSignals(True)
                        menu.cb_option3.setChecked(False)
                        menu.cb_option3.blockSignals(False)
                else:
                    plot_item.setLogMode(x=False, y=is_log)

            # Update Line Color (if it needed changing based on theme)
            data_items = plot_item.listDataItems()
            if data_items:
                 data_items[0].setPen(self.line_pen) # Keep original pen for now


# --- Run the Application ---
if __name__ == '__main__':
    # Enable Antialiasing globally in pyqtgraph for smoother results
    pg.setConfigOptions(antialias=True)

    app = QApplication(sys.argv)
    # Optional: Set a global style like Fusion for more modern look
    # app.setStyle('Fusion')

    window = PlotWindow()
    window.show()
    sys.exit(app.exec())
