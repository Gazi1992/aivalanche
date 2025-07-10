# --- START OF FILE test_parameters_transforms.py ---

"""
Tests for transformation functions of the Parameters class, including
discrete and categorical types.

Focuses on array/DataFrame transformations: denormalize, descale, normalize, scale.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import math # Added

# Import Parameters from your package
from aivalanche_lib.parameters import Parameters
# Import utils needed for manual calculation verification if necessary
from aivalanche_lib.parameters.scale_norm import denormalize_categorical_value, normalize_categorical_value, normalize_parameter_value

def create_test_data():
    """Create sample parameter data including discrete and categorical types."""
    # Using the same data as basics test for consistency
    return [
        # --- Continuous ---
        {"name": "cont_lin_pos", "type": "continuous", "min": 1.0, "max": 10.0, "default": 5.0, "scale": "lin", "mode": "variable"},
        {"name": "cont_log_pos", "type": "continuous", "min": 0.1, "max": 10.0, "default": 1.0, "scale": "log", "mode": "variable"},
        {"name": "cont_neglog", "type": "continuous", "min": -1000.0, "max": -0.1, "default": -10.0, "scale": "log", "mode": "variable"},
        # --- Discrete ---
        {"name": "disc_list_num", "type": "discrete", "values": [10, 20, 50, 100], "default": 50, "mode": "variable"}, # N=4
        {"name": "disc_step", "type": "discrete", "min": 16, "max": 128, "step": 16, "default": 64, "mode": "variable"},
        {"name": "disc_step_log", "type": "discrete", "min": 1, "max": 1000, "step": 1, "default": 10, "scale": "log", "mode": "variable"}, # Log scaled discrete steps
        # --- Categorical ---
        {"name": "cat_str", "type": "categorical", "values": ["adam", "sgd", "rmsprop"], "default": "adam", "mode": "variable"}, # N=3
        {"name": "cat_bool", "type": "categorical", "values": [True, False], "default": True, "mode": "variable"},          # N=2
        {"name": "cat_single", "type": "categorical", "values": ["only"], "default": "only", "mode": "variable"},             # N=1
        # --- Fixed ---
        {"name": "fixed_cont_lin", "type": "continuous", "min": 0.0, "max": 100.0, "default": 42.0, "scale": "lin", "mode": "fixed"},
        {"name": "fixed_disc_step", "type": "discrete", "min": 0, "max": 10, "step": 2, "default": 6, "mode": "fixed"},
        {"name": "fixed_cat", "type": "categorical", "values": ["red", "blue"], "default": "red", "mode": "fixed"} # N=2
    ]

def create_test_normalized_data():
    """
    Create sample normalized [0,1] data for denormalization testing.
    Values chosen to test boundaries, midpoints, and points that require rounding/snapping.
    """
    return pd.DataFrame({
        # Continuous
        "cont_lin_pos":  [0.0, 0.25, 0.5, 0.75, 1.0],    # Range [1, 10] -> 1, 3.25, 5.5, 7.75, 10
        "cont_log_pos":  [0.0, 0.25, 0.5, 0.75, 1.0],    # Scaled [-1, 1] -> Denorm -1, -0.5, 0, 0.5, 1 -> Descale 0.1, 0.316, 1, 3.16, 10
        "cont_neglog":   [0.0, 0.25, 0.5, 0.75, 1.0],    # Scaled [1, -3] -> Denorm 1, 0.0, -1.0, -2.0, -3.0 -> Descale -0.1, -1, -10, -100, -1000 (Check Denorm Step)
        # Discrete
        "disc_list_num": [0.0, 0.3, 0.6, 0.9, 1.0],    # Scaled [10, 100] -> Denorm 10, 37, 64, 91, 100 -> Snap 10, 50, 50, 100, 100
        "disc_step":     [0.0, 0.3, 0.6, 0.9, 1.0],    # Scaled [16, 128] -> Denorm 16, 49.6, 83.2, 116.8, 128 -> Snap 16, 48, 80, 112, 128
        "disc_step_log": [0.0, 0.3, 0.6, 0.9, 1.0],    # Scaled [0, 3] -> Denorm 0, 0.9, 1.8, 2.7, 3 -> Descale 1, 7.94, 63.1, 501.18, 1000 -> Snap 1, 8, 63, 501, 1000
        # Categorical (N=3, N=2, N=1) - Use utility logic for expected
        "cat_str":       [0.0, 0.1, 0.4, 0.8, 1.0],    # N=3 -> Indices 0, 0.2, 0.8, 1.6, 2 -> Round 0, 0, 1, 2, 2 -> adam, adam, sgd, rmsprop, rmsprop
        "cat_bool":      [0.0, 0.1, 0.6, 0.9, 1.0],    # N=2 -> Indices 0, 0.1, 0.6, 0.9, 1 -> Round 0, 0, 1, 1, 1 -> True, True, False, False, False
        "cat_single":    [0.0, 0.25, 0.5, 0.75, 1.0]   # N=1 -> Index 0 always -> 'only'
    })


def create_test_raw_data():
    """Create sample raw (original scale) data for scaling/normalization testing."""
    return pd.DataFrame({
        # Continuous
        "cont_lin_pos":  [1.0, 3.25, 5.5, 7.75, 10.0],       # Range [1, 10] -> Norm 0, 0.25, 0.5, 0.75, 1
        "cont_log_pos":  [0.1, 0.3162, 1.0, 3.1623, 10.0],    # Scale log10 -> -1, -0.5, 0, 0.5, 1 -> Norm 0, 0.25, 0.5, 0.75, 1
        "cont_neglog":   [-0.1, -1.0, -10.0, -100.0, -1000.0], # Scale -log10(-x) -> 1, 0, -1, -2, -3 -> Norm 0, 0.25, 0.5, 0.75, 1 (Scaled Range [1, -3])
        # Discrete
        "disc_list_num": [10, 20, 50, 100, 10],              # Scale lin -> 10, 20, 50, 100, 10 -> Norm 0, 1/9, 4/9, 1, 0
        "disc_step":     [16, 32, 64, 112, 128],             # Scale lin -> 16, 32, 64, 112, 128 -> Norm 0, 1/7, 3/7, 6/7, 1
        "disc_step_log": [1, 8, 63, 501, 1000],             # Scale log10 -> 0, 0.903, 1.799, 2.7, 3 -> Norm 0, 0.301, 0.6, 0.9, 1
        # Categorical
        "cat_str":       ["adam", "sgd", "rmsprop", "adam", "sgd"], # Scale index -> 0, 1, 2, 0, 1 -> Norm 0, 0.5, 1, 0, 0.5
        "cat_bool":      [True, False, True, False, True],          # Scale index -> 0, 1, 0, 1, 0 -> Norm 0, 1, 0, 1, 0
        "cat_single":    ["only", "only", "only", "only", "only"]   # Scale index -> 0, 0, 0, 0, 0 -> Norm 0.5, 0.5, 0.5, 0.5, 0.5
    })

# --- Test Denormalization/Descaling ---

def test_denormalize_and_descale_parameters_array():
    """Test combined denormalization and descaling with new types."""
    params = Parameters(create_test_data())
    assert not params.error_parsing, f"Error during parameter processing: {params.error_parsing}"
    normalized_data = create_test_normalized_data()

    # Use the combined function
    denorm_descaled = params.denormalize_and_descale_parameters_array(
        normalized_data.copy(), # Pass a copy
        include_fixed=True
    )
    assert isinstance(denorm_descaled, pd.DataFrame), "Result should be DataFrame"

    # --- Assertions for Continuous ---
    # cont_log_pos: Scaled Range [-1, 1]
    assert np.isclose(denorm_descaled["cont_log_pos"].iloc[0], 0.1)
    assert np.isclose(denorm_descaled["cont_log_pos"].iloc[2], 1.0)
    assert np.isclose(denorm_descaled["cont_log_pos"].iloc[4], 10.0)

    # cont_neglog: Scaled Range [1, -3]
    assert np.isclose(denorm_descaled["cont_neglog"].iloc[0], -1000), f"Expected -0.1, got {denorm_descaled['cont_neglog'].iloc[0]}"
    assert np.isclose(denorm_descaled["cont_neglog"].iloc[2], -10.0), f"Expected -10.0, got {denorm_descaled['cont_neglog'].iloc[2]}"
    assert np.isclose(denorm_descaled["cont_neglog"].iloc[4], -0.1), f"Expected -1000.0, got {denorm_descaled['cont_neglog'].iloc[4]}"

    # --- Assertions for Discrete (Check Snapping) ---
    # disc_list_num: values=[10, 20, 50, 100]. Scaled Range [10, 100].
    assert denorm_descaled["disc_list_num"].iloc[0] == 10
    assert denorm_descaled["disc_list_num"].iloc[1] == 50 # Snap check (37->50)
    assert denorm_descaled["disc_list_num"].iloc[2] == 50 # Snap check (64->50)
    assert denorm_descaled["disc_list_num"].iloc[3] == 100 # Snap check (91->100)
    assert denorm_descaled["disc_list_num"].iloc[4] == 100

    # disc_step: min=16, max=128, step=16. Scaled Range [16, 128].
    assert denorm_descaled["disc_step"].iloc[0] == 16
    assert denorm_descaled["disc_step"].iloc[1] == 48 # Snap check (49.6->48)
    assert denorm_descaled["disc_step"].iloc[2] == 80 # Snap check (83.2->80)
    assert denorm_descaled["disc_step"].iloc[3] == 112 # Snap check (116.8->112)
    assert denorm_descaled["disc_step"].iloc[4] == 128

    # disc_step_log: min=1, max=1000, step=1, scale=log. Scaled Range [0, 3].
    assert denorm_descaled["disc_step_log"].iloc[0] == 1
    assert denorm_descaled["disc_step_log"].iloc[1] == 8 # Snap check (7.94->8)
    assert denorm_descaled["disc_step_log"].iloc[2] == 63 # Snap check (63.1->63)
    assert denorm_descaled["disc_step_log"].iloc[3] == 501 # Snap check (501.18->501)
    assert denorm_descaled["disc_step_log"].iloc[4] == 1000

    # --- Assertions for Categorical (Check Mapping - Use Utility Logic) ---
    # cat_str: values=['adam', 'sgd', 'rmsprop']. N=3. Indices [0, 1, 2].
    assert denorm_descaled["cat_str"].iloc[0] == "adam"
    assert denorm_descaled["cat_str"].iloc[1] == "adam" # Round check (norm 0.1)
    assert denorm_descaled["cat_str"].iloc[2] == "sgd"  # Round check (norm 0.4)
    assert denorm_descaled["cat_str"].iloc[3] == "rmsprop" # Round check (norm 0.8)
    assert denorm_descaled["cat_str"].iloc[4] == "rmsprop"

    # cat_bool: values=[True, False]. N=2. Indices [0, 1].
    # *** USE == for boolean comparison ***
    assert denorm_descaled["cat_bool"].iloc[0] == True, f"Expected True, got {denorm_descaled['cat_bool'].iloc[0]}"
    assert denorm_descaled["cat_bool"].iloc[1] == True, f"Round check failed: Expected True, got {denorm_descaled['cat_bool'].iloc[1]}" # Round check (norm 0.1)
    assert denorm_descaled["cat_bool"].iloc[2] == False, f"Round check failed: Expected False, got {denorm_descaled['cat_bool'].iloc[2]}" # Round check (norm 0.6)
    assert denorm_descaled["cat_bool"].iloc[3] == False, f"Round check failed: Expected False, got {denorm_descaled['cat_bool'].iloc[3]}" # Round check (norm 0.9)
    assert denorm_descaled["cat_bool"].iloc[4] == False, f"Expected False, got {denorm_descaled['cat_bool'].iloc[4]}"

    # cat_single: values=['only']. N=1. Index [0].
    assert denorm_descaled["cat_single"].iloc[0] == "only"
    assert denorm_descaled["cat_single"].iloc[2] == "only"
    assert denorm_descaled["cat_single"].iloc[4] == "only"

    # --- Assertions for Fixed ---
    assert "fixed_cont_lin" in denorm_descaled.columns
    assert "fixed_disc_step" in denorm_descaled.columns
    assert "fixed_cat" in denorm_descaled.columns
    assert denorm_descaled["fixed_cont_lin"].iloc[0] == 42.0
    assert denorm_descaled["fixed_disc_step"].iloc[0] == 6
    assert denorm_descaled["fixed_cat"].iloc[0] == "red"

    return params, normalized_data, denorm_descaled


# --- Test Scaling/Normalization ---

def test_scale_and_normalize_parameters_array():
    """Test combined scaling and normalizing with new types."""
    params = Parameters(create_test_data())
    assert not params.error_parsing, f"Error during parameter processing: {params.error_parsing}"
    raw_data = create_test_raw_data()
    # Manually calculate expected normalized values based on raw_data and parameter definitions
    expected_normalized_dict = {
         "cont_lin_pos":  [0.0, 0.25, 0.5, 0.75, 1.0],
         "cont_log_pos":  [0.0, 0.25, 0.5, 0.75, 1.0],
         "cont_neglog":   [1.0, 0.75, 0.5, 0.25, 0.0], # Scaled range [1, -3]
         "disc_list_num": [0.0, 1/9, 4/9, 1.0, 0.0], # Scaled range [10, 100]
         "disc_step":     [0.0, 1/7, 3/7, 6/7, 1.0], # Scaled range [16, 128] -> (32-16)/112=16/112=1/7, (64-16)/112=48/112=3/7, (112-16)/112=96/112=6/7
         "disc_step_log": [0.0, 0.301, 0.6, 0.9, 1.0], # Scaled range [0, 3] -> log10(8)/3=0.903/3=0.301, log10(63)/3=1.799/3=0.6, log10(501)/3=2.7/3=0.9
         "cat_str":       [0.0, 0.5, 1.0, 0.0, 0.5], # Index 0,1,2 -> Norm 0/(3-1)=0, 1/2=0.5, 2/2=1.0
         "cat_bool":      [0.0, 1.0, 0.0, 1.0, 0.0], # Index 0,1 -> Norm 0/(2-1)=0, 1/1=1.0
         "cat_single":    [0.5, 0.5, 0.5, 0.5, 0.5]  # Index 0 -> Norm 0.5 (special case N=1)
    }
    expected_normalized = pd.DataFrame(expected_normalized_dict)


    # Use the combined function
    scaled_normalized = params.scale_and_normalize_parameters_array(
        raw_data.copy(), # Pass a copy
        include_fixed=True
    )
    assert isinstance(scaled_normalized, pd.DataFrame), "Result should be DataFrame"


    # --- Assertions for Variable Parameters ---
    for col in expected_normalized.columns:
         assert col in scaled_normalized.columns, f"Column '{col}' missing in result"
         assert np.allclose(scaled_normalized[col], expected_normalized[col], atol=1e-3), \
                f"Normalized values mismatch for '{col}'.\nExpected:\n{expected_normalized[col]}\nGot:\n{scaled_normalized[col]}"

    # --- Assertions for Fixed ---
    assert "fixed_cont_lin" in scaled_normalized.columns
    assert "fixed_disc_step" in scaled_normalized.columns
    assert "fixed_cat" in scaled_normalized.columns
    # Get expected normalized defaults from the Parameters object
    normed_fixed_cont_lin = params.get_parameter_normed("fixed_cont_lin")["default"]
    normed_fixed_disc_step = params.get_parameter_normed("fixed_disc_step")["default"]
    normed_fixed_cat = params.get_parameter_normed("fixed_cat")["default"]
    # Check all rows have the normalized fixed default
    assert np.allclose(scaled_normalized["fixed_cont_lin"], normed_fixed_cont_lin), f"Fixed cont lin norm failed. Expected {normed_fixed_cont_lin}"
    assert np.allclose(scaled_normalized["fixed_disc_step"], normed_fixed_disc_step), f"Fixed disc step norm failed. Expected {normed_fixed_disc_step}"
    assert np.allclose(scaled_normalized["fixed_cat"], normed_fixed_cat), f"Fixed cat norm failed. Expected {normed_fixed_cat}"

    # --- Compare overall structure ---
    # Check columns match expected normalized output columns (variable + fixed)
    expected_cols_final = sorted(list(expected_normalized.columns) + params.fixed_parameters_names)
    assert sorted(list(scaled_normalized.columns)) == expected_cols_final
    # Check number of rows
    assert len(scaled_normalized) == len(raw_data)


    return params, raw_data, scaled_normalized


# --- Visualization (Optional, similar structure needed if desired) ---
# Adapting the visualization functions from test_parameters_basics would be needed
# to show the array transformations step-by-step for the new types.
# This involves plotting the input raw/normalized data and the output at each stage.

# --- Test Runner ---
def run_tests_and_visualize():
    """Run all transformation tests."""
    print("Testing denormalize_and_descale_parameters_array...")
    params_dd, normalized_data, denorm_descaled = test_denormalize_and_descale_parameters_array()
    print("--> PASSED")

    print("\nTesting scale_and_normalize_parameters_array...")
    params_sn, raw_data, scaled_normalized = test_scale_and_normalize_parameters_array()
    print("--> PASSED")

    # Optional: Add visualization calls here if implemented
    # print("\nGenerating visualizations...")
    # fig1 = visualize_denormalize_descale(...)
    # fig2 = visualize_scale_normalize(...)
    # fig1.savefig(...)
    # fig2.savefig(...)
    # plt.show()


if __name__ == "__main__":
    # When running the script directly, execute tests
    run_tests_and_visualize()
    print("\nAll transformation tests passed!")

# --- END OF FILE test_parameters_transforms.py ---
