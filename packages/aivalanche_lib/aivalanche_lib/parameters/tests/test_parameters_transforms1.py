"""
Tests for transformation functions of the Parameters class.

This test file focuses on testing the array/DataFrame transformation functions:
- denormalize_parameters_array
- descale_parameters_array
- denormalize_and_descale_parameters_array
- scale_parameters_array
- normalize_parameters_array
- scale_and_normalize_parameters_array
"""

import pandas as pd
import numpy as np
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

def create_test_normalized_data():
    """Create sample normalized data for denormalization testing."""
    return pd.DataFrame({
        "linear_positive": [0.0, 0.25, 0.5, 0.75, 1.0],
        "linear_negative": [0.0, 0.25, 0.5, 0.75, 1.0],
        "linear_mixed": [0.0, 0.25, 0.5, 0.75, 1.0],
        "log_small": [0.0, 0.25, 0.5, 0.75, 1.0],
        "log_large": [0.0, 0.25, 0.5, 0.75, 1.0],
        "neglog": [0.0, 0.25, 0.5, 0.75, 1.0]
    })

def create_test_raw_data():
    """Create sample raw (original scale) data for scaling/normalization testing."""
    return pd.DataFrame({
        "linear_positive": [1.0, 3.25, 5.5, 7.75, 10.0],
        "linear_negative": [-10.0, -7.75, -5.5, -3.25, -1.0],
        "linear_mixed": [-5.0, -2.5, 0.0, 2.5, 5.0],
        "log_small": [0.1, 0.3162, 1.0, 3.1623, 10.0],       # Approximates of log scale values
        "log_large": [100.0, 316.2, 1000.0, 3162.3, 10000.0],  # Approximates of log scale values
        "neglog": [-1000.0, -100.0, -10.0, -1.0, -0.1]    # Approximates of neglog scale values
    })

def test_denormalize_parameters_array():
    """Test denormalizing parameters array."""
    params = Parameters(create_test_data())
    normalized_data = create_test_normalized_data()

    # Test denormalizing without fixed parameters
    denormalized = params.denormalize_parameters_array(normalized_data, include_fixed_parameters=False)

    # Verify denormalized values for linear parameters
    assert denormalized["linear_positive"].iloc[0] == params.variable_parameters_scaled.loc[params.variable_parameters_scaled['name'] == 'linear_positive', "min"].values[0]  # min value for 0.0
    assert denormalized["linear_positive"].iloc[4] == params.variable_parameters_scaled.loc[params.variable_parameters_scaled['name'] == 'linear_positive', "max"].values[0]  # max value for 1.0

    # Test denormalizing with fixed parameters
    denormalized_with_fixed = params.denormalize_parameters_array(normalized_data, include_fixed_parameters=True)

    # Verify fixed parameters are added
    assert "fixed_lin_param" in denormalized_with_fixed.columns
    assert "fixed_log_param" in denormalized_with_fixed.columns

    # Verify fixed parameters have their default values
    fixed_lin_param_defaults = params.fixed_parameters_scaled.loc[
        params.fixed_parameters_scaled["name"] == "fixed_lin_param", "default"].values[0]
    assert denormalized_with_fixed["fixed_lin_param"].iloc[0] == fixed_lin_param_defaults

    return params, normalized_data, denormalized_with_fixed

def test_descale_parameters_array():
    """Test descaling parameters array."""
    params = Parameters(create_test_data())
    normalized_data = create_test_normalized_data()

    # First denormalize
    denormalized = params.denormalize_parameters_array(normalized_data, include_fixed_parameters=False)

    # Then descale
    descaled = params.descale_parameters_array(denormalized, include_fixed_parameters=True)

    # Verify log transformations are reversed
    # For log_small: original min=0.1, max=10.0
    # Normalized 0.0 -> -1.0 (scaled) -> 0.1 (descaled)
    # Normalized 1.0 -> 1.0 (scaled) -> 10.0 (descaled)
    assert 0.099 <= descaled["log_small"].iloc[0] <= 0.11  # Should be approx 0.1
    assert 9.9 <= descaled["log_small"].iloc[4] <= 10.1    # Should be approx 10.0

    # For neglog: original min=-1000.0, max=-0.1
    # Normalized 0.0 -> -3.0 (scaled) -> -1000.0 (descaled)
    # Normalized 1.0 -> 1.0 (scaled) -> -0.1 (descaled)
    assert -1100.0 <= descaled["neglog"].iloc[0] <= -900.0  # Should be approx -1000.0
    assert -0.11 <= descaled["neglog"].iloc[4] <= -0.09     # Should be approx -0.1

    return params, denormalized, descaled

def test_denormalize_and_descale_parameters_array():
    """Test combined denormalization and descaling."""
    params = Parameters(create_test_data())
    normalized_data = create_test_normalized_data()

    # Use the combined function
    denorm_descaled = params.denormalize_and_descale_parameters_array(
        normalized_data, include_fixed_parameters=True
    )

    # Verify results match individual operations
    # First denormalize
    denormalized = params.denormalize_parameters_array(
        normalized_data, include_fixed_parameters=True
    )

    # Then descale
    descaled_separate = params.descale_parameters_array(
        denormalized, validate_data=False, include_fixed_parameters=False
    )

    # Compare results
    for col in normalized_data.columns:
        assert np.allclose(
            denorm_descaled[col].values,
            descaled_separate[col].values,
            rtol=1e-10, atol=1e-10
        )

    return params, normalized_data, denorm_descaled

def test_scale_parameters_array():
    """Test scaling parameters array."""
    params = Parameters(create_test_data())
    raw_data = create_test_raw_data()

    # Test scaling without fixed parameters
    scaled = params.scale_parameters_array(raw_data, include_fixed_parameters=False)

    # Verify scaled values for log parameters
    # log_small: min=0.1, max=10.0
    # raw 0.1 -> log10(0.1) = -1.0
    # raw 10.0 -> log10(10.0) = 1.0
    assert -1.1 <= scaled["log_small"].iloc[0] <= -0.9    # Should be approx -1.0
    assert 0.9 <= scaled["log_small"].iloc[4] <= 1.1      # Should be approx 1.0

    # Test scaling with fixed parameters
    scaled_with_fixed = params.scale_parameters_array(raw_data, include_fixed_parameters=True)

    # Verify fixed parameters are added
    assert "fixed_lin_param" in scaled_with_fixed.columns
    assert "fixed_log_param" in scaled_with_fixed.columns

    return params, raw_data, scaled_with_fixed

def test_normalize_parameters_array():
    """Test normalizing parameters array."""
    params = Parameters(create_test_data())
    raw_data = create_test_raw_data()

    # First scale
    scaled = params.scale_parameters_array(raw_data, include_fixed_parameters=False)

    # Then normalize
    normalized = params.normalize_parameters_array(scaled, include_fixed_parameters=True)

    # Verify normalization (all values should be between 0 and 1)
    for col in normalized.columns:
        assert normalized[col].min() >= 0
        assert normalized[col].max() <= 1

    # Specific checks for linear parameters
    # linear_positive: min=1.0, max=10.0
    # raw 1.0 -> norm 0.0
    # raw 10.0 -> norm 1.0
    assert 0 <= normalized["linear_positive"].iloc[0] <= 0.01  # Should be approx 0.0
    assert 0.99 <= normalized["linear_positive"].iloc[4] <= 1  # Should be approx 1.0

    return params, scaled, normalized

def test_scale_and_normalize_parameters_array():
    """Test combined scaling and normalizing."""
    params = Parameters(create_test_data())
    raw_data = create_test_raw_data()

    # Use the combined function
    scaled_normalized = params.scale_and_normalize_parameters_array(
        raw_data, include_fixed_parameters=True
    )

    # Verify results match individual operations
    # First scale
    scaled = params.scale_parameters_array(
        raw_data, include_fixed_parameters=True
    )

    # Then normalize
    normalized_separate = params.normalize_parameters_array(
        scaled, validate_data=False, include_fixed_parameters=True
    )

    # Compare results
    for col in raw_data.columns:
        assert np.allclose(
            scaled_normalized[col].values,
            normalized_separate[col].values,
            rtol=1e-10, atol=1e-10
        )

    return params, raw_data, scaled_normalized

def visualize_denormalize_descale(params, normalized_data, denormalized, descaled, denorm_descaled):
    """
    Create a visualization for denormalization and descaling process.

    Args:
        params: Parameters instance
        normalized_data: Input normalized data
        denormalized: Denormalized data
        descaled: Descaled data
        denorm_descaled: Combined denormalized and descaled data

    Returns:
        fig: Matplotlib figure
    """
    # Create figure with grid layout
    fig = plt.figure(figsize=(25, 10))
    gs = GridSpec(3, 2, figure=fig)

    # Define colors for different parameter types
    colors = {
        'fixed': '#FFD580',     # Light orange for fixed parameters
        'lin': '#D3D3D3',       # Light gray for linear parameters
        'log': '#ACD1E9',       # Light blue for log parameters
        'neglog': '#D8BFD8'     # Light purple for neglog parameters
    }

    # Row 1: Original parameters
    ax1 = fig.add_subplot(gs[0, :])
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
    table1.set_fontsize(10)
    table1.scale(1, 1.5)
    ax1.axis('tight')
    ax1.axis('off')
    ax1.set_title('Original Parameters')

    # Row 2, Left: Input normalized data
    ax2_left = fig.add_subplot(gs[1, 0])
    # Round to 4 decimal places for display
    normalized_display = normalized_data.round(4)

    # Create a table
    table2_left = ax2_left.table(
        cellText=normalized_display.values,
        colLabels=normalized_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color columns based on parameter type
    for col_idx, col_name in enumerate(normalized_display.columns):
        param = params.get_parameter(col_name)
        if param['mode'] == 'fixed':
            color = colors['fixed']
        elif param.get('transform') == 'log':
            color = colors['log']
        elif param.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the column except header
        for row_idx in range(1, len(normalized_display) + 1):
            table2_left[(row_idx, col_idx)].set_facecolor(color)

    table2_left.auto_set_font_size(False)
    table2_left.set_fontsize(10)
    table2_left.scale(1, 1.5)
    ax2_left.axis('tight')
    ax2_left.axis('off')
    ax2_left.set_title('Input Normalized Data')

    # Row 2, Right: Denormalized data
    ax2_right = fig.add_subplot(gs[1, 1])
    # Round to 4 decimal places for display
    denormalized_display = denormalized.round(4)

    # Create a table
    table2_right = ax2_right.table(
        cellText=denormalized_display.values,
        colLabels=denormalized_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color columns based on parameter type
    for col_idx, col_name in enumerate(denormalized_display.columns):
        param = params.get_parameter(col_name)
        if param['mode'] == 'fixed':
            color = colors['fixed']
        elif param.get('transform') == 'log':
            color = colors['log']
        elif param.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the column except header
        for row_idx in range(1, len(denormalized_display) + 1):
            table2_right[(row_idx, col_idx)].set_facecolor(color)

    table2_right.auto_set_font_size(False)
    table2_right.set_fontsize(10)
    table2_right.scale(1, 1.5)
    ax2_right.axis('tight')
    ax2_right.axis('off')
    ax2_right.set_title('Denormalized Data (Still in Scaled Space)')

    # Row 3, Left: Descaled data
    ax3_left = fig.add_subplot(gs[2, 0])
    # Round to 4 decimal places for display
    descaled_display = descaled.round(4)

    # Create a table
    table3_left = ax3_left.table(
        cellText=descaled_display.values,
        colLabels=descaled_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color columns based on parameter type
    for col_idx, col_name in enumerate(descaled_display.columns):
        param = params.get_parameter(col_name)
        if param['mode'] == 'fixed':
            color = colors['fixed']
        elif param.get('transform') == 'log':
            color = colors['log']
        elif param.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the column except header
        for row_idx in range(1, len(descaled_display) + 1):
            table3_left[(row_idx, col_idx)].set_facecolor(color)

    table3_left.auto_set_font_size(False)
    table3_left.set_fontsize(10)
    table3_left.scale(1, 1.5)
    ax3_left.axis('tight')
    ax3_left.axis('off')
    ax3_left.set_title('Descaled Data (After Applying Inverse Log Transform)')

    # Row 3, Right: Denormalized and descaled data
    ax3_right = fig.add_subplot(gs[2, 1])
    # Round to 4 decimal places for display
    denorm_descaled_display = denorm_descaled.round(4)

    # Create a table
    table3_right = ax3_right.table(
        cellText=denorm_descaled_display.values,
        colLabels=denorm_descaled_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color columns based on parameter type
    for col_idx, col_name in enumerate(denorm_descaled_display.columns):
        param = params.get_parameter(col_name)
        if param['mode'] == 'fixed':
            color = colors['fixed']
        elif param.get('transform') == 'log':
            color = colors['log']
        elif param.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the column except header
        for row_idx in range(1, len(denorm_descaled_display) + 1):
            table3_right[(row_idx, col_idx)].set_facecolor(color)

    table3_right.auto_set_font_size(False)
    table3_right.set_fontsize(10)
    table3_right.scale(1, 1.5)
    ax3_right.axis('tight')
    ax3_right.axis('off')
    ax3_right.set_title('Denormalized and Descaled Data (Original Space)')

    return fig

def visualize_scale_normalize(params, raw_data, scaled, normalized):
    """
    Create a visualization for scaling and normalization process.

    Args:
        params: Parameters instance
        raw_data: Input raw data
        scaled: Scaled data
        normalized: Normalized data

    Returns:
        fig: Matplotlib figure
    """
    # Create figure with grid layout
    fig = plt.figure(figsize=(25, 10))
    gs = GridSpec(3, 2, figure=fig)

    # Define colors for different parameter types
    colors = {
        'fixed': '#FFD580',     # Light orange for fixed parameters
        'lin': '#D3D3D3',       # Light gray for linear parameters
        'log': '#ACD1E9',       # Light blue for log parameters
        'neglog': '#D8BFD8'     # Light purple for neglog parameters
    }

    # Row 1: Original parameters
    ax1 = fig.add_subplot(gs[0, :])
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
    table1.set_fontsize(10)
    table1.scale(1, 1.5)
    ax1.axis('tight')
    ax1.axis('off')
    ax1.set_title('Original Parameters')

    # Row 2, Left: Input raw data
    ax2_left = fig.add_subplot(gs[1, 0])
    # Round to 4 decimal places for display
    raw_display = raw_data.round(4)

    # Create a table
    table2_left = ax2_left.table(
        cellText=raw_display.values,
        colLabels=raw_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color columns based on parameter type
    for col_idx, col_name in enumerate(raw_display.columns):
        param = params.get_parameter(col_name)
        if param['mode'] == 'fixed':
            color = colors['fixed']
        elif param.get('transform') == 'log':
            color = colors['log']
        elif param.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the column except header
        for row_idx in range(1, len(raw_display) + 1):
            table2_left[(row_idx, col_idx)].set_facecolor(color)

    table2_left.auto_set_font_size(False)
    table2_left.set_fontsize(10)
    table2_left.scale(1, 1.5)
    ax2_left.axis('tight')
    ax2_left.axis('off')
    ax2_left.set_title('Input Raw Data (Original Space)')

    # Row 2, Right: Scaled data
    ax2_right = fig.add_subplot(gs[1, 1])
    # Round to 4 decimal places for display
    scaled_display = scaled.round(4)

    # Create a table
    table2_right = ax2_right.table(
        cellText=scaled_display.values,
        colLabels=scaled_display.columns,
        loc='center',
        cellLoc='center'
    )

    # Color columns based on parameter type
    for col_idx, col_name in enumerate(scaled_display.columns):
        param = params.get_parameter(col_name)
        if param['mode'] == 'fixed':
            color = colors['fixed']
        elif param.get('transform') == 'log':
            color = colors['log']
        elif param.get('transform') == 'neglog':
            color = colors['neglog']
        else:
            color = colors['lin']

        # Apply color to all cells in the column except header
        for row_idx in range(1, len(scaled_display) + 1):
            table2_right[(row_idx, col_idx)].set_facecolor(color)

    table2_right.auto_set_font_size(False)
    table2_right.set_fontsize(10)
    table2_right.scale(1, 1.5)
    ax2_right.axis('tight')
    ax2_right.axis('off')
    ax2_right.set_title('Scaled Data (After Log Transform)')

    # Row 3, Left and Right: Normalized data (same in both places for symmetry)
    for idx, pos in enumerate(['left', 'right']):
        if pos == 'left':
            ax = fig.add_subplot(gs[2, 0])
            title = 'Normalized Data (0-1 Range)'
        else:
            ax = fig.add_subplot(gs[2, 1])
            title = 'Scale and Normalize Combined Result'

        # Round to 4 decimal places for display
        normalized_display = normalized.round(4)

        # Create a table
        table = ax.table(
            cellText=normalized_display.values,
            colLabels=normalized_display.columns,
            loc='center',
            cellLoc='center'
        )

        # Color columns based on parameter type
        for col_idx, col_name in enumerate(normalized_display.columns):
            param = params.get_parameter(col_name)
            if param['mode'] == 'fixed':
                color = colors['fixed']
            elif param.get('transform') == 'log':
                color = colors['log']
            elif param.get('transform') == 'neglog':
                color = colors['neglog']
            else:
                color = colors['lin']

            # Apply color to all cells in the column except header
            for row_idx in range(1, len(normalized_display) + 1):
                table[(row_idx, col_idx)].set_facecolor(color)

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        ax.axis('tight')
        ax.axis('off')
        ax.set_title(title)

    return fig

def run_tests_and_visualize():
    """Run all tests and generate visualizations."""
    print("Testing denormalization and descaling functions...")
    params, normalized_data, denormalized = test_denormalize_parameters_array()
    _, denorm_for_descale, descaled = test_descale_parameters_array()
    _, _, denorm_descaled = test_denormalize_and_descale_parameters_array()

    print("Testing scaling and normalization functions...")
    params, raw_data, scaled = test_scale_parameters_array()
    _, scaled_for_norm, normalized = test_normalize_parameters_array()
    _, _, scale_normalized = test_scale_and_normalize_parameters_array()

    print("Generating visualizations...")
    fig1 = visualize_denormalize_descale(params, normalized_data, denormalized, descaled, denorm_descaled)
    fig2 = visualize_scale_normalize(params, raw_data, scaled, normalized)

    fig1.savefig("denormalize_descale_visualization.png", dpi=300, bbox_inches='tight')
    fig2.savefig("scale_normalize_visualization.png", dpi=300, bbox_inches='tight')

    return fig1, fig2

if __name__ == "__main__":
    # When running the script directly, execute tests and show visualizations
    figs = run_tests_and_visualize()
    plt.show()
