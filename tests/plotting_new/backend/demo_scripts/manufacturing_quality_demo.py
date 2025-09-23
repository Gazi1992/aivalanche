"""
Manufacturing & Quality Demo
Real-world manufacturing examples including process control, defect analysis, and production metrics
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_manufacturing_plots():
    """Create manufacturing and quality visualizations"""
    plots = []

    # 1. Control Chart - Process Monitoring
    # Simulating daily quality measurements
    dates = pd.date_range('2024-01-01', periods=60, freq='D')
    target = 100
    ucl = 103  # Upper control limit
    lcl = 97   # Lower control limit

    # Process data with some out-of-control points
    np.random.seed(42)
    measurements = np.random.normal(target, 0.8, 60)
    # Add some out-of-control points
    measurements[15:18] = np.random.normal(104, 0.3, 3)
    measurements[35] = 96
    measurements[45:47] = np.random.normal(103.5, 0.2, 2)

    fig1 = go.Figure()

    # Measurements
    fig1.add_trace(go.Scatter(
        x=dates,
        y=measurements,
        mode='lines+markers',
        name='Measurements',
        marker=dict(
            size=8,
            color=['red' if (m > ucl or m < lcl) else 'blue' for m in measurements]
        ),
        line=dict(color='gray', width=1)
    ))

    # Control limits
    fig1.add_hline(y=target, line_dash="solid", line_color="green",
                   annotation_text="Target", annotation_position="right")
    fig1.add_hline(y=ucl, line_dash="dash", line_color="red",
                   annotation_text="UCL", annotation_position="right")
    fig1.add_hline(y=lcl, line_dash="dash", line_color="red",
                   annotation_text="LCL", annotation_position="right")

    fig1.update_layout(
        title="Statistical Process Control Chart",
        xaxis_title="Date",
        yaxis_title="Measurement Value",
        hovermode='x unified'
    )
    plots.append(('mfg_control_chart', fig1, {
        'appearance': {'title': {'text': 'Process Control Chart'}}
    }))

    # 2. Defect Pareto Chart
    defect_types = ['Scratches', 'Dimensions', 'Color', 'Assembly', 'Packaging',
                    'Material', 'Electrical', 'Other']
    defect_counts = [145, 89, 67, 45, 32, 28, 15, 12]
    cumulative_pct = np.cumsum(defect_counts) / sum(defect_counts) * 100

    fig2 = go.Figure()

    # Bar chart for defects
    fig2.add_trace(go.Bar(
        x=defect_types,
        y=defect_counts,
        name='Defect Count',
        marker_color='lightblue',
        yaxis='y'
    ))

    # Line chart for cumulative percentage
    fig2.add_trace(go.Scatter(
        x=defect_types,
        y=cumulative_pct,
        mode='lines+markers',
        name='Cumulative %',
        marker=dict(color='red', size=8),
        line=dict(color='red', width=2),
        yaxis='y2'
    ))

    # Add 80% reference line
    fig2.add_hline(y=80, line_dash="dash", line_color="orange",
                   annotation_text="80%")

    fig2.update_layout(
        title="Defect Analysis - Pareto Chart",
        xaxis_title="Defect Type",
        yaxis=dict(title="Count", side="left"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 100]),
        hovermode='x unified'
    )
    plots.append(('mfg_pareto', fig2, {
        'appearance': {'title': {'text': 'Defect Analysis'}}
    }))

    # 3. Process Capability Histogram
    # Simulating part measurements
    spec_lower = 49.5
    spec_upper = 50.5
    measurements_parts = np.random.normal(50.0, 0.15, 500)

    fig3 = go.Figure()

    # Histogram
    fig3.add_trace(go.Histogram(
        x=measurements_parts,
        nbinsx=30,
        name='Measurements',
        marker_color='lightgreen',
        opacity=0.7
    ))

    # Add specification limits
    fig3.add_vline(x=spec_lower, line_dash="dash", line_color="red",
                   annotation_text="LSL", annotation_position="top")
    fig3.add_vline(x=spec_upper, line_dash="dash", line_color="red",
                   annotation_text="USL", annotation_position="top")
    fig3.add_vline(x=np.mean(measurements_parts), line_dash="solid", line_color="blue",
                   annotation_text="Mean", annotation_position="top")

    # Calculate Cpk
    mean_val = np.mean(measurements_parts)
    std_val = np.std(measurements_parts)
    cpu = (spec_upper - mean_val) / (3 * std_val)
    cpl = (mean_val - spec_lower) / (3 * std_val)
    cpk = min(cpu, cpl)

    fig3.update_layout(
        title=f"Process Capability Analysis - Cpk: {cpk:.2f}",
        xaxis_title="Measurement (mm)",
        yaxis_title="Frequency"
    )
    plots.append(('mfg_capability', fig3, {
        'appearance': {'title': {'text': 'Process Capability'}}
    }))

    # 4. Production Flow Sankey
    fig4 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Raw Material", "Station 1", "Station 2", "Station 3",
                   "Quality Check", "Finished Goods", "Rework", "Scrap"],
            color=["blue", "green", "green", "green", "orange", "darkgreen", "yellow", "red"]
        ),
        link=dict(
            source=[0, 1, 2, 3, 4, 4, 4, 6, 1, 2, 3],  # indices correspond to labels
            target=[1, 2, 3, 4, 5, 6, 7, 2, 7, 7, 7],
            value=[1000, 980, 960, 940, 880, 50, 10, 45, 20, 20, 20]
        )
    )])

    fig4.update_layout(
        title="Production Flow Analysis",
        font_size=10
    )
    plots.append(('mfg_flow', fig4, {
        'appearance': {'title': {'text': 'Production Flow'}}
    }))

    # 5. OEE (Overall Equipment Effectiveness) Indicator
    fig5 = go.Figure()

    # OEE components
    availability = 92
    performance = 95
    quality = 98
    oee = (availability * performance * quality) / 10000

    fig5.add_trace(go.Indicator(
        mode="gauge+number",
        value=oee,
        title={'text': "Overall Equipment Effectiveness (%)"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 50], 'color': "red"},
                   {'range': [50, 75], 'color': "yellow"},
                   {'range': [75, 85], 'color': "lightgreen"},
                   {'range': [85, 100], 'color': "green"}],
               'threshold': {'line': {'color': "black", 'width': 4},
                           'thickness': 0.75, 'value': 85}},
        domain={'x': [0.25, 0.75], 'y': [0.4, 1]}
    ))

    # Component bars
    fig5.add_trace(go.Bar(
        x=['Availability', 'Performance', 'Quality'],
        y=[availability, performance, quality],
        text=[f'{v}%' for v in [availability, performance, quality]],
        textposition='outside',
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
        showlegend=False
    ))

    fig5.update_layout(
        title="OEE Dashboard",
        yaxis=dict(range=[0, 100], title="Percentage", domain=[0, 0.35]),
        xaxis=dict(domain=[0, 1])
    )
    plots.append(('mfg_oee', fig5, {
        'appearance': {'title': {'text': 'OEE Dashboard'}}
    }))

    # 6. Batch Quality Heatmap
    # Simulating quality scores across batches and parameters
    batches = [f'Batch {i}' for i in range(1, 21)]
    parameters = ['Temperature', 'Pressure', 'Speed', 'pH', 'Viscosity', 'Density']

    # Quality scores (0-100)
    quality_scores = np.random.normal(85, 10, (len(parameters), len(batches)))
    quality_scores = np.clip(quality_scores, 0, 100)

    # Add some problem areas
    quality_scores[1, 5:8] = np.random.normal(60, 5, 3)  # Pressure issues in batches 6-8
    quality_scores[3, 12:15] = np.random.normal(65, 5, 3)  # pH issues in batches 13-15

    fig6 = go.Figure(data=go.Heatmap(
        z=quality_scores,
        x=batches,
        y=parameters,
        colorscale=[[0, 'red'], [0.5, 'yellow'], [1, 'green']],
        text=quality_scores.round(0),
        texttemplate='%{text}',
        textfont={"size": 8},
        colorbar=dict(title="Quality Score")
    ))

    fig6.update_layout(
        title="Batch Quality Matrix",
        xaxis_title="Batch Number",
        yaxis_title="Quality Parameter"
    )
    plots.append(('mfg_batch_quality', fig6, {
        'appearance': {'title': {'text': 'Batch Quality'}}
    }))

    # 7. Equipment Efficiency Waterfall
    categories = ['Planned Time', 'Breakdown', 'Changeover', 'Minor Stops',
                  'Speed Loss', 'Quality Loss', 'Net Production']
    values = [480, -30, -45, -20, -35, -15, 335]

    fig7 = go.Figure(go.Waterfall(
        x=categories,
        y=values,
        text=[f"{v:+.0f} min" if v < 0 else f"{v:.0f} min" for v in values],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "red"}},
        increasing={"marker": {"color": "green"}},
        totals={"marker": {"color": "blue"}}
    ))

    fig7.update_layout(
        title="Daily Production Time Analysis",
        yaxis_title="Time (minutes)",
        showlegend=False
    )
    plots.append(('mfg_time_analysis', fig7, {
        'appearance': {'title': {'text': 'Time Analysis'}}
    }))

    # 8. Multi-Line Quality Trends
    weeks = [f'W{i}' for i in range(1, 13)]
    line_a = [95, 94, 96, 97, 96, 98, 97, 99, 98, 99, 99, 100]
    line_b = [92, 93, 94, 93, 95, 94, 96, 95, 97, 96, 98, 97]
    line_c = [88, 89, 90, 92, 91, 93, 94, 95, 94, 96, 95, 97]

    fig8 = go.Figure()

    fig8.add_trace(go.Scatter(
        x=weeks, y=line_a,
        mode='lines+markers',
        name='Line A',
        line=dict(color='green', width=2),
        marker=dict(size=8)
    ))

    fig8.add_trace(go.Scatter(
        x=weeks, y=line_b,
        mode='lines+markers',
        name='Line B',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))

    fig8.add_trace(go.Scatter(
        x=weeks, y=line_c,
        mode='lines+markers',
        name='Line C',
        line=dict(color='orange', width=2),
        marker=dict(size=8)
    ))

    # Add target line
    fig8.add_hline(y=95, line_dash="dash", line_color="red",
                   annotation_text="Target", annotation_position="right")

    fig8.update_layout(
        title="Production Line Quality Trends",
        xaxis_title="Week",
        yaxis_title="Quality Score (%)",
        hovermode='x unified'
    )
    plots.append(('mfg_line_trends', fig8, {
        'appearance': {'title': {'text': 'Line Quality Trends'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} manufacturing and quality visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_manufacturing_plots()
    print(result)