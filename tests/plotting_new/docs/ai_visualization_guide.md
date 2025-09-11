# AI Visualization Guide

This document provides guidance for the AI system on how to interpret user requests and generate appropriate visualizations.

## User Intent Mapping

### When user says "show me the data"
- If numeric columns ≤ 3: Create scatter matrix
- If numeric columns > 3: Create parallel coordinates plot
- Add histogram for main numeric column

### When user says "plot X vs Y"
- If both continuous: Create scatter plot
- If X is time/ordered: Create line plot
- If X categorical, Y continuous: Create bar plot

### When user says "show distribution"
- Create histogram for each numeric column
- Use 30 bins by default
- Consider box plots for comparison

### When user says "compare"
- Multiple series: Line plot with multiple traces
- Categories: Grouped bar plot
- Distributions: Side-by-side histograms

### When user says "analyze relationships"
- 2 variables: Scatter plot
- 3-5 variables: Scatter matrix
- 5+ variables: Parallel coordinates

### When user says "show trends"
- Line plot with time on x-axis
- Add trend line if requested
- Consider moving average

## Common Mistakes to Avoid

1. **Wrong source file**: Always use the actual filename from the data cache
2. **Wrong column names**: Use exact column names, case-sensitive
3. **Wrong plot type**: Match plot type to data type (categorical vs continuous)
4. **Missing data handling**: Check for null values before plotting
5. **Scale issues**: Consider log scale for highly skewed data

## Plot Type Decision Tree

```
Is it time series data?
├─ Yes → Line plot
└─ No → How many variables?
    ├─ 1 variable
    │   ├─ Continuous → Histogram
    │   └─ Categorical → Bar plot (counts)
    ├─ 2 variables
    │   ├─ Both continuous → Scatter plot
    │   ├─ One categorical → Bar plot
    │   └─ Both categorical → Grouped bar
    └─ 3+ variables
        ├─ All continuous → Parallel coordinates
        ├─ Mix of types → Multiple subplots
        └─ Want pairwise → Scatter matrix
```

## Configuration Examples

### Example 1: Time Series Request
User: "Show me temperature over time"
```json
{
  "theme": "light",
  "figures": [{
    "id": "figure_1",
    "visibility": true,
    "x_label": "Time",
    "y_label": "Temperature",
    "items": [{
      "id": "line_1",
      "type": "line",
      "source": "temperature_data.csv",
      "x_column": "timestamp",
      "y_column": "temperature",
      "legend_name": "Temperature",
      "line_style": "solid"
    }]
  }]
}
```

### Example 2: Correlation Request
User: "Show me how voltage relates to current"
```json
{
  "theme": "light",
  "figures": [{
    "id": "figure_1",
    "visibility": true,
    "x_label": "Voltage (V)",
    "y_label": "Current (A)",
    "items": [{
      "id": "scatter_1",
      "type": "scatter",
      "source": "electrical_data.csv",
      "x_column": "voltage",
      "y_column": "current",
      "legend_name": "V-I Characteristic",
      "marker_style": "circle"
    }]
  }]
}
```

### Example 3: Distribution Request
User: "Show me the distribution of values"
```json
{
  "theme": "light",
  "figures": [{
    "id": "figure_1",
    "visibility": true,
    "x_label": "Value",
    "y_label": "Frequency",
    "items": [{
      "id": "hist_1",
      "type": "histogram",
      "source": "data.csv",
      "column": "value",
      "bins": 30,
      "legend_name": "Distribution"
    }]
  }]
}
```

### Example 4: Multi-dimensional Request
User: "Compare all parameters"
```json
{
  "theme": "light",
  "figures": [{
    "id": "figure_1",
    "visibility": true,
    "items": [{
      "id": "pcp_1",
      "type": "parallel_coordinates",
      "source": "parameters.csv",
      "columns": ["param1", "param2", "param3", "param4"],
      "legend_name": "All Parameters"
    }]
  }]
}
```

## Response Templates

### Successful visualization:
"I've created [N] visualization(s) ([plot types]) based on your request. The plots show [brief description of what's visualized]."

### Need more information:
"To create the visualization, I need to know which columns to plot. Available columns are: [list]. What would you like to visualize?"

### Data needed:
"Please provide a data file first. You can upload a file using the 📎 button or describe which file to load."

### Error handling:
"I encountered an issue creating the visualization: [error]. Would you like me to try a different approach?"

## Best Practices

1. **Always validate data before plotting**
   - Check column existence
   - Check data types
   - Handle missing values

2. **Use appropriate scales**
   - Linear for most data
   - Log for exponential growth
   - Categorical for discrete values

3. **Set meaningful labels**
   - Include units when known
   - Use descriptive titles
   - Keep legends concise

4. **Optimize layout**
   - Layout is now controlled via interactive column selector (1-4 columns)
   - Grid automatically adjusts rows based on figure count and selected columns

5. **Color usage**
   - Use color to distinguish series
   - Consider colorblind-friendly palettes
   - Limit to 5-7 distinct colors