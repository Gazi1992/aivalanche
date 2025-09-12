# AI Visualization Guide

This document provides guidance for the AI system on how to interpret user requests and generate appropriate visualizations.

## Metadata Architecture

The application uses a fixed metadata structure where all visual properties are always defined with defaults. The metadata is the single source of truth for all plot rendering. Key components:

- **metadataStructure.js**: Defines the complete fixed structure with all properties and defaults
- **figureManager.js**: Manages figures with embedded metadata and generates Plotly layouts from metadata
- **Python Executor**: Can only update specific metadata values, never change the structure

### Metadata Structure Overview
```javascript
{
  appearance: {
    title: { visible, text, alignment, fontSize, color, bold, italic },
    axes: {
      x: { label, ticks, range, scale, grid },
      y: { label, ticks, range, scale, grid }
    },
    legend: { visible, position, fontSize, color, backgroundColor },
    background: { figure, plot },
    margins: { left, right, top, bottom }
  },
  data: { traces, selectedTraceIndex },
  capabilities: { hasAxes, hasLegend },
  customization: { userModified, pythonModified }
}
```

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

## Python Script Integration

When generating Python scripts that create visualizations:

1. **Import plotly**: Scripts should use `import plotly.graph_objects as go`
2. **Create figures**: Use standard Plotly API to create figures
3. **Set metadata**: Use `fig.update_layout()` to set visual properties that will be extracted into metadata
4. **Register plots**: Call `register_plot(fig)` to make the plot available to the frontend

### Example Python Script with Metadata
```python
import plotly.graph_objects as go

# Create figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6], name="Data"))

# Set metadata through layout
fig.update_layout(
    title=dict(text="My Plot", x=0.5, xanchor="center"),
    xaxis_title="X Label",
    yaxis_title="Y Label",
    showlegend=True,
    legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)")
)

# Register the plot
register_plot(fig)
```

The layout properties are automatically extracted and mapped to the fixed metadata structure. Properties not specified in the Python script retain their default values from the metadata structure.

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

## Theme System Integration

The application uses CSS variables for theming, with all plot margins and spacing values coming from `themes.css`:

- `--plot-margin-left`: Default 80px
- `--plot-margin-right`: Default 50px  
- `--plot-margin-top`: Default 60px
- `--plot-margin-bottom`: Default 60px
- `--plot-margin-pad`: Default 10px
- `--plot-h-gap`: Horizontal gap between plots
- `--plot-v-gap`: Vertical gap between plots

These values are automatically applied when generating layouts from metadata, ensuring consistent spacing across all themes.