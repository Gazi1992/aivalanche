from __future__ import annotations

"""Reusable SVG icon rendering & caching utilities.

Usage:
    icon_mgr = IconManager(base_path="components/svg_templates")
    icon_mgr.register_icon("sidebar_logo", "logo_template.svg")
    pix = icon_mgr.get_pixmap("sidebar_logo", QSize(48,48), fill_color="#FFFFFF")

The underlying template SVG must contain placeholders like ``{fill_color}``
that will be substituted via ``str.format`` before rendering.
"""

import os
import re
from functools import lru_cache
from typing import Dict, Optional

from PyQt6.QtCore import QSize, QByteArray, Qt
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QColor
from PyQt6.QtSvg import QSvgRenderer
import logging

logger = logging.getLogger(__name__)


class SvgIconComponent:
    """Represents one SVG template that can be rendered in arbitrary colours/sizes."""

    def __init__(self, template_path: str):
        if not os.path.exists(template_path):
            raise FileNotFoundError(template_path)
        self.template_path = template_path
        with open(template_path, "r", encoding="utf-8") as fh:
            self.template_content = fh.read()

        # Extract aspect ratio from the viewBox attribute (format: "minX minY width height")
        viewbox_match = re.search(r"viewBox=\"([\d.\s]+)\"", self.template_content)
        if viewbox_match:
            try:
                _, _, width_str, height_str = viewbox_match.group(1).split()
                width = float(width_str)
                height = float(height_str)
                # Avoid division by zero
                self.aspect_ratio: Optional[float] = width / height if height != 0 else None
            except ValueError:
                logger.warning("Could not parse viewBox in %s", template_path)
                self.aspect_ratio = None
        else:
            self.aspect_ratio = None

    # ---------------------------------------------------------------- cache key helper
    @staticmethod
    def _cache_key(width: int, height: int, params: Dict[str, str]):
        # params dict → sorted tuple for hashing
        return width, height, tuple(sorted(params.items()))

    @lru_cache(maxsize=256)
    def _render_cached(self, width: int, height: int, key):  # key unused (just for caching uniqueness)
        # key already encodes size & params via lru_cache's wrapper
        width, height, params_tuple = key
        params_dict = dict(params_tuple)

        svg_source = self.template_content.format(**params_dict)
        svg_data = QByteArray(svg_source.encode("utf-8"))
        renderer = QSvgRenderer(svg_data)
        if not renderer.isValid():
            logger.warning("Invalid SVG after formatting %s", self.template_path)
            pm = QPixmap(width, height)
            pm.fill(Qt.GlobalColor.transparent)
            return pm

        pm = QPixmap(width, height)
        pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm)
        renderer.render(painter)
        painter.end()
        return pm

    def get_pixmap(self, size: QSize, **params) -> QPixmap:
        # Defaults
        defaults = {
            "fill_color": "black",
            "stroke_color": "none",
            "stroke_width": "1",
        }
        defaults.update(params)
        key = self._cache_key(size.width(), size.height(), defaults)
        return self._render_cached(size.width(), size.height(), key)

    def get_icon(self, size: QSize, **params) -> QIcon:
        return QIcon(self.get_pixmap(size=size, **params))


class IconManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._components: Dict[str, SvgIconComponent] = {}

    def register_icon(self, name: str, template_filename: str):
        path = os.path.join(self.base_path, template_filename)
        try:
            self._components[name] = SvgIconComponent(path)
        except FileNotFoundError:
            logger.error("SVG template missing: %s", path)

    def get_pixmap(self, name: str, size: QSize, **params) -> QPixmap:
        comp = self._components.get(name)
        if not comp:
            logger.error("Icon '%s' not registered", name)
            return QPixmap(size)  # empty
        return comp.get_pixmap(size=size, **params)

    def get_icon(self, name: str, size: QSize, **params) -> QIcon:
        comp = self._components.get(name)
        if not comp:
            return QIcon()
        return comp.get_icon(size=size, **params)

    # ------------------------------------------------------------------ Aspect ratio helper
    def get_aspect_ratio(self, name: str) -> Optional[float]:
        """Return the width/height aspect ratio for a registered SVG template.

        Parameters
        ----------
        name : str
            The key under which the icon was registered.

        Returns
        -------
        float | None
            The computed aspect ratio or *None* if unavailable/invalid.
        """
        comp = self._components.get(name)
        if not comp:
            logger.error("Icon '%s' not registered", name)
            return None
        return comp.aspect_ratio 