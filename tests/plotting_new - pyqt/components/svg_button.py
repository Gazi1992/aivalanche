from __future__ import annotations

"""PushButton subclass that renders an SVG icon via IconManager and updates it
according to hover / pressed / disabled states.
"""

from PyQt6.QtWidgets import QPushButton, QStyleOptionButton
from PyQt6.QtCore import QSize, QEvent, Qt, QRect
from PyQt6.QtGui import QMouseEvent, QIcon, QPainter
from .icon_manager import IconManager


class SvgButton(QPushButton):
    """A QPushButton that uses *IconManager* to render template-based SVG icons.

    Parameters
    ----------
    icon_name : str
        The key registered with ``IconManager.register_icon``.
    icon_manager : IconManager
        Shared manager instance that holds template definitions.
    text : str, optional
        Optional button label.
    size : QSize, optional
        Target button size (defaults 24×24). When aspect_ratio is provided,
        this becomes the button size while icon scales to fit proportionally.
    aspect_ratio : float, optional
        Aspect ratio (width/height) of the SVG content. When provided,
        the icon will be scaled to fit within 'size' while preserving proportions.
    enable_hover : bool, optional
        Whether to enable hover state.
    enable_press : bool, optional
        Whether to enable press state.
    """

    def __init__(self, icon_name: str, icon_manager: IconManager, text: str = "", *, size: QSize | None = None, aspect_ratio: float | None = None, enable_hover: bool = False, enable_press: bool = False, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SvgButton")
        self.icon_name = icon_name
        self.icon_manager = icon_manager
        
        # Determine aspect ratio: caller-supplied value overrides automatic detection
        resolved_ar = aspect_ratio
        if resolved_ar is None:
            resolved_ar = self.icon_manager.get_aspect_ratio(icon_name)

        if resolved_ar is not None and size is not None:
            # Preserve SVG proportions within the requested button size
            self.current_icon_size = self._calculate_aspect_ratio_size(size, resolved_ar)
            # Button keeps the target size, icon scales inside
            self.setFixedSize(size)
        else:
            # Fallback: no aspect ratio available – icon fills button equally
            self.current_icon_size = size or QSize(24, 24)

        # Default colour scheme – can be overridden via set_icon_parameters
        self.icon_params_normal = {"fill_color": "#333333", "stroke_color": "none"}
        self.icon_params_hover = {"fill_color": "#0078D7", "stroke_color": "none"}
        self.icon_params_pressed = {"fill_color": "#005A9E", "stroke_color": "none"}
        self.icon_params_disabled = {"fill_color": "#AAAAAA", "stroke_color": "none"}

        self.enable_hover = enable_hover
        self.enable_press = enable_press

        self.setIconSize(self.current_icon_size)
        self.setMouseTracking(True)  # ensure hover events
        self._update_icon()

    # ---------------------------------------------------------------- API
    def set_icon_parameters(self, *, normal=None, hover=None, pressed=None, disabled=None):
        if normal:
            self.icon_params_normal = normal
        if hover:
            self.icon_params_hover = hover
        if pressed:
            self.icon_params_pressed = pressed
        if disabled:
            self.icon_params_disabled = disabled
        self._update_icon()

    # ---------------------------------------------------------------- Overrides
    def setIconSize(self, size: QSize):  # noqa: N802 (Qt API)
        super().setIconSize(size)
        self.current_icon_size = size
        self._update_icon()

    # ---------------------------------------------------------------- Internal helpers
    def _calculate_aspect_ratio_size(self, target_size: QSize, aspect_ratio: float) -> QSize:
        """Calculate icon size that preserves aspect ratio within target size.
        
        Parameters
        ----------
        target_size : QSize
            The target button/container size
        aspect_ratio : float
            The aspect ratio (width/height) of the original SVG
            
        Returns
        -------
        QSize
            Icon size that fits within target_size while preserving aspect ratio
        """
        target_width = target_size.width()
        target_height = target_size.height()
        
        # Scale to fit target size while preserving aspect ratio
        if aspect_ratio < 1.0:  # taller than wide
            icon_width = int(target_width * aspect_ratio)
            icon_height = target_height
        else:  # wider than tall or square
            icon_width = target_width
            icon_height = int(target_height / aspect_ratio)
            
        return QSize(icon_width, icon_height)

    def _params_for_current_state(self):
        if not self.isEnabled():
            return self.icon_params_disabled
        if self.isDown() and self.enable_press:
            return self.icon_params_pressed
        if self.underMouse() and self.enable_hover:
            return self.icon_params_hover
        return self.icon_params_normal

    def _update_icon(self):
        params = self._params_for_current_state()
        icon: QIcon = self.icon_manager.get_icon(self.icon_name, size=self.current_icon_size, **params)
        super().setIcon(icon)

    # ---------------------------------------------------------------- Event handling
    def event(self, e: QEvent):  # noqa: N802
        # HoverEnter/HoverLeave are better than enterEvent/leaveEvent in some styles
        if e.type() in (QEvent.Type.HoverEnter, QEvent.Type.HoverLeave, QEvent.Type.EnabledChange):
            self._update_icon()
        return super().event(e)

    def mousePressEvent(self, ev: QMouseEvent):  # noqa: N802
        super().mousePressEvent(ev)
        self._update_icon()

    def mouseReleaseEvent(self, ev: QMouseEvent):  # noqa: N802
        super().mouseReleaseEvent(ev)
        self._update_icon()