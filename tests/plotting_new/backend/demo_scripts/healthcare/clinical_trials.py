"""
Clinical Trial Results
Visualizing treatment response rates, survival curves, and biomarker analysis
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# === Generate realistic clinical trial data ===
np.random.seed(42)

# === Visualization 1: Sankey Diagram - Patient Treatment Pathways ===
# Define patient flow through treatment options
sankey_data = {
    'source': [
        0, 0, 0,           # Initial screening to arms
        1, 1, 2, 2, 3, 3,  # Treatment arms to outcomes
        4, 4, 5, 5, 6, 6    # Outcomes to long-term
    ],
    'target': [
        1, 2, 3,           # To treatment arms
        4, 5, 4, 6, 5, 6,  # To outcomes
        7, 8, 7, 8, 7, 8   # To long-term status
    ],
    'value': [
        340, 310, 350,     # Patient allocation
        240, 100, 180, 130, 200, 150,  # Treatment results
        350, 70, 200, 80, 250, 80      # Long-term outcomes
    ],
    'labels': [
        'Enrolled (1000)',        # 0
        'Standard Treatment',      # 1
        'New Drug A',             # 2
        'New Drug B',             # 3
        'Complete Response',       # 4
        'Partial Response',        # 5
        'No Response',            # 6
        'Disease Free',           # 7
        'Relapsed'                # 8
    ],
    'colors': [
        '#3498db',  # Enrolled
        '#95a5a6',  # Standard
        '#27ae60',  # Drug A
        '#e74c3c',  # Drug B
        '#2ecc71',  # Complete Response
        '#f39c12',  # Partial Response
        '#c0392b',  # No Response
        '#16a085',  # Disease Free
        '#d35400'   # Relapsed
    ]
}

fig1 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=sankey_data['labels'],
        color=sankey_data['colors']
    ),
    link=dict(
        source=sankey_data['source'],
        target=sankey_data['target'],
        value=sankey_data['value'],
        color='rgba(0,0,0,0.1)'
    )
)])

fig1.update_layout(
    title={
        'text': 'Clinical Trial Patient Flow Analysis',
        'x': 0.5,
        'xanchor': 'center'
    },
    font_size=10
)

register_plot(
    fig1,
    plot_id='patient_flow_sankey',
    metadata={
        'appearance': {
            'title': {'text': 'Treatment Pathways'}
        }
    }
)

# === Visualization 2: Kaplan-Meier Survival Curves ===
# Generate survival data for three treatment groups
time_points = np.arange(0, 61, 1)  # 60 months

# Different survival profiles for each treatment
def generate_survival_curve(median_survival, n_patients=100):
    """Generate Kaplan-Meier survival data"""
    survival_prob = []
    current_prob = 1.0

    for t in time_points:
        # Exponential decay with different rates
        hazard = 1.0 / median_survival
        prob_survive = np.exp(-hazard * t)
        # Add some noise
        prob_survive += np.random.normal(0, 0.02)
        prob_survive = np.clip(prob_survive, 0, current_prob)
        survival_prob.append(prob_survive)
        current_prob = prob_survive

    return survival_prob

treatments = {
    'Standard Care': generate_survival_curve(24),
    'Drug A': generate_survival_curve(36),
    'Drug B': generate_survival_curve(42)
}

fig2 = go.Figure()

colors = {'Standard Care': '#95a5a6', 'Drug A': '#27ae60', 'Drug B': '#e74c3c'}

for treatment, survival in treatments.items():
    fig2.add_trace(go.Scatter(
        x=time_points,
        y=survival,
        mode='lines',
        name=treatment,
        line=dict(color=colors[treatment], width=3),
        hovertemplate='<b>%{fullData.name}</b><br>Time: %{x} months<br>Survival: %{y:.1%}<extra></extra>'
    ))

    # Add confidence interval bands
    upper = np.array(survival) + 0.05
    lower = np.array(survival) - 0.05

    fig2.add_trace(go.Scatter(
        x=np.concatenate([time_points, time_points[::-1]]),
        y=np.concatenate([upper, lower[::-1]]),
        fill='toself',
        fillcolor=colors[treatment],
        opacity=0.2,
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add median survival lines
fig2.add_hline(y=0.5, line_dash="dash", line_color="gray",
               annotation_text="Median Survival")

fig2.update_layout(
    title={
        'text': 'Kaplan-Meier Survival Curves',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Time (months)', range=[0, 60]),
    yaxis=dict(title='Survival Probability', range=[0, 1], tickformat='.0%'),
    hovermode='x unified',
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.98,
        xanchor="right",
        x=0.98
    )
)

register_plot(
    fig2,
    plot_id='survival_curves',
    metadata={
        'appearance': {
            'title': {'text': 'Survival Analysis'}
        }
    }
)

# === Visualization 3: Biomarker Heatmap ===
# Generate biomarker expression data
biomarkers = ['CD3', 'CD4', 'CD8', 'PD-1', 'PD-L1', 'CTLA-4', 'TNF-α', 'IL-6', 'IL-10', 'IFN-γ']
patient_groups = ['Responders', 'Partial Resp.', 'Non-Responders']
timepoints = ['Baseline', 'Week 2', 'Week 4', 'Week 8', 'Week 12']

# Generate expression levels
expression_matrix = []
for group in patient_groups:
    group_data = []
    for timepoint in timepoints:
        # Different patterns for different groups
        if group == 'Responders':
            base = np.random.uniform(0.5, 1.0, len(biomarkers))
            if timepoint != 'Baseline':
                base *= np.random.uniform(1.2, 1.5)  # Increase over time
        elif group == 'Partial Resp.':
            base = np.random.uniform(0.3, 0.7, len(biomarkers))
            if timepoint != 'Baseline':
                base *= np.random.uniform(0.9, 1.2)  # Slight change
        else:
            base = np.random.uniform(0.1, 0.5, len(biomarkers))
            if timepoint != 'Baseline':
                base *= np.random.uniform(0.8, 1.0)  # Decrease

        group_data.extend(base)
    expression_matrix.append(group_data)

# Create labels for heatmap
y_labels = []
for group in patient_groups:
    for _ in timepoints:
        y_labels.append(group)

x_labels = []
for _ in patient_groups:
    for timepoint in timepoints:
        x_labels.append(timepoint)

# Reshape data for heatmap
z_data = np.array(expression_matrix).reshape(len(patient_groups) * len(timepoints), len(biomarkers))

fig3 = go.Figure(data=go.Heatmap(
    z=z_data.T,
    x=[f"{group}<br>{time}" for group in patient_groups for time in timepoints],
    y=biomarkers,
    colorscale='RdYlBu_r',
    colorbar=dict(title='Expression<br>Level'),
    hovertemplate='Biomarker: %{y}<br>Group/Time: %{x}<br>Level: %{z:.2f}<extra></extra>'
))

# Add vertical lines to separate patient groups
for i in range(1, len(patient_groups)):
    fig3.add_vline(x=i*len(timepoints)-0.5, line_width=2, line_color="white")

fig3.update_layout(
    title={
        'text': 'Biomarker Expression Profiles',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Patient Group / Timepoint',
        tickangle=45
    ),
    yaxis=dict(title='Biomarker')
)

register_plot(
    fig3,
    plot_id='biomarker_heatmap',
    metadata={
        'appearance': {
            'title': {'text': 'Immunotherapy Response Markers'}
        }
    }
)