import json
import os
import logging
from typing import Dict, List, Any, Optional

from config_schema import SchemaRegistry, ConfigField

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loads and validates configuration files for the visualization tool."""

    def __init__(self, config_file: str):
        self.config_path = config_file
        self.config = {}
        self.validation_errors = []
        try:
            self.config = self._load_config()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load configuration: {e}")
            # Config remains empty, validation should fail later if needed

    def _load_config(self) -> Dict:
        """Loads the configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                logger.info(f"Loading configuration from: {self.config_path}")
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            # Raise with more context
            raise json.JSONDecodeError(f"Invalid JSON in config '{self.config_path}': {e.msg}", e.doc, e.pos) from e
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading {self.config_path}: {e}")
            return {}

    def validate_config(self) -> bool:
        """Validates the configuration file structure against the schemas."""
        self.validation_errors = []
        logger.info("Starting configuration validation...")

        if not isinstance(self.config, dict) or not self.config:
            self.validation_errors.append("Configuration is empty or not a valid JSON object.")
            logger.error("Configuration validation failed: Root is not a valid object.")
            return False

        self._recursive_validate(self.config, SchemaRegistry.get_general_schema(), "General config")

        if not self.validation_errors:
            logger.info("Configuration validation successful.")
        else:
            logger.warning(f"Configuration validation completed with {len(self.validation_errors)} errors/warnings.")
            for error in self.validation_errors:
                logger.warning(f"  - {error}")
        return len(self.validation_errors) == 0

    def _recursive_validate(self, config_section: Dict, schema: Dict[str, ConfigField], context: str):
        self._validate_section(config_section, schema, context)
        self._check_unrecognized_fields_for_section(config_section, schema, context)

        if "grid_layout" in config_section and isinstance(config_section.get("grid_layout"), dict):
            self._recursive_validate(config_section["grid_layout"], SchemaRegistry.get_grid_layout_schema(), f"{context} -> grid_layout")

        if "figures" in config_section and isinstance(config_section.get("figures"), list):
            for i, figure in enumerate(config_section["figures"]):
                if isinstance(figure, dict):
                    figure_context = f"{context} -> figures[{i}]"
                    self._recursive_validate(figure, SchemaRegistry.get_base_figure_schema(), figure_context)
                    if "items" in figure and isinstance(figure.get("items"), list):
                        for j, item in enumerate(figure["items"]):
                            if isinstance(item, dict):
                                plot_type = item.get("type")
                                item_schema = SchemaRegistry.get_plot_type_schema(plot_type) if plot_type else None
                                if item_schema:
                                    item_context = f"{figure_context} -> items[{j}] (type: {plot_type})"
                                    self._recursive_validate(item, item_schema, item_context)
                                else:
                                    self.validation_errors.append(f"{figure_context} -> items[{j}]: unsupported plot type: {plot_type}")
                            else:
                                self.validation_errors.append(f"{figure_context} -> items[{j}]: must be an object")
                else:
                    self.validation_errors.append(f"{context} -> figures[{i}]: must be an object")

    def _validate_section(self, config_section: Dict, schema: Dict[str, ConfigField], context: str) -> None:
        """Validate a section of the configuration against its schema."""
        for field_name, field_schema in schema.items():
            if field_schema.required and field_name not in config_section:
                self.validation_errors.append(f"{context}: Required field '{field_name}' is missing")
                continue
            if field_name in config_section:
                value = config_section[field_name]
                self._validate_field_value(field_name, value, field_schema, context)

    def _validate_field_value(self, field_name: str, value: Any, field_schema: ConfigField, context: str) -> None:
        """Validate a single field value against its schema definition."""
        is_correct_type = any(isinstance(value, t) for t in field_schema.field_type if t is not type(None))
        if type(None) in field_schema.field_type and value is None:
             is_correct_type = True
        if not is_correct_type:
            expected_types = [t.__name__ if t is not None else 'None' for t in field_schema.field_type]
            self.validation_errors.append(
                f"{context}: Field '{field_name}' must be of type {' or '.join(expected_types)}, got {type(value).__name__}"
            )
            return

        if field_schema.possible_values is not None:
            is_in_possible = value in field_schema.possible_values
            if not is_in_possible and not (value is None and type(None) in field_schema.field_type):
                 self.validation_errors.append(
                    f"{context}: Field '{field_name}' value '{value}' is not allowed. Must be one of: {field_schema.possible_values}"
                 )

        if field_schema.validator:
            if not (value is None and type(None) in field_schema.field_type): # Skip validator for None unless explicitly handled by validator logic
                try:
                    if not field_schema.validator(value):
                         self.validation_errors.append(
                             f"{context}: Field '{field_name}' value '{value}' failed custom validation."
                         )
                except Exception as e:
                     self.validation_errors.append(
                         f"{context}: Field '{field_name}' validator function failed for value '{value}' with error: {e}"
                     )
                     logger.exception(f"Validator failed for field {field_name} in {context}")

    def _check_unrecognized_fields_for_section(self, config_section: Dict, schema: Dict, context: str) -> None:
        """Warn about fields present in the config but not defined in the schema."""
        allowed_fields = set(schema.keys())
        # Extend allowed fields for sections that have nested structures defined elsewhere
        if context == "General config":
            allowed_fields.update(["figures", "grid_layout"])
        elif "figures[" in context and "items" not in context:
            allowed_fields.add("items")

        for field_name in config_section.keys():
            if field_name not in allowed_fields:
                msg = f"{context}: Unrecognized field '{field_name}' found."
                if msg not in self.validation_errors:
                     self.validation_errors.append(msg)
                     logger.warning(msg)

    def apply_defaults(self) -> None:
        """Apply default values to missing optional fields in the configuration."""
        if not isinstance(self.config, dict):
            logger.warning("Cannot apply defaults: Configuration is not a dictionary.")
            return

        logger.info("Applying configuration defaults...")
        self._apply_defaults_to_section(self.config, SchemaRegistry.get_general_schema())

        if "grid_layout" not in self.config:
            self.config["grid_layout"] = {}
        if isinstance(self.config.get("grid_layout"), dict):
            self._apply_defaults_to_section(self.config["grid_layout"], SchemaRegistry.get_grid_layout_schema())

        if "figures" in self.config and isinstance(self.config["figures"], list):
            for figure in self.config["figures"]:
                if not isinstance(figure, dict): continue
                self._apply_defaults_to_section(figure, SchemaRegistry.get_base_figure_schema())
                if "items" in figure and isinstance(figure["items"], list):
                    for item in figure["items"]:
                        if not isinstance(item, dict): continue
                        plot_type = item.get("type")
                        item_schema = SchemaRegistry.get_plot_type_schema(plot_type) if plot_type else None
                        if item_schema:
                            self._apply_defaults_to_section(item, item_schema)

    def _apply_defaults_to_section(self, config_section: Dict, schema: Dict[str, ConfigField]) -> None:
        """Apply default values to a specific section of the configuration."""
        for field_name, field_schema in schema.items():
            if field_name not in config_section and not field_schema.required:
                 config_section[field_name] = field_schema.default

    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors and warnings."""
        return self.validation_errors

    def get_app_title(self) -> str:
        """Get the application title from the configuration."""
        return self.config.get('app_title', 'Visualization Tool')

    def get_margins(self) -> Dict[str, int]:
        """Get the margin settings from the configuration. Assumes defaults applied."""
        return {
            'left': self.config.get('left_margin', 10),
            'right': self.config.get('right_margin', 10),
            'top': self.config.get('top_margin', 10),
            'bottom': self.config.get('bottom_margin', 10)
        }

    def get_theme(self) -> str:
        """Get the theme setting from the configuration."""
        return self.config.get('theme', 'light')

    def set_theme(self, new_theme: str):
        """Updates the theme in the loaded configuration dictionary."""
        general_schema = SchemaRegistry.get_general_schema()
        theme_field_schema = general_schema.get('theme')
        if theme_field_schema:
            if theme_field_schema.possible_values and new_theme not in theme_field_schema.possible_values:
                logger.warning(f"Attempted to set invalid theme '{new_theme}'. Allowed: {theme_field_schema.possible_values}. Not changing theme.")
                return
            self.config['theme'] = new_theme
            logger.info(f"Application theme changed in config object to: {new_theme}")
        else:
            logger.warning("Attempted to set theme, but 'theme' field not found in general schema. Storing anyway.")
            self.config['theme'] = new_theme

    def get_grid_layout(self) -> Dict[str, Any]:
        """Get the grid layout configuration."""
        grid_layout = self.config.get('grid_layout', {})
        if not isinstance(grid_layout, dict): # Should be a dict after apply_defaults if it was missing
            logger.warning("Grid layout configuration is not a dictionary. Returning empty layout.")
            return {}
        return grid_layout

    def get_figures(self) -> List[Dict]:
        """Get the list of figures from the configuration."""
        figures = self.config.get('figures', [])
        if not isinstance(figures, list):
             logger.warning("'figures' configuration is not a list. Returning empty list.")
             return []
        return figures

    def get_figure_by_id(self, figure_id: str) -> Optional[Dict]:
        """Get a figure by its ID."""
        for figure in self.get_figures():
            if isinstance(figure, dict) and figure.get('id') == figure_id:
                return figure
        return None
