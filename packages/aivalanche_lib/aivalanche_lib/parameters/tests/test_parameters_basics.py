# --- START OF FILE test_parameters_basics.py ---

import os
import json
import tempfile
import pandas as pd
import numpy as np # Added for isnan/isclose
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import math # Ensure math is imported if used in format_val

# Import Parameters
from aivalanche_lib.parameters import Parameters

# create_test_data function remains the same...
def create_test_data():
    """Create sample parameter data including discrete and categorical types."""
    return [
        # --- Continuous ---
        {"name": "cont_lin_pos", "type": "continuous", "min": 1.0, "max": 10.0, "default": 5.0, "scale": "lin", "mode": "variable"},
        {"name": "cont_lin_neg", "type": "continuous", "min": -10.0, "max": -1.0, "default": -5.0, "scale": "lin", "mode": "variable"},
        {"name": "cont_lin_mix", "type": "continuous", "min": -5.0, "max": 5.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "cont_log_pos", "type": "continuous", "min": 0.1, "max": 10.0, "default": 1.0, "scale": "log", "mode": "variable"},
        {"name": "cont_log_large", "type": "continuous", "min": 100.0, "max": 10000.0, "default": 1000.0, "scale": "log", "mode": "variable"},
        {"name": "cont_neglog", "type": "continuous", "min": -1000.0, "max": -0.1, "default": -10.0, "scale": "log", "mode": "variable"},
        # --- Discrete ---
        {"name": "disc_list_num", "type": "discrete", "values": [10, 20, 50, 100], "default": 50, "mode": "variable"},
        {"name": "disc_step", "type": "discrete", "min": 16, "max": 128, "step": 16, "default": 64, "mode": "variable"},
        {"name": "disc_step_log", "type": "discrete", "min": 1, "max": 1000, "step": 1, "default": 10, "scale": "log", "mode": "variable"}, # Log scaled discrete steps
        # --- Categorical ---
        {"name": "cat_str", "type": "categorical", "values": ["adam", "sgd", "rmsprop"], "default": "adam", "mode": "variable"}, # N=3, Def Index 0
        {"name": "cat_bool", "type": "categorical", "values": [True, False], "default": True, "mode": "variable"},          # N=2, Def Index 0
        {"name": "cat_mixed", "type": "categorical", "values": ["A", 1, True, None], "default": True, "mode": "variable"}, # N=4, Def Index 2
        {"name": "cat_single", "type": "categorical", "values": ["only_option"], "default": "only_option", "mode": "variable"}, # N=1, Def Index 0
        # --- Fixed ---
        {"name": "fixed_cont_lin", "type": "continuous", "min": 0.0, "max": 100.0, "default": 42.0, "scale": "lin", "mode": "fixed"},
        {"name": "fixed_cont_log", "type": "continuous", "min": 0.01, "max": 1000.0, "default": 10.0, "scale": "log", "mode": "fixed"},
        {"name": "fixed_disc_step", "type": "discrete", "min": 0, "max": 10, "step": 2, "default": 6, "mode": "fixed"},
        {"name": "fixed_cat", "type": "categorical", "values": ["red", "blue"], "default": "red", "mode": "fixed"} # N=2, Def Index 0
    ]

# test_init_from_list, test_init_from_dataframe, etc. remain the same...
# ... (Paste the test functions from the previous version here) ...
def test_init_from_list():
    """Test initializing Parameters from a list including new types."""
    test_data = create_test_data()
    params = Parameters(test_data)

    total_params = len(test_data)
    nr_variable = sum(1 for p in test_data if p.get("mode", "variable") == "variable")
    nr_fixed = total_params - nr_variable
    nr_continuous = sum(1 for p in test_data if p.get("type", "continuous") == "continuous")
    nr_discrete = sum(1 for p in test_data if p.get("type") == "discrete")
    nr_categorical = sum(1 for p in test_data if p.get("type") == "categorical")


    assert params.nr_parameters == total_params, f"Expected {total_params}, got {params.nr_parameters}"
    assert params.nr_variable_parameters == nr_variable
    assert params.nr_fixed_parameters == nr_fixed
    assert len(params.continuous_parameters) == nr_continuous
    assert len(params.discrete_parameters) == nr_discrete
    assert len(params.categorical_parameters) == nr_categorical
    assert not params.error_parsing, f"Parsing error: {params.error_parsing}"

    # Check if parameters were correctly classified
    variable_names = {p["name"] for p in test_data if p.get("mode", "variable") == "variable"}
    fixed_names = {p["name"] for p in test_data if p.get("mode") == "fixed"}
    assert set(params.variable_parameters_names) == variable_names
    assert set(params.fixed_parameters_names) == fixed_names

def test_init_from_dataframe():
    """Test initializing Parameters from a DataFrame including new types."""
    test_data = create_test_data()
    df = pd.DataFrame(test_data)
    params = Parameters(df)

    total_params = len(test_data)
    nr_variable = sum(1 for p in test_data if p.get("mode", "variable") == "variable")
    nr_fixed = total_params - nr_variable

    assert params.nr_parameters == total_params
    assert params.nr_variable_parameters == nr_variable
    assert params.nr_fixed_parameters == nr_fixed
    assert not params.error_parsing, f"Parsing error: {params.error_parsing}"

def test_init_from_json_file():
    """Test initializing Parameters from JSON including new types."""
    test_data = create_test_data()
    total_params = len(test_data)
    nr_variable = sum(1 for p in test_data if p.get("mode", "variable") == "variable")
    nr_fixed = total_params - nr_variable

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
        # json.dump handles None correctly (converts to null)
        json.dump(test_data, tmp, indent=4)
        tmp_path = tmp.name

    try:
        params = Parameters(tmp_path)
        assert params.nr_parameters == total_params, f"Expected {total_params}, got {params.nr_parameters}"
        assert params.nr_variable_parameters == nr_variable
        assert params.nr_fixed_parameters == nr_fixed
        assert not params.error_parsing, f"Parsing error: {params.error_parsing}"
    finally:
        os.unlink(tmp_path)

def test_init_from_csv_file():
    """Test initializing Parameters from CSV including new types."""
    test_data = create_test_data()
    df = pd.DataFrame(test_data)
    total_params = len(test_data)
    nr_variable = sum(1 for p in test_data if p.get("mode", "variable") == "variable")
    nr_fixed = total_params - nr_variable

     # Convert lists in 'values' to string representations for CSV
    df_csv = df.copy()
    # Ensure None in lists becomes 'null' or similar for valid JSON string
    def list_to_json_string(x):
         if isinstance(x, list):
              # Convert Python None to JSON null representation within the list
              # json.dumps handles this automatically
              return json.dumps(x)
         return x # Keep non-lists as they are (e.g., NaN will become NA)

    df_csv['values'] = df_csv['values'].apply(list_to_json_string)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp:
        df_csv.to_csv(tmp.name, index=False, na_rep='NA') # Use NA for missing values
        tmp_path = tmp.name

    try:
        params = Parameters(tmp_path)
        assert params.nr_parameters == total_params, f"Expected {total_params} params, got {params.nr_parameters}"
        assert params.nr_variable_parameters == nr_variable
        assert params.nr_fixed_parameters == nr_fixed
        assert not params.error_parsing, f"Parsing error: {params.error_parsing}"

        # Check if list was parsed back correctly for a categorical param
        cat_param = params.get_parameter("cat_str")
        assert isinstance(cat_param['values'], list), f"cat_str values not list: {cat_param['values']}"
        assert cat_param['values'] == ["adam", "sgd", "rmsprop"]

        cat_mixed_param = params.get_parameter("cat_mixed")
        assert isinstance(cat_mixed_param['values'], list), f"cat_mixed values not list: {cat_mixed_param['values']}"
        # CSV load might convert numeric-like strings, check expected types
        # Our CSV parser now tries bool/int/float conversion, so expect [str, int, bool, None]
        assert cat_mixed_param['values'] == ["A", 1, True, None]


    finally:
        os.unlink(tmp_path)

def test_internal_scaling():
    """Test internal parameter scaling including new types."""
    test_data = create_test_data()
    params = Parameters(test_data)

    assert not params.all_parameters_scaled.empty, "Scaled parameters df is empty"
    assert not params.error_parsing, f"Error during parameter processing: {params.error_parsing}"


    # --- Continuous ---
    log_small = params.get_parameter_scaled("cont_log_pos")
    assert np.isclose(log_small["min"], -1) and np.isclose(log_small["max"], 1), f"cont_log_pos scaled range failed: {log_small}"
    neglog_param = params.get_parameter_scaled("cont_neglog")
    # Scaled neglog: min from orig max, max from orig min
    assert np.isclose(neglog_param["min"], -3), f"cont_neglog scaled min failed: {neglog_param}" # Neglog min comes from original MAX (-0.1 -> -log10(0.1) = 1, but min/max swapped in func -> -log10(1000)=-3)
    assert np.isclose(neglog_param["max"], 1), f"cont_neglog scaled max failed: {neglog_param}" # Neglog max comes from original MIN (-1000 -> -log10(0.1)=1)


    # --- Discrete ---
    disc_step_log = params.get_parameter_scaled("disc_step_log")
    # log10(1)=0, log10(1000)=3, log10(10)=1
    assert np.isclose(disc_step_log["min"], 0), f"disc_step_log scaled min failed: {disc_step_log}"
    assert np.isclose(disc_step_log["max"], 3), f"disc_step_log scaled max failed: {disc_step_log}"
    assert np.isclose(disc_step_log["default"], 1), f"disc_step_log scaled default failed: {disc_step_log}"

    disc_list_num = params.get_parameter_scaled("disc_list_num")
    # Linear scale, min/max inferred from values [10, 100], default 50
    assert disc_list_num["min"] == 10, f"disc_list_num scaled min failed: {disc_list_num}"
    assert disc_list_num["max"] == 100, f"disc_list_num scaled max failed: {disc_list_num}"
    assert disc_list_num["default"] == 50, f"disc_list_num scaled default failed: {disc_list_num}"

    # --- Categorical (Check Index Scaling) ---
    cat_str = params.get_parameter_scaled("cat_str") # values=["adam", "sgd", "rmsprop"], default="adam" (index 0), N=3
    assert np.isclose(cat_str["min"], 0.0), f"cat_str scaled min failed: {cat_str}" # Scaled min is 0
    assert np.isclose(cat_str["max"], 2.0), f"cat_str scaled max failed: {cat_str}" # Scaled max is N-1 = 2
    assert np.isclose(cat_str["default"], 0.0), f"cat_str scaled default failed: {cat_str}" # Scaled default is index 0
    assert cat_str["values"] == ["adam", "sgd", "rmsprop"], "cat_str original values lost" # Check original values preserved

    cat_bool = params.get_parameter_scaled("cat_bool") # values=[True, False], default=True (index 0), N=2
    assert np.isclose(cat_bool["min"], 0.0), f"cat_bool scaled min failed: {cat_bool}"
    assert np.isclose(cat_bool["max"], 1.0), f"cat_bool scaled max failed: {cat_bool}" # N-1 = 1
    assert np.isclose(cat_bool["default"], 0.0), f"cat_bool scaled default failed: {cat_bool}" # index 0
    assert cat_bool["values"] == [True, False], "cat_bool original values lost"

    cat_mixed = params.get_parameter_scaled("cat_mixed") # values=["A", 1, True, None], default=True (index 2), N=4
    assert np.isclose(cat_mixed["min"], 0.0), f"cat_mixed scaled min failed: {cat_mixed}"
    assert np.isclose(cat_mixed["max"], 3.0), f"cat_mixed scaled max failed: {cat_mixed}" # N-1 = 3
    assert np.isclose(cat_mixed["default"], 2.0), f"cat_mixed scaled default failed: {cat_mixed}" # index 2
    assert cat_mixed["values"] == ["A", 1, True, None], "cat_mixed original values lost"

    cat_single = params.get_parameter_scaled("cat_single") # values=["only_option"], default="only_option" (index 0), N=1
    assert np.isclose(cat_single["min"], 0.0), f"cat_single scaled min failed: {cat_single}"
    assert np.isclose(cat_single["max"], 0.0), f"cat_single scaled max failed: {cat_single}" # N-1 = 0
    assert np.isclose(cat_single["default"], 0.0), f"cat_single scaled default failed: {cat_single}" # index 0
    assert cat_single["values"] == ["only_option"], "cat_single original values lost"

    # --- Fixed ---
    fixed_log = params.get_parameter_scaled("fixed_cont_log")
    assert np.isclose(fixed_log["min"], -2) and np.isclose(fixed_log["max"], 3)
    assert np.isclose(fixed_log["default"], 1)

    fixed_disc_step = params.get_parameter_scaled("fixed_disc_step")
    assert fixed_disc_step["min"] == 0 and fixed_disc_step["max"] == 10 # No scaling applied (lin)
    assert fixed_disc_step["default"] == 6

    fixed_cat = params.get_parameter_scaled("fixed_cat") # values=["red", "blue"], default="red" (index 0), N=2
    assert np.isclose(fixed_cat["min"], 0.0)
    assert np.isclose(fixed_cat["max"], 1.0) # N-1 = 1
    assert np.isclose(fixed_cat["default"], 0.0) # index 0
    assert fixed_cat["values"] == ["red", "blue"]

def test_internal_normalization():
    """Test internal parameter normalization including new types."""
    test_data = create_test_data()
    params = Parameters(test_data)

    assert not params.all_parameters_normed.empty, "Normalized parameters df is empty"
    assert not params.error_parsing, f"Error during parameter processing: {params.error_parsing}"


    # Check all params have min=0, max=1 in normed space
    for param_name in params.parameters_names:
        norm_param = params.get_parameter_normed(param_name)
        assert norm_param is not None, f"Normed param '{param_name}' not found"
        # Use tolerance for float comparison
        assert np.isclose(norm_param["min"], 0.0), f"{param_name} normed min is not 0.0: {norm_param['min']}"
        assert np.isclose(norm_param["max"], 1.0), f"{param_name} normed max is not 1.0: {norm_param['max']}"

    # --- Continuous Defaults ---
    norm_log_pos = params.get_parameter_normed("cont_log_pos") # Def=1.0, Scaled Range [-1, 1], Scaled Def = log10(1)=0 -> Norm Def = (0 - (-1)) / (1 - (-1)) = 1 / 2 = 0.5
    assert np.isclose(norm_log_pos["default"], 0.5), f"cont_log_pos norm default failed: {norm_log_pos['default']}"

    # --- Discrete Defaults ---
    norm_disc_list = params.get_parameter_normed("disc_list_num") # Def=50, Scaled Range [10, 100] -> Norm Def = (50-10)/(100-10) = 40/90 = 4/9
    assert np.isclose(norm_disc_list["default"], 4/9), f"disc_list_num norm default failed: {norm_disc_list['default']}"

    norm_disc_step = params.get_parameter_normed("disc_step") # Def=64, Scaled Range [16, 128] -> Norm Def = (64-16)/(128-16) = 48/112 = 3/7
    assert np.isclose(norm_disc_step["default"], 3/7), f"disc_step norm default failed: {norm_disc_step['default']}"

    norm_disc_step_log = params.get_parameter_normed("disc_step_log") # Def=10, Scaled Range [0, 3], Scaled Def=log10(10)=1 -> Norm Def = (1-0)/(3-0) = 1/3
    assert np.isclose(norm_disc_step_log["default"], 1/3), f"disc_step_log norm default failed: {norm_disc_step_log['default']}"

    # --- Categorical Defaults (Normalized Index) ---
    norm_cat_str = params.get_parameter_normed("cat_str") # N=3, Def Index 0, Scaled Range [0, 2] -> Norm Def = (0-0)/(2-0) = 0.0
    assert np.isclose(norm_cat_str["default"], 0.0), f"cat_str norm default failed: {norm_cat_str['default']}"

    norm_cat_bool = params.get_parameter_normed("cat_bool") # N=2, Def Index 0, Scaled Range [0, 1] -> Norm Def = (0-0)/(1-0) = 0.0
    assert np.isclose(norm_cat_bool["default"], 0.0), f"cat_bool norm default failed: {norm_cat_bool['default']}"

    norm_cat_mixed = params.get_parameter_normed("cat_mixed") # N=4, Def Index 2, Scaled Range [0, 3] -> Norm Def = (2-0)/(3-0) = 2/3
    assert np.isclose(norm_cat_mixed["default"], 2/3), f"cat_mixed norm default failed: {norm_cat_mixed['default']}"

    norm_cat_single = params.get_parameter_normed("cat_single") # N=1, Def Index 0, Scaled Range [0, 0] -> Norm Def = 0.5 (special case)
    assert np.isclose(norm_cat_single["default"], 0.5), f"cat_single norm default failed: {norm_cat_single['default']}"

    # --- Fixed Defaults ---
    fixed_log = params.get_parameter_normed("fixed_cont_log") # Def=10, Scaled Range [-2, 3], Scaled Def=log10(10)=1 -> Norm Def = (1 - (-2)) / (3 - (-2)) = 3/5 = 0.6
    assert np.isclose(fixed_log["default"], 0.6), f"fixed_log norm default failed: {fixed_log['default']}"

    fixed_disc_step = params.get_parameter_normed("fixed_disc_step") # Def=6, Scaled Range [0, 10] -> Norm Def = (6-0)/(10-0) = 0.6
    assert np.isclose(fixed_disc_step["default"], 0.6), f"fixed_disc_step norm default failed: {fixed_disc_step['default']}"

    fixed_cat = params.get_parameter_normed("fixed_cat") # N=2, Def Index 0, Scaled Range [0, 1] -> Norm Def = (0-0)/(1-0) = 0.0
    assert np.isclose(fixed_cat["default"], 0.0), f"fixed_cat norm default failed: {fixed_cat['default']}"


def test_transforms():
    """Test that the correct transforms are applied, including new types."""
    test_data = create_test_data()
    params = Parameters(test_data)
    assert not params.error_parsing, f"Error during parameter processing: {params.error_parsing}"


    # Check transforms for continuous
    assert params.get_parameter("cont_log_pos")["transform"] == "log"
    # Check neglog transform (was determined based on range and 'log' scale)
    assert params.get_parameter("cont_neglog")["transform"] == "neglog", f"cont_neglog transform failed: {params.get_parameter('cont_neglog')}"
    assert params.get_parameter("cont_lin_pos")["transform"] is None # Should be None for lin

    # Check discrete
    assert params.get_parameter("disc_step_log")["transform"] == "log"
    assert params.get_parameter("disc_list_num")["transform"] is None

    # Check categorical (should always be None)
    assert params.get_parameter("cat_str")["transform"] is None
    assert params.get_parameter("cat_bool")["transform"] is None

    # Check fixed
    assert params.get_parameter("fixed_cont_log")["transform"] == "log"
    assert params.get_parameter("fixed_cat")["transform"] is None


# --- Visualization Function ---
def visualize_parameters_table(params):
    """
    Create a visualization of original, scaled, and normalized parameters
    in a single table with parameters as rows.
    """
    if params.all_parameters.empty:
        print("Cannot visualize empty parameters.")
        return None

    # Select columns and prepare for merge
    df_orig = params.all_parameters[['name', 'type', 'mode', 'values', 'step', 'min', 'max', 'default']].copy()
    df_orig.rename(columns={'min': 'orig_min', 'max': 'orig_max', 'default': 'orig_default', 'values': 'orig_values', 'step': 'orig_step'}, inplace=True)

    df_scaled = params.all_parameters_scaled[['name', 'min', 'max', 'default', 'scale', 'transform']].copy()
    # Rename scale/transform to indicate they are the final, potentially validated/changed values
    df_scaled.rename(columns={'min': 'scaled_min', 'max': 'scaled_max', 'default': 'scaled_default', 'scale': 'final_scale', 'transform': 'final_transform'}, inplace=True)

    df_normed = params.all_parameters_normed[['name', 'min', 'max', 'default']].copy()
    df_normed.rename(columns={'min': 'normed_min', 'max': 'normed_max', 'default': 'normed_default'}, inplace=True)

    # Merge the dataframes
    merged_df = pd.merge(df_orig, df_scaled, on='name', how='left')
    merged_df = pd.merge(merged_df, df_normed, on='name', how='left')

    # Define final column order
    cols_to_show = [
        'name', 'type', 'mode', 'final_scale', 'final_transform',
        'orig_values', 'orig_step',
        'orig_min', 'orig_max', 'orig_default',
        'scaled_min', 'scaled_max', 'scaled_default',
        'normed_min', 'normed_max', 'normed_default'
    ]
    # Reorder and sort rows (parameters)
    merged_df = merged_df[cols_to_show]
    merged_df = merged_df.sort_values(by=['mode', 'type', 'name']).reset_index(drop=True)


    # --- Formatting ---
    def format_val(v):
        if isinstance(v, float):
            if math.isnan(v): return "NaN"
            # Show more precision for normalized defaults and min/max
            if 0 <= v <= 1 and v != 0 and v != 1: return f"{v:.3f}" # Normed range
            if abs(v) < 1e-3 and v != 0: return f"{v:.2e}"
            # Reduce precision for other floats unless they are simple integers
            if v == int(v): return str(int(v))
            return f"{v:.2f}" # General float formatting
        if isinstance(v, list):
            MAX_LIST_ITEMS_DISPLAY = 4
            str_list = [format_val(item) for item in v[:MAX_LIST_ITEMS_DISPLAY+1]]
            if len(v) > MAX_LIST_ITEMS_DISPLAY:
                return "[" + ", ".join(str_list[:MAX_LIST_ITEMS_DISPLAY]) + ", ...]"
            return "[" + ", ".join(str_list) + "]"
        if isinstance(v, str) and len(v) > 15: return v[:12] + '...'
        if v is None: return "None"
        if isinstance(v, bool): return str(v) # Show True/False explicitly
        return str(v)

    # Apply formatting
    formatted_df = merged_df.map(format_val)

    # --- Plotting ---
    # Adjust figure size based on number of columns and rows
    # More columns now, so width needs to increase more
    fig_width = max(20, len(formatted_df.columns) * 1.2) # Increase width multiplier
    fig_height = max(8, len(formatted_df.index) * 0.4)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('tight')
    ax.axis('off')
    ax.set_title("Parameter Overview (Original, Scaled, Normalized)", fontsize=14, pad=20)

    table = ax.table(
        cellText=formatted_df.values,
        colLabels=formatted_df.columns,
        loc='center',
        cellLoc='center', # Center align text in cells
        colWidths=[0.08]*len(formatted_df.columns) # Use smaller fixed width for more columns
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8) # Adjust vertical scaling

    # --- Coloring ---
    colors = {
        'fixed': '#FFD580',      # Light orange
        'continuous': '#D3D3D3', # Light gray
        'discrete': '#ACD1E9',   # Light blue
        'categorical': '#90EE90', # Light green
        'log_overlay': '#FFAAAA', # Indicate log transform (applied on top)
        'neglog_overlay': '#E6A4E6' # Indicate neglog transform
    }

    # Find column indices for coloring
    try:
        final_scale_idx = formatted_df.columns.get_loc('final_scale')
        final_transform_idx = formatted_df.columns.get_loc('final_transform')
        type_idx = formatted_df.columns.get_loc('type')
        mode_idx = formatted_df.columns.get_loc('mode')
        name_idx = formatted_df.columns.get_loc('name')
    except KeyError as e:
        print(f"Error finding column index for coloring: {e}. Skipping coloring.")
        return fig # Return the uncolored table


    for i in range(len(formatted_df.index)):
        row_idx = i + 1 # Table row index (1-based due to header)
        param_type = merged_df.iloc[i]['type'] # Use original merged df for type/mode
        param_mode = merged_df.iloc[i]['mode']
        param_name = merged_df.iloc[i]['name'] # For potential future use?

        # Determine base color
        base_color = colors['fixed'] if param_mode == 'fixed' else colors.get(param_type, '#FFFFFF')

        # Apply base color to all cells in the row
        for j in range(len(formatted_df.columns)):
            table[(row_idx, j)].set_facecolor(base_color)

        # Apply overlay for transforms if applicable (only for non-fixed)
        if param_mode != 'fixed':
            transform = merged_df.iloc[i]['final_transform'] # Get final transform from merged data
            if transform and transform != 'None': # Check it's actually 'log' or 'neglog'
                overlay_color = colors.get(f'{transform}_overlay', None)
                if overlay_color:
                    # Apply overlay color to scale/transform cells
                    table[(row_idx, final_scale_idx)].set_facecolor(overlay_color)
                    table[(row_idx, final_transform_idx)].set_facecolor(overlay_color)

    # Bold column labels
    for j in range(len(formatted_df.columns)):
        table[(0, j)].get_text().set_weight('bold') # Column labels

    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05) # Adjust layout for wide table
    return fig


# --- Updated Test Runner ---
def test_with_visualization():
    """
    Test with visualization of parameters including new types using the merged table view.
    Useful for manual inspection.
    """
    test_data = create_test_data()
    params = Parameters(test_data)
    assert not params.error_parsing, f"Error during parameter processing: {params.error_parsing}"

    # Create visualization
    fig = visualize_parameters_table(params) # Call the new function
    if fig is None:
        print("Visualization could not be generated.")
        return

    # Save the figure (optional)
    output_filename = 'parameters_visualization_table.png' # New filename
    try:
        fig.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"Merged table visualization saved to {output_filename}")
    except Exception as e:
        print(f"Error saving visualization: {e}")

    # Display the figure if running in an interactive environment
    # plt.show() # Comment out for automated runs

    plt.close(fig) # Close the figure

if __name__ == "__main__":
    print("Running Basic Tests with New Types...")
    test_init_from_list()
    print("test_init_from_list PASSED")
    test_init_from_dataframe()
    print("test_init_from_dataframe PASSED")
    test_init_from_json_file()
    print("test_init_from_json_file PASSED")
    test_init_from_csv_file()
    print("test_init_from_csv_file PASSED")
    test_transforms()
    print("test_transforms PASSED")
    test_internal_scaling()
    print("test_internal_scaling PASSED")
    test_internal_normalization()
    print("test_internal_normalization PASSED")
    print("All basic tests passed!")

    # Create and save visualization
    print("\nGenerating merged table visualization...")
    test_with_visualization()

# --- END OF FILE test_parameters_basics.py ---
