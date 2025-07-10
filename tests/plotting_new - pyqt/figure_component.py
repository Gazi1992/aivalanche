# figure_component.py
import logging
from typing import Dict, Optional, Any, List, Callable

import pyqtgraph as pg
from PyQt6 import QtGui
from PyQt6.QtWidgets import ( QWidget, QVBoxLayout, QFrame,
                              QGraphicsDropShadowEffect, QApplication, QLabel)
from PyQt6.QtCore import Qt, QPoint, QEvent, pyqtSignal, QRect # QRect added
from PyQt6.QtGui import QColor, QFont

from data_handler import DataHandler
import plot_handlers
import pandas as pd

logger = logging.getLogger(__name__)

SHADOW_BLUR_RADIUS = 15
SHADOW_OFFSET = 5
FRAME_CLICK_MARGIN = 15 # Pixels from the edge of plot_frame to consider a "frame click"

class FigureComponent(QWidget):
    figure_clicked = pyqtSignal(str)

    def __init__(self,
                 figure_id: str,
                 figure_config: Dict,
                 data_handler: DataHandler,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.figure_id = figure_id
        self.figure_config = figure_config
        self.data_handler = data_handler
        self.plot_widget: Optional[pg.PlotWidget] = None
        self.plot_frame: Optional[QFrame] = None
        self.plot_items: List[Dict[str, Any]] = []
        self.transparent_pen = pg.mkPen(None)
        self.current_theme_props: Optional[Dict[str, Any]] = None
        self.is_selected: bool = False

        self.plot_handlers_map: Dict[str, Callable] = {
            "line": plot_handlers.create_line_plot_item,
            "scatter": plot_handlers.create_scatter_plot_item,
            "histogram": plot_handlers.create_histogram_plot_item,
            "bar": plot_handlers.create_bar_plot_item,
        }

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(SHADOW_BLUR_RADIUS)
        shadow.setOffset(SHADOW_OFFSET, SHADOW_OFFSET)
        shadow.setColor(QColor(0, 0, 0, 0))
        self.setGraphicsEffect(shadow)

        self._setup_ui_and_plot()

    def _setup_ui_and_plot(self):
        component_layout = QVBoxLayout(self)
        component_layout.setContentsMargins(0, 0, 0, 0)
        component_layout.setSpacing(0)

        self.plot_frame = QFrame(objectName=f"PlotFrame_{self.figure_id}")
        self.plot_frame.setProperty("role", "plot")
        self.plot_frame.setProperty("selected", False)
        self.plot_frame.setFrameShape(QFrame.Shape.StyledPanel)
        component_layout.addWidget(self.plot_frame)

        self.frame_layout = QVBoxLayout(self.plot_frame)
        self.frame_layout.setContentsMargins(6, 6, 6, 6)
        self.frame_layout.setSpacing(0)

        self.plot_widget = self._create_plot_widget_from_config()
        if self.plot_widget is None:
            error_label = QLabel(f"Error creating plot '{self.figure_id}'")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.frame_layout.addWidget(error_label) # Add to frame_layout
            logger.error(f"FigureComponent '{self.figure_id}': PlotWidget creation failed.")
            return
        else:
            self.frame_layout.addWidget(self.plot_widget) # Add to frame_layout

        self._add_plot_items_from_config()

    def _create_plot_widget_from_config(self) -> Optional[pg.PlotItem]:
        try:
            plot_widget = pg.PlotWidget()

            x_scale = self.figure_config.get('x_scale', 'linear')
            y_scale = self.figure_config.get('y_scale', 'linear')
            plot_widget.setLogMode(x=(x_scale == 'log'), y=(y_scale == 'log'))

            title_text = self.figure_config.get('title', '')
            if title_text: plot_widget.setTitle(title_text)
            x_label_text = self.figure_config.get('x_label', '')
            if x_label_text: plot_widget.setLabel('bottom', x_label_text)
            y_label_text = self.figure_config.get('y_label', '')
            if y_label_text: plot_widget.setLabel('left', y_label_text)

            plot_item = plot_widget.getPlotItem()
            if plot_item:
                 view_box = plot_item.getViewBox()
                 if view_box:
                      view_box.setBorder(self.transparent_pen)

            items_cfg = self.figure_config.get('items', [])
            needs_legend = any(
                isinstance(item, dict) and item.get('legend_name') is not None
                for item in items_cfg
            )
            if needs_legend:
                 current_plot_item = plot_widget.getPlotItem()
                 if current_plot_item and not current_plot_item.legend:
                     try: plot_widget.addLegend()
                     except Exception as e: logger.error(f"Failed to add legend for '{self.figure_id}': {e}")
            return plot_widget
        except Exception as e:
             logger.error(f"Failed to create plot widget for '{self.figure_id}': {e}", exc_info=True)
             return None

    def _add_plot_items_from_config(self):
        if not self.plot_widget: return
        items_config = self.figure_config.get('items', [])
        if not isinstance(items_config, list):
             logger.warning(f"Figure '{self.figure_id}': 'items' is not a list or is missing.")
             return
        for item_config in items_config:
            if not isinstance(item_config, dict):
                logger.warning(f"Skipping invalid (non-dict) item config in '{self.figure_id}'.")
                continue
            item_id = item_config.get('id'); plot_type = item_config.get('type')
            if not item_id or not plot_type:
                logger.warning(f"Skipping item in '{self.figure_id}': Missing 'id' or 'type'.")
                continue

            handler = self.plot_handlers_map.get(plot_type)
            if not handler:
                logger.error(f"No handler found for plot type '{plot_type}' (item '{item_id}').")
                continue

            # Special handling for histogram: only one data column needed.
            if plot_type == 'histogram':
                source = item_config.get('source')
                column_name = item_config.get('column') or item_config.get('y_column') or item_config.get('x_column')
                if not source or not column_name:
                    logger.error(f"Histogram item '{item_id}' requires 'source' and 'column' fields.")
                    continue

                df = self.data_handler.load_data(source)
                if df is None:
                    continue  # Error already logged inside DataHandler

                if column_name not in df.columns:
                    logger.error(f"Histogram item '{item_id}': Column '{column_name}' not found in data source '{source}'.")
                    continue

                try:
                    values_series = df[column_name].dropna()
                    # Attempt numeric conversion; ignore non-convertible rows
                    numeric_values = pd.to_numeric(values_series, errors='coerce').dropna().tolist()
                except Exception as e:
                    logger.error(f"Histogram item '{item_id}': Error processing data column '{column_name}': {e}", exc_info=True)
                    continue

                if not numeric_values:
                    logger.warning(f"Histogram item '{item_id}' resulted in no numeric data to plot.")
                    continue

                plot_item_obj = handler(item_config, numeric_values, None)
            else:
                # Check for 3D-to-2D mode
                z_col = item_config.get('z_column')
                if z_col:
                    self._add_line_scatter_with_z(item_config, handler)
                    continue  # handler done internally

                x_data, y_data = self.data_handler.get_plot_data(item_config)
                if x_data is None or y_data is None:
                    continue
                if not x_data and not y_data:
                    logger.warning(f"No data points available for item '{item_id}' in '{self.figure_id}'. Skipping plot item.")
                    continue

                # Handle optional stacking for bar plots
                stack_ctx = None
                if plot_type == 'bar':
                    stack_group = item_config.get('stack_group')
                    if stack_group is not None:
                        if not hasattr(self, '_bar_stack_contexts'):
                            self._bar_stack_contexts = {}
                        stack_ctx = self._bar_stack_contexts.setdefault(stack_group, {})

                plot_item_obj = handler(item_config, x_data, y_data, stack_ctx) if plot_type == 'bar' else handler(item_config, x_data, y_data)

            if plot_item_obj:
                try:
                    if isinstance(plot_item_obj, (list, tuple)):
                        for sub_idx, sub_item in enumerate(plot_item_obj):
                            self.plot_widget.addItem(sub_item)
                            self.plot_items.append({'id': f"{item_id}_{sub_idx}", 'item': sub_item})
                    else:
                        self.plot_widget.addItem(plot_item_obj)
                        self.plot_items.append({'id': item_id, 'item': plot_item_obj})

                        # If bar plot provided categorical labels, set them as X-axis tick labels
                        if hasattr(plot_item_obj, '_category_labels') and isinstance(plot_item_obj._category_labels, list):
                            try:
                                labels = plot_item_obj._category_labels
                                x_positions = list(range(len(labels)))
                                axis = self.plot_widget.getPlotItem().getAxis('bottom')
                                axis.setTicks([[(pos, str(label)) for pos, label in zip(x_positions, labels)]])
                            except Exception as e:
                                logger.error(f"Failed to set category tick labels for bar plot '{item_id}': {e}")
                except Exception as e:
                    logger.error(f"Error adding plot graphics item '{item_id}' to plot: {e}", exc_info=True)
            else:
                logger.error(f"Handler failed to create graphics item '{item_id}' (type {plot_type}).")

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.plot_frame and self.plot_widget:
                # Get the click position relative to FigureComponent
                click_pos_in_figure_comp = event.pos()

                # Get the geometry of plot_widget relative to FigureComponent
                # FigureComponent -> plot_frame -> frame_layout -> plot_widget

                # Position of plot_frame within FigureComponent (usually 0,0 if component_layout has no margins)
                plot_frame_pos_in_figure_comp = self.plot_frame.pos()

                # Position of plot_widget within plot_frame (considering frame_layout's margins)
                plot_widget_pos_in_plot_frame = self.plot_widget.pos()

                # Overall position of plot_widget relative to FigureComponent's top-left
                plot_widget_origin_in_figure_comp = plot_frame_pos_in_figure_comp + plot_widget_pos_in_plot_frame

                plot_widget_rect_in_figure_comp = QRect(
                    plot_widget_origin_in_figure_comp,
                    self.plot_widget.size()
                )

                # Check if the click is INSIDE the plot_widget's bounding rectangle
                if plot_widget_rect_in_figure_comp.contains(click_pos_in_figure_comp):
                    # Click is inside the plot_widget, let plot_widget handle it (for zoom/pan etc.)
                    # We might need to pass the event down if it's not automatically.
                    # However, pyqtgraph's PlotWidget usually handles its own mouse events.
                    # So, we just don't emit figure_clicked here.
                    # logger.debug(f"Click inside plot_widget for {self.figure_id}")
                    pass # Let the event propagate or be handled by plot_widget
                else:
                    # Click is outside plot_widget, potentially on the frame/margin area
                    # Check if click is within the bounds of plot_frame itself
                    # (This is implicitly true if event is received by FigureComponent and not consumed by plot_widget)
                    # Or, more specifically, if it's within the FigureComponent's bounds but outside plot_widget_rect

                    # For a simpler approach, if it's not in plot_widget, consider it a frame click.
                    # The FRAME_CLICK_MARGIN logic could be added here if you want to be more precise
                    # about *how close* to the border the click must be.
                    # e.g. check if click_pos_in_figure_comp is within self.rect() but
                    # not within plot_widget_rect_in_figure_comp.
                    # For now, any click not on plot_widget but on FigureComponent triggers selection.
                    self.figure_clicked.emit(self.figure_id)
                    event.accept() # Consume the event as we've handled it for selection
                    return # Important to prevent further processing if we emit.
            else:
                # Fallback or if widgets aren't ready, emit click anyway
                self.figure_clicked.emit(self.figure_id)
                event.accept()
                return

        super().mousePressEvent(event) # Pass on other mouse buttons or if not handled

    def set_selected(self, is_selected: bool):
        if self.is_selected == is_selected:
            return
        self.is_selected = is_selected
        if self.current_theme_props and self.plot_frame:
            self._apply_frame_and_shadow_style(self.current_theme_props)
            self.plot_frame.update()

    def reset_style_overrides_to_theme(self):
        fig_id = self.figure_id
        logger.info(f"Figure '{fig_id}': Resetting style overrides to theme defaults.")
        if 'grid_color' in self.figure_config:
            self.figure_config['grid_color'] = None

    def apply_theme(self, theme_props: Dict[str, Any]):
       self.current_theme_props = theme_props
       fig_id = self.figure_id

       is_dark_theme = theme_props.get('is_dark', False)
       if not self.plot_widget or not self.plot_frame:
           logger.error(f"Figure '{fig_id}': PlotWidget or PlotFrame not available. Styling error frame.")
           error_frame_bg_key = 'error_frame_bg_dark' if is_dark_theme else 'error_frame_bg_light'
           default_error_bg = "#500" if is_dark_theme else "#FDD"
           error_frame_bg = theme_props.get(error_frame_bg_key, default_error_bg)
           if self.plot_frame:
                self.plot_frame.setStyleSheet(f"QFrame {{ background-color: {error_frame_bg}; border: 1px solid red; border-radius: 6px; }}")
                shadow = self.graphicsEffect()
                if shadow: shadow.setEnabled(False)
           return

       self._apply_frame_and_shadow_style(theme_props)
       self._apply_plot_widget_style(theme_props)

       plot_item = self.plot_widget.getPlotItem()
       if plot_item:
            bottom_axis = plot_item.getAxis('bottom')
            left_axis = plot_item.getAxis('left')
            initial_y_scale_log = self.figure_config.get('y_scale') == 'log'
            current_x_log = bottom_axis.logMode if bottom_axis else False
            plot_item.setLogMode(x=current_x_log, y=initial_y_scale_log)

            initial_x_scale_log = self.figure_config.get('x_scale') == 'log'
            current_y_log = left_axis.logMode if left_axis else False
            plot_item.setLogMode(x=initial_x_scale_log, y=current_y_log)

            initial_grid_x_visible = self.figure_config.get('grid_x', True)
            initial_grid_y_visible = self.figure_config.get('grid_y', True)
            plot_item.showGrid(x=initial_grid_x_visible, y=initial_grid_y_visible)

       self.plot_widget.update()
       if plot_item and plot_item.getViewBox():
           plot_item.getViewBox().update()

    def _apply_frame_and_shadow_style(self, theme_props: Dict[str, Any]):
        if not self.plot_frame: return

        border_radius = theme_props['border_radius']  # still used for shadow effect radius maybe
        shadow_color_val = theme_props['shadow_color']
        shadow_color = QColor(shadow_color_val) if isinstance(shadow_color_val, str) else shadow_color_val
        shadow_blur = theme_props['shadow_blur']
        shadow_offset = theme_props['shadow_offset']

        if self.is_selected:
            frame_border_color = theme_props.get('selected_frame_border', theme_props['frame_border'])
            frame_border_width = theme_props.get('selected_frame_border_width', 2)
        else:
            frame_border_color = theme_props['frame_border']
            frame_border_width = 1

        # Update selected property so QSS switches border color/width
        self.plot_frame.setProperty("selected", self.is_selected)
        self.plot_frame.style().unpolish(self.plot_frame)
        self.plot_frame.style().polish(self.plot_frame)

        shadow_effect = self.graphicsEffect()
        if isinstance(shadow_effect, QGraphicsDropShadowEffect):
            shadow_effect.setColor(shadow_color)
            shadow_effect.setBlurRadius(shadow_blur)
            shadow_effect.setOffset(shadow_offset, shadow_offset)
            shadow_effect.setEnabled(True)

    def _apply_plot_widget_style(self, theme_props: Dict[str, Any]):
        if not self.plot_widget: return

        plot_bg_color = theme_props['plot_bg']
        axis_fg_color_theme = theme_props.get('axis_fg', '#808080')
        legend_text_color = theme_props['legend_text_color']

        plot_title_fs = theme_props['plot_title_font_size']
        plot_title_margin_bottom_str = theme_props['plot_title_margin_bottom']
        axis_label_fs = theme_props['axis_label_font_size']
        axis_tick_fs_str = theme_props['axis_tick_font_size']
        legend_fs_str = theme_props['legend_font_size']

        try: plot_title_pixel_spacing = int("".join(filter(str.isdigit, plot_title_margin_bottom_str)))
        except ValueError: plot_title_pixel_spacing = 5
        try: axis_tick_font_point_size = int(axis_tick_fs_str.replace('pt', ''))
        except ValueError: axis_tick_font_point_size = 9
        try: legend_font_point_size = int(legend_fs_str.replace('pt', ''))
        except ValueError: legend_font_point_size = 9

        self.plot_widget.setBackground(plot_bg_color)
        plot_item = self.plot_widget.getPlotItem()

        if not plot_item:
            logger.warning(f"Figure '{self.figure_id}': PlotItem not found. Cannot style.")
            return

        view_box = plot_item.getViewBox()
        if view_box: view_box.setBorder(self.transparent_pen)

        original_title_text = self.figure_config.get('title', '')
        if original_title_text or plot_item.titleLabel:
            title_style = f"color:{axis_fg_color_theme}; font-size:{plot_title_fs};"
            if not plot_item.titleLabel and original_title_text: plot_item.setTitle(original_title_text)
            if plot_item.titleLabel : plot_item.setTitle(f'<span style="{title_style}">{original_title_text}</span>')

        if plot_item.titleLabel and plot_item.layout:
             plot_item.layout.setRowSpacing(0, plot_title_pixel_spacing if plot_item.titleLabel.isVisible() else 0)

        self._style_plot_axes(plot_item, theme_props, axis_fg_color_theme, axis_tick_font_point_size, axis_label_fs)
        self._style_plot_legend(plot_item, theme_props, legend_text_color, legend_font_point_size)

    def _style_plot_axes(self, plot_item: pg.PlotItem, theme_props: Dict[str, Any],
                         axis_fg_color_theme: str, axis_tick_font_point_size: int, axis_label_fs: str):
        grid_color_hex_from_config = self.figure_config.get('grid_color')
        if grid_color_hex_from_config and QColor.isValidColor(grid_color_hex_from_config):
            effective_axis_color = QColor(grid_color_hex_from_config)
        else:
            effective_axis_color = QColor(axis_fg_color_theme)

        axis_label_text_color = QColor(axis_fg_color_theme)
        grid_alpha_float = self.figure_config.get('grid_alpha', 0.3)
        grid_alpha_int = int(grid_alpha_float * 255)

        axis_line_tick_pen = pg.mkPen(color=effective_axis_color)
        tick_font = QFont(); tick_font.setPointSize(axis_tick_font_point_size)

        initial_grid_x_visible = self.figure_config.get('grid_x', True)
        initial_grid_y_visible = self.figure_config.get('grid_y', True)

        for axis_name in ('left', 'bottom', 'right', 'top'):
            axis = plot_item.getAxis(axis_name)
            if axis:
                axis.setPen(axis_line_tick_pen)
                axis.setTextPen(axis_line_tick_pen)
                axis.setTickFont(tick_font)

                show_this_axis_grid = False
                if axis_name == 'bottom' and initial_grid_x_visible: show_this_axis_grid = True
                elif axis_name == 'left' and initial_grid_y_visible: show_this_axis_grid = True

                axis.setGrid(grid_alpha_int if show_this_axis_grid else 0)

                label_text_key = None
                if axis_name == 'bottom': label_text_key = 'x_label'
                elif axis_name == 'left': label_text_key = 'y_label'

                if label_text_key:
                     original_label_text = self.figure_config.get(label_text_key, axis.labelText or "")
                     label_style_dict = {'color': axis_label_text_color.name(), 'font-size': axis_label_fs}
                     axis.setLabel(text=original_label_text, units=axis.labelUnits, **label_style_dict)

    def _style_plot_legend(self, plot_item: pg.PlotItem, theme_props: Dict[str, Any],
                           legend_text_color: str, legend_font_point_size: int):
        if plot_item.legend:
           legend_font = QFont(); legend_font.setPointSize(legend_font_point_size)
           for _, label_item_proxy in plot_item.legend.items:
               actual_label_item = None
               if hasattr(label_item_proxy, 'item') and isinstance(label_item_proxy.item, pg.LabelItem):
                   actual_label_item = label_item_proxy.item
               elif isinstance(label_item_proxy, pg.LabelItem):
                   actual_label_item = label_item_proxy

               if actual_label_item:
                   actual_label_item.setFont(legend_font)
                   actual_label_item.opts['color'] = legend_text_color
                   actual_label_item.setText(actual_label_item.text)

    def on_grid_x_visibility_changed(self, visible: bool):
        if not self.plot_widget: return
        plot_item = self.plot_widget.getPlotItem()
        if plot_item:
            current_y_grid = self.figure_config.get('grid_y', True)
            plot_item.showGrid(x=visible, y=current_y_grid)
            self.figure_config['grid_x'] = visible

    def on_grid_y_visibility_changed(self, visible: bool):
        if not self.plot_widget: return
        plot_item = self.plot_widget.getPlotItem()
        if plot_item:
            current_x_grid = self.figure_config.get('grid_x', True)
            plot_item.showGrid(x=current_x_grid, y=visible)
            self.figure_config['grid_y'] = visible

    def on_grid_color_changed(self, new_color: QColor):
        fig_id = self.figure_id
        if new_color.isValid():
            hex_color_string = new_color.name(QColor.NameFormat.HexArgb)
            self.figure_config['grid_color'] = hex_color_string
            if self.current_theme_props:
                 self.apply_theme(self.current_theme_props)
            else:
                 logger.warning(f"Figure '{fig_id}': Cannot re-apply theme for grid color, current_theme_props is None.")
        else:
            logger.warning(f"Figure '{fig_id}': Received invalid grid color for update.")

    def on_grid_opacity_changed(self, new_opacity: float):
        fig_id = self.figure_id
        new_opacity = max(0.0, min(1.0, new_opacity))
        self.figure_config['grid_alpha'] = new_opacity
        if self.current_theme_props:
            self.apply_theme(self.current_theme_props)
        else:
            logger.warning(f"Figure '{fig_id}': Cannot re-apply theme for grid opacity, current_theme_props is None.")

    def on_title_changed(self, new_title: str):
        """Update the plot title."""
        if not self.plot_widget:
            return
        
        self.figure_config['title'] = new_title
        
        # Apply the title with current theme styling
        if self.current_theme_props:
            plot_item = self.plot_widget.getPlotItem()
            if plot_item:
                axis_fg_color = self.current_theme_props.get('axis_fg', '#808080')
                plot_title_fs = self.current_theme_props.get('plot_title_font_size', '12pt')
                title_style = f"color:{axis_fg_color}; font-size:{plot_title_fs};"
                
                if new_title:
                    plot_item.setTitle(f'<span style="{title_style}">{new_title}</span>')
                else:
                    plot_item.setTitle('')
        else:
            # Fallback without styling
            self.plot_widget.setTitle(new_title)
        
        logger.debug(f"Figure '{self.figure_id}': Title updated to '{new_title}'")

    def on_x_label_changed(self, new_label: str):
        """Update the X-axis label."""
        if not self.plot_widget:
            return
        
        self.figure_config['x_label'] = new_label
        
        # Apply the label with current theme styling  
        if self.current_theme_props:
            plot_item = self.plot_widget.getPlotItem()
            if plot_item:
                bottom_axis = plot_item.getAxis('bottom')
                if bottom_axis:
                    axis_fg_color = self.current_theme_props.get('axis_fg', '#808080')
                    axis_label_fs = self.current_theme_props.get('axis_label_font_size', '10pt')
                    label_style_dict = {'color': axis_fg_color, 'font-size': axis_label_fs}
                    bottom_axis.setLabel(text=new_label, units=bottom_axis.labelUnits, **label_style_dict)
        else:
            # Fallback without styling
            self.plot_widget.setLabel('bottom', new_label)
        
        logger.debug(f"Figure '{self.figure_id}': X-axis label updated to '{new_label}'")

    def on_y_label_changed(self, new_label: str):
        """Update the Y-axis label."""
        if not self.plot_widget:
            return
        
        self.figure_config['y_label'] = new_label
        
        # Apply the label with current theme styling
        if self.current_theme_props:
            plot_item = self.plot_widget.getPlotItem()
            if plot_item:
                left_axis = plot_item.getAxis('left')
                if left_axis:
                    axis_fg_color = self.current_theme_props.get('axis_fg', '#808080')
                    axis_label_fs = self.current_theme_props.get('axis_label_font_size', '10pt')
                    label_style_dict = {'color': axis_fg_color, 'font-size': axis_label_fs}
                    left_axis.setLabel(text=new_label, units=left_axis.labelUnits, **label_style_dict)
        else:
            # Fallback without styling
            self.plot_widget.setLabel('left', new_label)
        
        logger.debug(f"Figure '{self.figure_id}': Y-axis label updated to '{new_label}'")

    def on_toggle_zoom(self, state_or_bool):
        is_enabled = state_or_bool if isinstance(state_or_bool, bool) else (state_or_bool == Qt.CheckState.Checked.value)
        if not self.plot_widget: return
        plot_item = self.plot_widget.getPlotItem()
        view_box = plot_item.getViewBox() if plot_item else None
        if view_box:
            logger.debug(f"Figure '{self.figure_id}': Zoom/Pan mouse enabled set to {is_enabled}")
            view_box.setMouseEnabled(x=is_enabled, y=is_enabled)

    def on_y_axis_scale_changed(self, scale: str):
        if not self.plot_widget: return
        plot_item = self.plot_widget.getPlotItem()
        if plot_item:
            is_log = (scale == 'log')
            bottom_axis = plot_item.getAxis('bottom')
            current_x_log = bottom_axis.logMode if bottom_axis else False
            plot_item.setLogMode(x=current_x_log, y=is_log)
            self.figure_config['y_scale'] = scale
            logger.debug(f"Figure '{self.figure_id}': Y-axis scale set to {scale}")

    def on_x_axis_scale_changed(self, scale: str):
        if not self.plot_widget: return
        plot_item = self.plot_widget.getPlotItem()
        if plot_item:
            is_log = (scale == 'log')
            left_axis = plot_item.getAxis('left')
            current_y_log = left_axis.logMode if left_axis else False
            plot_item.setLogMode(x=is_log, y=current_y_log)
            self.figure_config['x_scale'] = scale
            logger.debug(f"Figure '{self.figure_id}': X-axis scale set to {scale}")

    def getPlotWidget(self) -> Optional[pg.PlotWidget]:
         return self.plot_widget

    # ------------------------------------------------------------------ Export --
    def export(self, export_spec):
        """Export the figure according to *export_spec*.

        The method supports 2 calling styles for backward-compatibility:

        1. ``export("png")`` – *legacy* interface used by earlier UI versions.
        2. ``export({...})``  – new interface receiving a detailed *dict* as
           emitted by the revamped *ExportSectionWidget*.
        """
        if not self.plot_widget:
            raise RuntimeError("PlotWidget is not initialised.")

        # ------------------------------------------------------------------
        # Legacy simple string interface
        # ------------------------------------------------------------------
        if isinstance(export_spec, str):
            fmt_str = export_spec.lower()
            from pyqtgraph.exporters import ImageExporter, SVGExporter, CSVExporter

            exporter_cls = None
            default_ext = fmt_str

            if fmt_str in {"png", "jpg", "jpeg", "bmp"}:
                exporter_cls = ImageExporter
                if fmt_str == "jpg":
                    default_ext = "jpeg"
            elif fmt_str == "svg":
                exporter_cls = SVGExporter
            elif fmt_str == "csv":
                exporter_cls = CSVExporter
            else:
                raise ValueError(f"Unsupported export format: {fmt_str}")

            from PyQt6.QtWidgets import QFileDialog
            from PyQt6.QtCore import Qt

            dialog_filter = f"*.{default_ext}"
            
            # Create dialog with theming options
            dialog = QFileDialog(self, "Export Figure", f"{self.figure_id}.{default_ext}")
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setNameFilter(f"{fmt_str.upper()} files ({dialog_filter})")
            dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
            dialog.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            
            # Apply theming
            try:
                from themes import apply_dialog_theme
                main_win = self.window()
                if hasattr(main_win, 'current_theme_props') and main_win.current_theme_props:
                    apply_dialog_theme(dialog, main_win.current_theme_props)
            except Exception as e:
                logger.debug(f"Could not apply dialog theme to file dialog: {e}")
            
            if dialog.exec():
                selected_files = dialog.selectedFiles()
                if selected_files:
                    file_path = selected_files[0]
                else:
                    return
            else:
                return  # user cancelled

            exporter = exporter_cls(self.plot_widget.plotItem)

            # For images, set quality for JPEG if needed
            if isinstance(exporter, ImageExporter) and fmt_str in {"jpeg", "jpg"}:
                if "quality" in exporter.parameters():
                    exporter.parameters()["quality"] = 90

            exporter.export(file_path)
            logger.info("Figure '%s' exported to %s (%s).", self.figure_id, file_path, fmt_str)
            return

        # ------------------------------------------------------------------
        # New dictionary-based interface
        # ------------------------------------------------------------------
        if not isinstance(export_spec, dict):
            raise TypeError("export_spec must be a str or dict")

        from pyqtgraph.exporters import ImageExporter, SVGExporter, CSVExporter
        import os

        file_type = export_spec.get("file_type", "image").lower()

        # Ensure directory exists (create if possible)
        directory = export_spec.get("directory", os.getcwd())
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"Cannot create export directory '{directory}': {e}") from e

        if file_type == "image":
            fmt_user = export_spec.get("image_format", "png").lower()
            # Qt's image writer expects 'jpeg' rather than 'jpg'. Keep the
            # user-visible extension unchanged, but translate for the exporter
            fmt_for_qt = "jpeg" if fmt_user == "jpg" else fmt_user

            file_path = os.path.join(directory, f"{export_spec.get('file_name', 'figure')}.{fmt_user}")

            exporter = ImageExporter(self.plot_widget.plotItem)

            # Width / height settings -------------------------------------------------
            width_val = export_spec.get("width")
            height_val = export_spec.get("height")

            try:
                if width_val:
                    params_obj = exporter.parameters()
                    # ParameterTree object – use key assignment which internally calls setValue
                    params_obj["width"] = int(width_val)
                    # Height will auto-scale to keep aspect ratio.
                    logger.debug("Applied image export width: %s px (height auto)", width_val)
            except Exception as e:
                logger.warning("Could not apply custom width/height to exporter: %s", e)

            try:
                if fmt_for_qt in {"jpeg", "jpg"} and "quality" in exporter.parameters():
                    exporter.parameters()["quality"] = 90
            except Exception:
                pass

            exporter.export(file_path)
            logger.info("Figure '%s' exported to %s (%s).", self.figure_id, file_path, fmt_user)

        elif file_type == "csv":
            file_path = os.path.join(directory, f"{export_spec.get('file_name', 'figure')}.csv")

            exporter = CSVExporter(self.plot_widget.plotItem)
            params = exporter.parameters()

            sep = export_spec.get("separator", ",")
            if "separator" in params:
                params["separator"] = sep

            precision_val = export_spec.get("precision")
            if precision_val is not None and "precision" in params:
                params["precision"] = int(precision_val)

            exporter.export(file_path)
            logger.info("Figure '%s' exported to %s (csv).", self.figure_id, file_path)

        else:
            raise ValueError(f"Unsupported file_type in export_spec: {file_type}")

    # ---------------- Helper for z_column expansion ----------------
    def _add_line_scatter_with_z(self, base_config: Dict[str, Any], handler: Callable):
        source = base_config.get('source'); x_col = base_config.get('x_column'); y_col = base_config.get('y_column'); z_col = base_config.get('z_column')
        if not all([source, x_col, y_col, z_col]):
            logger.error(f"Item '{base_config.get('id')}' is missing required fields for z-column plotting.")
            return

        df = self.data_handler.load_data(source)
        if df is None or z_col not in df.columns or x_col not in df.columns or y_col not in df.columns:
            logger.error(f"Item '{base_config.get('id')}' columns not found in data.")
            return

        df_clean = df[[x_col, y_col, z_col]].dropna()
        if df_clean.empty:
            logger.warning(f"Item '{base_config.get('id')}' resulted in no data after dropping NaNs.")
            return

        # Determine unique z values sorted
        unique_z = sorted(df_clean[z_col].unique())
        n_z = len(unique_z)

        color_scheme = base_config.get('color_scheme', 'single')
        use_colormap = color_scheme and color_scheme.lower() not in ('single', 'default')

        if use_colormap:
            try:
                cmap = pg.colormap.get(color_scheme)
            except Exception:
                cmap = pg.colormap.get('viridis')
                logger.warning(f"Unknown colormap '{color_scheme}'. Falling back to viridis.")

        show_colorbar = bool(base_config.get('show_colorbar', False)) and use_colormap
        legend_visible = bool(base_config.get('legend_visible', True))

        # Ensure legend exists before adding slices so entries appear
        if legend_visible:
            plot_item = self.plot_widget.getPlotItem()
            if plot_item and not plot_item.legend:
                try:
                    self.plot_widget.addLegend()
                except Exception as e:
                    logger.warning(f"Could not add legend: {e}")

        colorbar_added = False

        for idx, z_val in enumerate(unique_z):
            slice_df = df_clean[df_clean[z_col] == z_val]
            x_slice = slice_df[x_col].tolist()
            y_slice = slice_df[y_col].tolist()

            cfg_copy = dict(base_config)  # shallow copy
            if legend_visible:
                cfg_copy['legend_name'] = f"{z_col} = {z_val}"
            else:
                cfg_copy['legend_name'] = None

            if use_colormap:
                color_ratio = idx / (n_z - 1) if n_z > 1 else 0.5
                rgb_tuple = cmap.map(color_ratio, mode='byte')  # returns 0-255 RGBA
                hex_color = '#{0:02X}{1:02X}{2:02X}'.format(*rgb_tuple[:3])
                if base_config['type'] == 'line':
                    cfg_copy['line_color'] = hex_color
                else:
                    cfg_copy['symbol_color'] = hex_color
                    cfg_copy['symbol_outline'] = hex_color

            plot_item = handler(cfg_copy, x_slice, y_slice)
            if plot_item:
                self.plot_widget.addItem(plot_item)
                self.plot_items.append({'id': f"{cfg_copy.get('id')}_{idx}", 'item': plot_item})

        # Add colorbar once per z-series item if requested
        if show_colorbar and use_colormap and unique_z and not colorbar_added:
            try:
                vmin, vmax = float(min(unique_z)), float(max(unique_z))
                cbar = pg.ColorBarItem(values=(vmin, vmax), colorMap=cmap, label=z_col, width=10)
                plot_item = self.plot_widget.getPlotItem()
                plot_item.layout.addItem(cbar, 2, 3)

                # dynamic update of colours when handles moved
                def _recolor_lines():
                    low, high = cbar.levels()
                    span = high - low if high != low else 1.0
                    for idx2, z_val2 in enumerate(unique_z):
                        ratio = (z_val2 - low) / span
                        rgb = cmap.map(ratio, mode='byte')
                        hex_col = '#{0:02X}{1:02X}{2:02X}'.format(*rgb[:3])
                        line_item = self.plot_items[-n_z + idx2]['item']  # assume recently added order
                        if isinstance(line_item, pg.PlotDataItem):
                            pen = pg.mkPen(hex_col, width=cfg_copy.get('line_width', 1))
                            line_item.setPen(pen)
                        else:
                            line_item.setBrush(pg.mkBrush(hex_col))

                cbar.sigLevelsChanged.connect(_recolor_lines)

                colorbar_added = True
            except Exception as e:
                logger.warning(f"Unable to create colorbar: {e}")
