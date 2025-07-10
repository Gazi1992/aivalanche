"""
Tests for basic functionality of the Parameters class.

This test file focuses on the initialization of the Parameters class
and the internal scaling and normalization of parameters that happens
automatically during initialization, not on the array functions.
"""

import os
import json
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Import Parameters from your package
from aivalanche_lib.parameters import Parameters

def create_test_data():
    """Create sample parameter data for testing."""
    return [
        {"name": "linear_positive", "min": 1.0, "max": 10.0, "default": 5.0, "scale": "lin", "mode": "variable"},
        {"name": "linear_negative", "min": -10.0, "max": -1.0, "default": -5.0, "scale": "lin", "mode": "variable"},
        {"name": "linear_mixed", "min": -5.0, "max": 5.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "log_small", "min": 0.1, "max": 10.0, "default": 1.0, "scale": "log", "mode": "variable"},
        {"name": "log_large", "min": 100.0, "max": 10000.0, "default": 1000.0, "scale": "log", "mode": "variable"},
        {"name": "neglog", "min": -1000.0, "max": -0.1, "default": -10.0, "scale": "log", "mode": "variable"},
        {"name": "fixed_lin_param", "min": 0.0, "max": 100.0, "default": 42.0, "scale": "lin", "mode": "fixed"},
        {"name": "fixed_log_param", "min": 0.01, "max": 1000.0, "default": 10.0, "scale": "log", "mode": "fixed"}
    ]

def test_init_from_list():
    """Test initializing Parameters from a list of dictionaries."""
    test_data = create_test_data()
    params = Parameters(test_data)

    assert params.nr_parameters == 8
    assert params.nr_variable_parameters == 6
    assert params.nr_fixed_parameters == 2
    assert not params.error_parsing

    # Check if parameters were correctly classified as fixed or variable
    assert set(params.variable_parameters_names) == {"linear_positive", "linear_negative",
                                                  "linear_mixed", "log_small",
                                                  "log_large", "neglog"}
    assert set(params.fixed_parameters_names) == {"fixed_lin_param", "fixed_log_param"}

def test_init_from_dataframe():
    """Test initializing Parameters from a pandas DataFrame."""
    test_data = create_test_data()
    df = pd.DataFrame(test_data)
    params = Parameters(df)

    assert params.nr_parameters == 8
    assert params.nr_variable_parameters == 6
    assert params.nr_fixed_parameters == 2
    assert not params.error_parsing

def test_init_from_json_file():
    """Test initializing Parameters from a JSON file."""
    test_data = create_test_data()

    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        json.dump(test_data, tmp)
        tmp_path = tmp.name

    try:
        # Test loading from JSON file
        params = Parameters(tmp_path)

        assert params.nr_parameters == 8
        assert params.nr_variable_parameters == 6
        assert params.nr_fixed_parameters == 2
        assert not params.error_parsing
    finally:
        # Clean up the temporary file
        os.unlink(tmp_path)

def test_init_from_csv_file():
    """Test initializing Parameters from a CSV file."""
    test_data = create_test_data()
    df = pd.DataFrame(test_data)

    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        # Test loading from CSV file
        params = Parameters(tmp_path)

        assert params.nr_parameters == 8
        assert params.nr_variable_parameters == 6
        assert params.nr_fixed_parameters == 2
        assert not params.error_parsing
    finally:
        # Clean up the temporary file
        os.unlink(tmp_path)

def test_internal_scaling():
    """Test internal parameter scaling during initialization."""
    test_data = create_test_data()
    params = Parameters(test_data)

    # Check that scaled DataFrame was created
    assert not params.all_parameters_scaled.empty

    # Check log-scaled parameters
    log_small = params.get_parameter_scaled("log_small")
    assert log_small is not None
    # log10(0.1) = -1, log10(10) = 1
    assert log_small["min"] == -1  # Allow for floating point imprecision
    assert log_small["max"] == 1

    log_large = params.get_parameter_scaled("log_large")
    assert log_large is not None
    # log10(100) = 2, log10(10000) = 4
    assert log_large["min"] == 2
    assert log_large["max"] == 4

    # Check neglog-scaled parameters
    neglog_param = params.get_parameter_scaled("neglog")
    assert neglog_param is not None
    # -log10(-(-1000)) = -3, -log10(-(-0.1)) = +1
    assert neglog_param["min"] == -3
    assert neglog_param["max"] == 1

    # Check fixed log parameter is properly scaled
    fixed_log = params.get_parameter_scaled("fixed_log_param")
    assert fixed_log is not None
    # log10(0.01) = -2, log10(1000) = 3
    assert fixed_log["min"] == -2
    assert fixed_log["max"] == 3
    # log10(10) = 1
    assert fixed_log["default"] == 1

def test_internal_normalization():
    """Test internal parameter normalization during initialization."""
    test_data = create_test_data()
    params = Parameters(test_data)

    # Check that normalized DataFrame was created
    assert not params.all_parameters_normed.empty

    # Check normalized parameters (all should have min=0, max=1)
    for param_name in params.parameters_names:
        norm_param = params.get_parameter_normed(param_name)
        assert norm_param is not None
        assert 0 <= norm_param["min"] <= 0.001  # Should be 0
        assert 0.999 <= norm_param["max"] <= 1  # Should be 1

    # Check specific normalized default values
    linear_positive = params.get_parameter_normed("linear_positive")
    assert 0.44 <= linear_positive["default"] <= 0.46  # Should be 0.44...

    log_small = params.get_parameter_normed("log_small")
    # log10(1) = 0, which is 0.5 of the way between log10(0.1)=-1 and log10(10)=1
    assert 0.49 <= log_small["default"] <= 0.51

    fixed_log = params.get_parameter_normed("fixed_log_param")
    # log10(10) = 1, which is 0.6 of the way between log10(0.01)=-2 and log10(1000)=3
    assert 0.59 <= fixed_log["default"] <= 0.61  # Should be 0.6

def test_transforms():
    """Test that the correct transforms are applied to parameters."""
    test_data = create_test_data()
    params = Parameters(test_data)

    # Check transforms for log-scaled parameters
    log_small = params.get_parameter("log_small")
    assert log_small["transform"] == "log"

    log_large = params.get_parameter("log_large")
    assert log_large["transform"] == "log"

    neglog = params.get_parameter("neglog")
    assert neglog["transform"] == "neglog"

    linear_mixed = params.get_parameter("linear_mixed")
    assert linear_mixed.get("transform") is None or linear_mixed.get("transform") == "lin"

    # Check transforms for fixed parameters
    fixed_lin = params.get_parameter("fixed_lin_param")
    assert fixed_lin.get("transform") is None or fixed_lin.get("transform") == "lin"

    fixed_log = params.get_parameter("fixed_log_param")
    assert fixed_log["transform"] == "log"

def visualize_parameters(params):
    """
    Create a visualization of original, scaled, and normalized parameters.
    Args:
        params: Parameters instance
    Returns:
        fig: Matplotlib figure
    """
    # Create figure with 3 subplots stacked vertically
    fig = plt.figure(figsize=(18, 10))
    gs = GridSpec(3, 1, figure=fig, height_ratios=[1, 1, 1])

    # Define colors for different parameter types
    colors = {
        'fixed': '#FFD580',     # Light orange for fixed parameters
        'lin': '#D3D3D3',       # Light gray for linear parameters
        'log': '#ACD1E9',       # Light blue for log parameters
        'neglog': '#D8BFD8'     # Light purple for neglog parameters
    }

    # Original parameters
    ax1 = fig.add_subplot(gs[0])
    df1 = params.all_parameters.copy()
    # Format the DataFrame for display
    df1_display = df1[['name', 'min', 'max', 'default', 'scale', 'mode', 'transform']]
    df1_display = df1_display.sort_values(by=['mode', 'name'])

    # Create a table
    table1 = ax1.table(
        cellText=df1_display.values,
        colLabels=df1_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color rows based on parameter type
    for i, row in enumerate(df1_display.iterrows()):
        row_idx = i + 1  # +1 because row 0 is the header
        row_data = row[1]

        # Determine row color
        if row_data['mode'] == 'fixed':
            color = colors['fixed']
        elif row_data.get('transform') == 'log':
            color = colors['log']
        elif row_data.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the row
        for j in range(len(df1_display.columns)):
            table1[(row_idx, j)].set_facecolor(color)

    table1.auto_set_font_size(False)
    table1.set_fontsize(12)
    table1.scale(1, 1.5)
    ax1.axis('tight')
    ax1.axis('off')
    ax1.set_title('Original Parameters')

    # Scaled parameters
    ax2 = fig.add_subplot(gs[1])
    df2 = params.all_parameters_scaled.copy()
    # Format the DataFrame for display
    df2_display = df2[['name', 'min', 'max', 'default', 'scale', 'mode', 'transform']]
    df2_display = df2_display.sort_values(by=['mode', 'name'])

    # Create a table
    table2 = ax2.table(
        cellText=df2_display.values,
        colLabels=df2_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color rows based on parameter type
    for i, row in enumerate(df2_display.iterrows()):
        row_idx = i + 1  # +1 because row 0 is the header
        row_data = row[1]

        # Determine row color
        if row_data['mode'] == 'fixed':
            color = colors['fixed']
        elif row_data.get('transform') == 'log':
            color = colors['log']
        elif row_data.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the row
        for j in range(len(df2_display.columns)):
            table2[(row_idx, j)].set_facecolor(color)

    table2.auto_set_font_size(False)
    table2.set_fontsize(12)
    table2.scale(1, 1.5)
    ax2.axis('tight')
    ax2.axis('off')
    ax2.set_title('Scaled Parameters')

    # Normalized parameters
    ax3 = fig.add_subplot(gs[2])
    df3 = params.all_parameters_normed.copy()
    # Format the DataFrame for display
    df3_display = df3[['name', 'min', 'max', 'default', 'scale', 'mode', 'transform']]
    df3_display = df3_display.sort_values(by=['mode', 'name'])

    # Create a table
    table3 = ax3.table(
        cellText=df3_display.values,
        colLabels=df3_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color rows based on parameter type
    for i, row in enumerate(df3_display.iterrows()):
        row_idx = i + 1  # +1 because row 0 is the header
        row_data = row[1]

        # Determine row color
        if row_data['mode'] == 'fixed':
            color = colors['fixed']
        elif row_data.get('transform') == 'log':
            color = colors['log']
        elif row_data.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the row
        for j in range(len(df3_display.columns)):
            table3[(row_idx, j)].set_facecolor(color)

    table3.auto_set_font_size(False)
    table3.set_fontsize(12)
    table3.scale(1, 1.5)
    ax3.axis('tight')
    ax3.axis('off')
    ax3.set_title('Normalized Parameters')

    plt.tight_layout()
    return fig

def test_with_visualization():
    """
    Test with visualization of parameters.
    This test creates the visualization but doesn't check anything.
    It's useful for manual inspection.
    """
    test_data = create_test_data()
    params = Parameters(test_data)

    # Create visualization
    fig = visualize_parameters(params)

    # Save the figure (optional)
    fig.savefig('parameters_visualization.png', dpi=300, bbox_inches='tight')

    # Display the figure if running in an interactive environment
    plt.show()

    # Close the figure to prevent resource leaks
    # plt.close(fig)

if __name__ == "__main__":
    # When running the script directly, execute tests and show visualization
    test_data = create_test_data()
    params = Parameters(test_data)

    print("Testing initialization and parameter transformation...")
    test_init_from_list()
    test_init_from_dataframe()
    test_transforms()
    test_internal_scaling()
    test_internal_normalization()
    print("All tests passed!")

    # Create and display visualization
    print("Generating visualization...")
    fig = test_with_visualization()
    plt.show()
