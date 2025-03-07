import unittest
import os
import json
import tempfile
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from aivalanche_lib import Parameters

class TestParameters(unittest.TestCase):
    """Test cases for the Parameters class."""

    def setUp(self):
        """Set up test cases."""
        self.sample_params = [
            {"name": "alpha", "min": 0.1, "max": 1.0, "default": 0.5, "scale": "lin", "mode": "variable"},
            {"name": "beta", "min": 1.0, "max": 100.0, "default": 10.0, "scale": "log", "mode": "variable"},
            {"name": "gamma", "min": -1.0, "max": 1.0, "default": 0.0, "scale": "lin", "mode": "fixed"}
        ]

        # Create a temporary CSV file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "test_params.csv")
        self.json_path = os.path.join(self.temp_dir.name, "test_params.json")

        # Write to CSV
        pd.DataFrame(self.sample_params).to_csv(self.csv_path, index=False)

        # Write to JSON
        with open(self.json_path, 'w') as f:
            json.dump(self.sample_params, f)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_init_from_list(self):
        """Test initialization from a list of dictionaries."""
        params = Parameters(self.sample_params)
        self.assertEqual(params.nr_parameters, 3)
        self.assertEqual(params.nr_variable_parameters, 2)
        self.assertEqual(params.nr_fixed_parameters, 1)

    def test_init_from_csv(self):
        """Test initialization from a CSV file."""
        params = Parameters(self.csv_path)
        self.assertEqual(params.nr_parameters, 3)
        self.assertEqual(params.file, self.csv_path)

    def test_init_from_json(self):
        """Test initialization from a JSON file."""
        params = Parameters(self.json_path)
        self.assertEqual(params.nr_parameters, 3)
        self.assertEqual(params.file, self.json_path)

    def test_init_from_dataframe(self):
        """Test initialization from a pandas DataFrame."""
        df = pd.DataFrame(self.sample_params)
        params = Parameters(df)
        self.assertEqual(params.nr_parameters, 3)
        self.assertIsNone(params.file)

    def test_min_max_swap(self):
        """Test automatic swapping of min/max values."""
        swapped_params = [
            {"name": "delta", "min": 2.0, "max": 1.0}  # min > max, should be swapped
        ]
        params = Parameters(swapped_params)
        param = params.get_parameter("delta")
        self.assertEqual(param["min"], 1.0)
        self.assertEqual(param["max"], 2.0)

    def test_default_value_generation(self):
        """Test automatic generation of default values."""
        no_default_params = [
            {"name": "epsilon", "min": 1.0, "max": 3.0}  # no default provided
        ]
        params = Parameters(no_default_params)
        param = params.get_parameter("epsilon")
        self.assertEqual(param["default"], 2.0)  # Should be (1+3)/2

    def test_scale_determination(self):
        """Test automatic scale determination."""
        scale_test_params = [
            {"name": "pos_wide", "min": 0.01, "max": 10000.0},  # Should be log (ratio > 100)
            {"name": "mixed_sign", "min": -10.0, "max": 10.0},  # Should be lin (different signs)
            {"name": "pos_narrow", "min": 1.0, "max": 10.0}     # Should be lin (ratio < 100)
        ]
        params = Parameters(scale_test_params)
        self.assertEqual(params.get_parameter("pos_wide")["scale"], "log")
        self.assertEqual(params.get_parameter("mixed_sign")["scale"], "lin")
        self.assertEqual(params.get_parameter("pos_narrow")["scale"], "lin")

    def test_parameter_scaling(self):
        """Test parameter scaling."""
        params = Parameters(self.sample_params)

        # Check log scaling for beta
        beta_scaled = params.all_parameters_scaled[params.all_parameters_scaled["name"] == "beta"].iloc[0]
        self.assertAlmostEqual(beta_scaled["min"], math.log10(1.0))  # log10(1) = 0
        self.assertAlmostEqual(beta_scaled["max"], math.log10(100.0))  # log10(100) = 2

        # Check linear parameter is unchanged
        alpha_scaled = params.all_parameters_scaled[params.all_parameters_scaled["name"] == "alpha"].iloc[0]
        self.assertEqual(alpha_scaled["min"], 0.1)
        self.assertEqual(alpha_scaled["max"], 1.0)

    def test_parameter_normalization(self):
        """Test parameter normalization."""
        params = Parameters(self.sample_params)

        # All normalized parameters should have min=0 and max=1
        for _, row in params.all_parameters_normed.iterrows():
            self.assertEqual(row["min"], 0.0)
            self.assertEqual(row["max"], 1.0)

        # Check default normalization for alpha: (0.5-0.1)/(1.0-0.1) = 0.444...
        alpha_normed = params.all_parameters_normed[params.all_parameters_normed["name"] == "alpha"].iloc[0]
        self.assertAlmostEqual(alpha_normed["default"], (0.5-0.1)/(1.0-0.1))

        # Check gamma normalization (for fixed parameter): (0-(-1))/(1-(-1)) = 0.5
        gamma_normed = params.all_parameters_normed[params.all_parameters_normed["name"] == "gamma"].iloc[0]
        self.assertAlmostEqual(gamma_normed["default"], 0.5)

    def test_add_parameter(self):
        """Test adding a parameter."""
        params = Parameters(self.sample_params)
        params.add_parameter("delta", 0.0, 1.0, 0.5, "lin", "variable")
        self.assertEqual(params.nr_parameters, 4)
        self.assertEqual(params.get_parameter("delta")["default"], 0.5)

        # Check if it's also in scaled and normed DataFrames
        self.assertIn("delta", params.all_parameters_scaled["name"].values)
        self.assertIn("delta", params.all_parameters_normed["name"].values)

    def test_remove_parameter(self):
        """Test removing a parameter."""
        params = Parameters(self.sample_params)
        params.remove_parameter("alpha")
        self.assertEqual(params.nr_parameters, 2)
        self.assertNotIn("alpha", params.all_parameters["name"].values)
        self.assertNotIn("alpha", params.all_parameters_scaled["name"].values)
        self.assertNotIn("alpha", params.all_parameters_normed["name"].values)

    def test_get_parameter(self):
        """Test getting a parameter."""
        params = Parameters(self.sample_params)
        param = params.get_parameter("beta")
        self.assertEqual(param["name"], "beta")
        self.assertEqual(param["min"], 1.0)
        self.assertEqual(param["max"], 100.0)

        # Test non-existent parameter
        self.assertIsNone(params.get_parameter("nonexistent"))

    def test_property_access(self):
        """Test property access for different parameter types."""
        params = Parameters(self.sample_params)

        # Test variable parameters
        self.assertEqual(len(params.variable_parameters), 2)
        self.assertIn("alpha", params.variable_parameters_names)
        self.assertIn("beta", params.variable_parameters_names)

        # Test fixed parameters
        self.assertEqual(len(params.fixed_parameters), 1)
        self.assertEqual(params.fixed_parameters.iloc[0]["name"], "gamma")

        # Test normed parameters
        self.assertEqual(len(params.variable_parameters_normed), 2)
        self.assertEqual(len(params.fixed_parameters_normed), 1)

    def test_random_parameters(self):
        """Test generating random parameters."""
        params = Parameters(self.sample_params)
        random_params = params.generate_random_parameters()

        # Check that all parameters are present
        self.assertEqual(set(random_params.keys()), {"alpha", "beta", "gamma"})

        # Check that fixed parameter has default value
        self.assertEqual(random_params["gamma"], 0.0)

        # Check that variable parameters are within bounds
        self.assertGreaterEqual(random_params["alpha"], 0.1)
        self.assertLessEqual(random_params["alpha"], 1.0)
        self.assertGreaterEqual(random_params["beta"], 1.0)
        self.assertLessEqual(random_params["beta"], 100.0)

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Missing required column
        invalid_params = [
            {"name": "test", "min": 0.0}  # missing max
        ]
        params = Parameters(invalid_params)
        self.assertIsNotNone(params.error_parsing)

        # Invalid file path
        params = Parameters("nonexistent_file.csv")
        self.assertIsNotNone(params.error_parsing)

        # Invalid data type
        params = Parameters(123)  # not a supported data type
        self.assertIsNotNone(params.error_parsing)

    def test_default_parameters(self):
        """Test getting default parameters."""
        params = Parameters(self.sample_params)
        defaults = params.get_default_parameters()

        self.assertEqual(defaults["alpha"], 0.5)
        self.assertEqual(defaults["beta"], 10.0)
        self.assertEqual(defaults["gamma"], 0.0)

    def test_write_to_file(self):
        """Test writing parameters to file."""
        params = Parameters(self.sample_params)

        # Write to a new CSV file
        output_csv = os.path.join(self.temp_dir.name, "output_params.csv")
        params.write_to_file(output_csv)
        self.assertTrue(os.path.exists(output_csv))

        # Read it back and verify
        params2 = Parameters(output_csv)
        self.assertEqual(params2.nr_parameters, 3)

        # Write to a new JSON file
        output_json = os.path.join(self.temp_dir.name, "output_params.json")
        params.write_to_file(output_json)
        self.assertTrue(os.path.exists(output_json))

    def test_denormalize_parameters(self):
        """Test denormalizing parameters from [0,1] range back to scaled range."""
        # Create parameters with different scale types
        test_params = [
            {"name": "linear_param", "min": 10.0, "max": 20.0, "default": 15.0, "scale": "lin", "mode": "variable"},
            {"name": "log_param", "min": 0.1, "max": 1000.0, "default": 10.0, "scale": "log", "mode": "variable"},
            {"name": "neglog_param", "min": -1000.0, "max": -0.1, "default": -10.0, "scale": "log", "mode": "variable"},
            {"name": "fixed_param", "min": 0.0, "max": 1.0, "default": 0.5, "scale": "lin", "mode": "fixed"}
        ]

        params = Parameters(test_params)

        # Create normalized data (in the [0,1] range)
        norm_data = pd.DataFrame({
            "linear_param": [0.0, 0.5, 1.0],
            "log_param": [0.0, 0.5, 1.0],
            "neglog_param": [0.0, 0.5, 1.0]
        })

        # Denormalize parameters
        denorm_data = params.denormalize_parameters(norm_data)

        # Check linear parameter denormalization
        # [0, 0.5, 1] should be mapped to [10, 15, 20]
        self.assertAlmostEqual(denorm_data["linear_param"][0], 10.0)
        self.assertAlmostEqual(denorm_data["linear_param"][1], 15.0)
        self.assertAlmostEqual(denorm_data["linear_param"][2], 20.0)

        # Check that fixed parameters are included
        self.assertIn("fixed_param", denorm_data.columns)
        self.assertEqual(denorm_data["fixed_param"][0], 0.5)

        # Test with list of dictionaries
        norm_data_list = [
            {"linear_param": 0.0, "log_param": 0.0, "neglog_param": 0.0},
            {"linear_param": 1.0, "log_param": 1.0, "neglog_param": 1.0}
        ]
        denorm_data_list = params.denormalize_parameters(norm_data_list)

        # Check format and values
        self.assertIsInstance(denorm_data_list, list)
        self.assertIsInstance(denorm_data_list[0], dict)
        self.assertAlmostEqual(denorm_data_list[0]["linear_param"], 10.0)
        self.assertAlmostEqual(denorm_data_list[1]["linear_param"], 20.0)

        # Test validation - partial data should raise an error
        with self.assertRaises(ValueError):
            params.denormalize_parameters(pd.DataFrame({"linear_param": [0.5]}))

        with self.assertRaises(ValueError):
            params.denormalize_parameters(pd.DataFrame({"linear_param": [0.5], "log_param": [0.5]}))

        # Test without fixed parameters
        no_fixed = params.denormalize_parameters(norm_data, include_fixed_parameters=False)
        self.assertNotIn("fixed_param", no_fixed.columns)

        # Test with extra parameters (should raise error)
        with self.assertRaises(ValueError):
            extra_data = norm_data.copy()
            extra_data["extra_param"] = [0.5, 0.5, 0.5]
            params.denormalize_parameters(extra_data)

    def test_descale_parameters(self):
        """Test applying inverse scaling transformations."""
        # Create parameters with different scale types
        test_params = [
            {"name": "linear_param", "min": 10.0, "max": 20.0, "default": 15.0, "scale": "lin", "mode": "variable"},
            {"name": "log_param", "min": 0.1, "max": 1000.0, "default": 10.0, "scale": "log", "mode": "variable"},
            {"name": "neglog_param", "min": -1000.0, "max": -0.1, "default": -10.0, "scale": "log", "mode": "variable"}
        ]

        params = Parameters(test_params)

        # Create scaled data (after denormalization but before descaling)
        scaled_data = pd.DataFrame({
            "linear_param": [10.0, 15.0, 20.0],  # Linear parameters don't change
            "log_param": [0.0, 1.5, 3.0],       # These are log10 values
            "neglog_param": [-3.0, -1.5, 0.0]   # These are -log10(-x) values
        })

        # Descale parameters
        descaled_data = params.descale_parameters(scaled_data)

        # Check results
        # Linear parameters remain unchanged
        self.assertAlmostEqual(descaled_data["linear_param"][0], 10.0)
        self.assertAlmostEqual(descaled_data["linear_param"][1], 15.0)
        self.assertAlmostEqual(descaled_data["linear_param"][2], 20.0)

        # Log parameters: 10^value
        self.assertAlmostEqual(descaled_data["log_param"][0], 1.0)  # 10^0 = 1
        self.assertAlmostEqual(descaled_data["log_param"][1], 31.622776601683793)  # 10^1.5 ≈ 31.6
        self.assertAlmostEqual(descaled_data["log_param"][2], 1000.0)  # 10^3 = 1000

        # Neglog parameters: -10^(-value)
        self.assertAlmostEqual(descaled_data["neglog_param"][0], -1000.0)  # -10^-(-3) = -10^3 = -1000
        self.assertAlmostEqual(descaled_data["neglog_param"][1], -31.622776601683793)  # -10^-(-1.5) ≈ -31.6
        self.assertAlmostEqual(descaled_data["neglog_param"][2], -1.0)  # -10^-0 = -1

        # Test with list of dictionaries
        scaled_data_list = [
            {"linear_param": 10.0, "log_param": 0.0, "neglog_param": -3.0},
            {"linear_param": 20.0, "log_param": 3.0, "neglog_param": 0.0}
        ]
        descaled_data_list = params.descale_parameters(scaled_data_list)

        # Check format and values
        self.assertIsInstance(descaled_data_list, list)
        self.assertIsInstance(descaled_data_list[0], dict)
        self.assertAlmostEqual(descaled_data_list[0]["log_param"], 1.0)
        self.assertAlmostEqual(descaled_data_list[1]["log_param"], 1000.0)
        self.assertAlmostEqual(descaled_data_list[0]["neglog_param"], -1000.0)
        self.assertAlmostEqual(descaled_data_list[1]["neglog_param"], -1.0)

    def test_denormalize_and_descale_parameters(self):
        """Test combined denormalization and descaling."""
        # Create parameters with different scale types
        test_params = [
            {"name": "linear_param", "min": 10.0, "max": 20.0, "default": 15.0, "scale": "lin", "mode": "variable"},
            {"name": "log_param", "min": 0.1, "max": 1000.0, "default": 10.0, "scale": "log", "mode": "variable"},
            {"name": "neglog_param", "min": -1000.0, "max": -0.1, "default": -10.0, "scale": "log", "mode": "variable"},
            {"name": "fixed_param", "min": 0.0, "max": 1.0, "default": 0.5, "scale": "lin", "mode": "fixed"}
        ]

        params = Parameters(test_params)

        # Create normalized data (in the [0,1] range)
        norm_data = pd.DataFrame({
            "linear_param": [0.0, 0.5, 1.0],
            "log_param": [0.0, 0.5, 1.0],
            "neglog_param": [0.0, 0.5, 1.0]
        })

        # Apply combined denormalization and descaling
        result = params.denormalize_and_descale_parameters(norm_data)

        # Test linear parameter (should be same as denormalization only)
        self.assertAlmostEqual(result["linear_param"][0], 10.0)
        self.assertAlmostEqual(result["linear_param"][1], 15.0)
        self.assertAlmostEqual(result["linear_param"][2], 20.0)

        # For log parameter:
        # Original normalized [0, 0.5, 1]
        # After denormalization [log(0.1), (log(0.1)+log(1000))/2, log(1000)] ≈ [-1.0, 1.0, 3.0]
        # After descaling [10^-1, 10^1, 10^3] = [0.1, 10, 1000]
        self.assertAlmostEqual(result["log_param"][0], 0.1)
        self.assertAlmostEqual(result["log_param"][1], 10.0, places=1)  # Using fewer decimal places for floating point comparison
        self.assertAlmostEqual(result["log_param"][2], 1000.0)

        # For neglog parameter:
        # Original normalized [0, 0.5, 1]
        # After denormalization [-3.0, -1, 1]
        # After descaling [-10^-(-3), -10^-(-1), -10^-(1)] = [-1000, -10, -0.1]
        self.assertAlmostEqual(result["neglog_param"][0], -1000.0)
        self.assertAlmostEqual(result["neglog_param"][1], -10, places=1)
        self.assertAlmostEqual(result["neglog_param"][2], -0.1)

        # Check fixed parameter is included
        self.assertIn("fixed_param", result.columns)

    def test_visualize_parameter_properties(self):
        """Test that creates and visualizes parameter properties and transformations with multiple tables."""

        # Create a mix of parameter types
        test_params = [
            {"name": "linear_1", "min": 10.0, "max": 20.0, "default": 15.0, "scale": "lin", "mode": "variable"},
            {"name": "linear_2", "min": -50.0, "max": 50.0, "default": 0.0, "scale": "lin", "mode": "variable"},
            {"name": "log_1", "min": 0.1, "max": 1000.0, "default": 10.0, "scale": "log", "mode": "variable"},
            {"name": "log_2", "min": 1.0, "max": 1000000.0, "default": 1000.0, "scale": "log", "mode": "variable"},
            {"name": "neglog_1", "min": -1000.0, "max": -0.1, "default": -10.0, "scale": "log", "mode": "variable"},
            {"name": "neglog_2", "min": -1000000.0, "max": -100.0, "default": -1000.0, "scale": "log", "mode": "variable"},
            {"name": "fixed_1", "min": 0.0, "max": 1.0, "default": 0.5, "scale": "lin", "mode": "fixed"},
            {"name": "fixed_2", "min": -10.0, "max": 10.0, "default": 0.0, "scale": "lin", "mode": "fixed"},
        ]

        params = Parameters(test_params)

        # Create a larger figure with grid layout for multiple tables
        fig = plt.figure(figsize=(22, 12))
        gs = GridSpec(2, 3, height_ratios=[1, 1.2], width_ratios=[1, 1, 1], figure=fig)

        # Main properties table in the top row, spanning all columns
        ax_main = fig.add_subplot(gs[0, :])
        ax_main.axis('tight')
        ax_main.axis('off')

        # Three transformation tables in bottom row
        ax_left = fig.add_subplot(gs[1, 0])
        ax_left.axis('tight')
        ax_left.axis('off')

        ax_middle = fig.add_subplot(gs[1, 1])
        ax_middle.axis('tight')
        ax_middle.axis('off')

        ax_right = fig.add_subplot(gs[1, 2])
        ax_right.axis('tight')
        ax_right.axis('off')

        # --- TABLE 1: Parameter Properties ---

        # Extract all properties from the parameter DataFrames
        data = []
        headers = ['Name', 'Min', 'Max', 'Default', 'Scale', 'Mode', 'Transform',
                   'Min (Scaled)', 'Max (Scaled)', 'Default (Scaled)',
                   'Min (Norm)', 'Max (Norm)', 'Default (Norm)']

        # Combine all parameters (variable and fixed)
        all_params = pd.concat([params.variable_parameters, params.fixed_parameters])
        all_params_scaled = pd.concat([params.variable_parameters_scaled, params.fixed_parameters_scaled])
        all_params_normed = pd.concat([params.variable_parameters_normed, params.fixed_parameters_normed])

        # Sort by parameter name for consistency
        all_params = all_params.sort_values('name').reset_index(drop=True)

        # Build the data rows
        for i, row in all_params.iterrows():
            param_name = row['name']

            # Get corresponding rows from scaled and normed DataFrames
            scaled_row = all_params_scaled[all_params_scaled['name'] == param_name].iloc[0]
            normed_row = all_params_normed[all_params_normed['name'] == param_name].iloc[0]

            # Add data row
            data.append([
                param_name,
                f"{row['min']:.3g}",
                f"{row['max']:.3g}",
                f"{row['default']:.3g}",
                row['scale'],
                row['mode'],
                row.get('transform', '-'),
                f"{scaled_row['min']:.3g}",
                f"{scaled_row['max']:.3g}",
                f"{scaled_row['default']:.3g}",
                f"{normed_row['min']:.1f}",  # Min normalized is always 0
                f"{normed_row['max']:.1f}",  # Max normalized is always 1
                f"{normed_row['default']:.3f}"
            ])

        # Create the main properties table
        main_table = ax_main.table(
            cellText=data,
            colLabels=headers,
            loc='center',
            cellLoc='center',
            colWidths=[0.07] * len(headers)  # Explicitly set column widths
        )

        # Adjust table appearance for better visibility
        main_table.auto_set_font_size(False)
        main_table.set_fontsize(10)  # Larger font size
        main_table.scale(1.5, 1.8)   # Increase table size

        # Highlight header
        for i, key in enumerate(headers):
            cell = main_table[(0, i)]
            cell.set_text_props(fontweight='bold')
            cell.set_facecolor('#e6e6e6')

        # Color-code rows by parameter type
        for i, row in enumerate(data):
            # Get parameter type from name
            param_name = row[0]
            param_type = param_name.split('_')[0]  # linear, log, neglog, or fixed

            # Set background color based on parameter type
            color = {
                'linear': '#f0f8ff',  # Light blue
                'log': '#f0fff0',     # Light green
                'neglog': '#fff0f0',  # Light red
                'fixed': '#f8f0ff'    # Light purple
            }.get(param_type, '#ffffff')

            # Apply color to all cells in the row
            for j in range(len(headers)):
                cell = main_table[(i + 1, j)]
                cell.set_facecolor(color)
                cell.PAD = 0.05  # Improve cell padding for better readability

        # --- Function to create transformation tables ---
        def create_transformation_table(ax, norm_values, title):
            # Get variable parameter names
            var_param_names = params.variable_parameters_names

            # Create a DataFrame with the given normalized values
            norm_data = {}
            for param in var_param_names:
                norm_data[param] = norm_values
            norm_df = pd.DataFrame(norm_data)

            # Apply transformations
            denorm_df = params.denormalize_parameters(norm_df, include_fixed_parameters=False)
            descaled_df = params.denormalize_and_descale_parameters(norm_df, include_fixed_parameters=False)

            # Prepare table data
            transform_data = []
            transform_headers = ['Parameter', 'Normalized', 'Denormalized', 'Denorm+Descaled']

            for param in var_param_names:
                for i in range(len(norm_values)):
                    norm_val = norm_df[param][i]
                    denorm_val = denorm_df[param][i]
                    descaled_val = descaled_df[param][i]

                    # Format values based on magnitude
                    if abs(denorm_val) < 0.01 or abs(denorm_val) > 1000:
                        denorm_str = f"{denorm_val:.2e}"
                    else:
                        denorm_str = f"{denorm_val:.3g}"

                    if abs(descaled_val) < 0.01 or abs(descaled_val) > 1000:
                        descaled_str = f"{descaled_val:.2e}"
                    else:
                        descaled_str = f"{descaled_val:.3g}"

                    # Only include parameter name in first row for each parameter
                    param_name = param if i == 0 else ""

                    transform_data.append([
                        param_name,
                        f"{norm_val:.2f}",
                        denorm_str,
                        descaled_str
                    ])

            # Create table
            transform_table = ax.table(
                cellText=transform_data,
                colLabels=transform_headers,
                loc='center',
                cellLoc='center',
                colWidths=[0.25, 0.2, 0.3, 0.3]
            )

            # Adjust table appearance
            transform_table.auto_set_font_size(False)
            transform_table.set_fontsize(10)
            transform_table.scale(1.2, 1.5)

            # Highlight header
            for i, key in enumerate(transform_headers):
                cell = transform_table[(0, i)]
                cell.set_text_props(fontweight='bold')
                cell.set_facecolor('#e6e6e6')

            # Color rows by parameter type
            current_param = None
            current_color = None

            for i, row in enumerate(transform_data):
                param_name = row[0]

                # Update current parameter and color when we encounter a parameter name
                if param_name:
                    current_param = param_name
                    param_type = current_param.split('_')[0]
                    current_color = {
                        'linear': '#f0f8ff',  # Light blue
                        'log': '#f0fff0',     # Light green
                        'neglog': '#fff0f0',  # Light red
                    }.get(param_type, '#ffffff')

                # Apply color to all cells in the row
                for j in range(len(transform_headers)):
                    cell = transform_table[(i + 1, j)]
                    cell.set_facecolor(current_color)
                    cell.PAD = 0.05

            ax.set_title(title, fontsize=14, pad=20)
            return transform_table

        # --- Create the three transformation tables ---

        # Table with low normalized values (near 0)
        create_transformation_table(
            ax_left,
            [0.0, 0.1, 0.2],
            'Transformations with Low Normalized Values'
        )

        # Table with middle normalized values
        create_transformation_table(
            ax_middle,
            [0.4, 0.5, 0.6],
            'Transformations with Middle Normalized Values'
        )

        # Table with high normalized values (near 1)
        create_transformation_table(
            ax_right,
            [0.8, 0.9, 1.0],
            'Transformations with High Normalized Values'
        )

        # --- Adjust layout and save ---
        plt.tight_layout(h_pad=3, w_pad=2)
        fig.suptitle('Parameter Visualization and Transformation Analysis', fontsize=20, y=0.98)
        plt.subplots_adjust(top=0.95)

        # Save the figure if a test output directory is available
        try:
            import os
            output_dir = os.path.join(os.path.dirname(__file__), 'test_output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            plt.savefig(os.path.join(output_dir, 'parameter_properties_and_transformations.png'),
                       dpi=150,  # Higher resolution
                       bbox_inches='tight')  # Tight bounding box to remove excess whitespace
        except Exception as e:
            print(f"Could not save visualization: {e}")

        # Show the figure
        plt.show()  # For interactive testing

        # --- Verification tests ---

        # Verify that all parameters have the expected transformations
        # Linear parameters should have no transform
        for name in ['linear_1', 'linear_2']:
            param = params.get_parameter(name)
            self.assertIsNone(param.get('transform'))

        # Log parameters should have 'log' transform
        for name in ['log_1', 'log_2']:
            param = params.get_parameter(name)
            self.assertEqual(param.get('transform'), 'log')

        # Neglog parameters should have 'neglog' transform
        for name in ['neglog_1', 'neglog_2']:
            param = params.get_parameter(name)
            self.assertEqual(param.get('transform'), 'neglog')

        # Verify specific transformations for selected values
        test_norm_values = [0.0, 0.5, 1.0]
        test_df = pd.DataFrame({param: test_norm_values for param in params.variable_parameters_names})

        denorm_df = params.denormalize_parameters(test_df, include_fixed_parameters=False)
        descaled_df = params.denormalize_and_descale_parameters(test_df, include_fixed_parameters=False)

        # Verify linear parameter transformation
        self.assertAlmostEqual(denorm_df['linear_1'][0], 10.0)  # min
        self.assertAlmostEqual(denorm_df['linear_1'][1], 15.0)  # middle
        self.assertAlmostEqual(denorm_df['linear_1'][2], 20.0)  # max

        # Same for descaled since linear doesn't change in descaling
        self.assertAlmostEqual(descaled_df['linear_1'][0], 10.0)
        self.assertAlmostEqual(descaled_df['linear_1'][1], 15.0)
        self.assertAlmostEqual(descaled_df['linear_1'][2], 20.0)

        # Verify log parameter transformations
        self.assertLess(descaled_df['log_1'][0], 1.0)      # Should be near min (0.1)
        self.assertAlmostEqual(descaled_df['log_1'][1], 10.0, delta=1.0)  # Should be near 10
        self.assertGreaterEqual(descaled_df['log_1'][2], 100.0)  # Should be at max (1000)

        # Verify neglog parameter transformations
        self.assertLessEqual(descaled_df['neglog_1'][0], -100.0)  # Should be near min (-1000)
        self.assertAlmostEqual(descaled_df['neglog_1'][1], -10.0, delta=1.0)  # Should be near -10
        self.assertGreaterEqual(descaled_df['neglog_1'][2], -1.0)  # Should be near max (-0.1)

if __name__ == "__main__":
    unittest.main()
