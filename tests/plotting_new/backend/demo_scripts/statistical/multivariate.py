"""
🧪 Multivariate Statistical Analysis
Advanced statistical visualizations for high-dimensional data
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np

# Generate synthetic multivariate dataset (similar to Iris but for materials)
np.random.seed(42)

# Material properties dataset
materials = []
material_types = ['Metal', 'Polymer', 'Ceramic', 'Composite']

for mat_type in material_types:
    n_samples = 50

    if mat_type == 'Metal':
        base = {'tensile': 500, 'density': 7.8, 'thermal': 50, 'cost': 30, 'hardness': 200}
        std = {'tensile': 100, 'density': 0.5, 'thermal': 10, 'cost': 5, 'hardness': 30}
    elif mat_type == 'Polymer':
        base = {'tensile': 50, 'density': 1.2, 'thermal': 0.2, 'cost': 10, 'hardness': 20}
        std = {'tensile': 20, 'density': 0.2, 'thermal': 0.05, 'cost': 2, 'hardness': 5}
    elif mat_type == 'Ceramic':
        base = {'tensile': 300, 'density': 3.5, 'thermal': 2, 'cost': 50, 'hardness': 800}
        std = {'tensile': 50, 'density': 0.3, 'thermal': 0.5, 'cost': 10, 'hardness': 100}
    else:  # Composite
        base = {'tensile': 800, 'density': 1.8, 'thermal': 5, 'cost': 100, 'hardness': 400}
        std = {'tensile': 150, 'density': 0.2, 'thermal': 2, 'cost': 20, 'hardness': 60}

    for _ in range(n_samples):
        materials.append({
            'Material_Type': mat_type,
            'Tensile_Strength_MPa': max(0, np.random.normal(base['tensile'], std['tensile'])),
            'Density_g_cm3': max(0, np.random.normal(base['density'], std['density'])),
            'Thermal_Conductivity': max(0, np.random.normal(base['thermal'], std['thermal'])),
            'Cost_USD_kg': max(0, np.random.normal(base['cost'], std['cost'])),
            'Hardness_HV': max(0, np.random.normal(base['hardness'], std['hardness']))
        })

df = pd.DataFrame(materials)

# === Plot 1: SPLOM - Scatterplot Matrix ===
dimensions = ['Tensile_Strength_MPa', 'Density_g_cm3', 'Thermal_Conductivity', 'Cost_USD_kg', 'Hardness_HV']

fig1 = go.Figure(data=go.Splom(
    dimensions=[dict(label=dim.replace('_', ' '), values=df[dim]) for dim in dimensions],
    text=df['Material_Type'],
    marker=dict(
        color=df['Material_Type'].astype('category').cat.codes,
        colorscale='Viridis',
        size=5,
        line=dict(width=0.5, color='white')
    ),
    diagonal=dict(visible=False),  # Remove diagonal
    showupperhalf=False,  # Only show lower triangle
))

# Update layout
fig1.update_layout(
    title={
        'text': "🔬 Material Properties - Correlation Matrix (SPLOM)",
        'x': 0.5,
        'xanchor': 'center'
    },
    height=700,
    width=900,
    hovermode='closest',
    dragmode='select'
)

register_plot(
    fig1,
    plot_id='material_splom',
    metadata={'title': 'Material Properties Correlation Matrix'}
)

# === Plot 2: Parallel Coordinates ===
# Normalize the data for better visualization
df_norm = df.copy()
for col in dimensions:
    df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

fig2 = go.Figure(data=go.Parcoords(
    line=dict(
        color=df['Material_Type'].astype('category').cat.codes,
        colorscale='Rainbow',
        showscale=True,
        cmin=0,
        cmax=3,
        colorbar=dict(
            title='Material Type',
            tickvals=[0, 1, 2, 3],
            ticktext=material_types,
            lenmode='fraction',
            len=0.5
        )
    ),
    dimensions=[
        dict(
            range=[0, 1],
            constraintrange=[0.3, 0.7],  # Add initial brush
            label='Tensile Strength',
            values=df_norm['Tensile_Strength_MPa'],
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=['Low', '', 'Med', '', 'High']
        ),
        dict(
            range=[0, 1],
            label='Density',
            values=df_norm['Density_g_cm3'],
            tickvals=[0, 0.5, 1],
            ticktext=['Light', 'Med', 'Heavy']
        ),
        dict(
            range=[0, 1],
            label='Thermal Cond.',
            values=df_norm['Thermal_Conductivity'],
            tickvals=[0, 0.5, 1],
            ticktext=['Poor', 'Med', 'Good']
        ),
        dict(
            range=[0, 1],
            label='Cost',
            values=df_norm['Cost_USD_kg'],
            tickvals=[0, 0.5, 1],
            ticktext=['Low', 'Med', 'High']
        ),
        dict(
            range=[0, 1],
            label='Hardness',
            values=df_norm['Hardness_HV'],
            tickvals=[0, 0.5, 1],
            ticktext=['Soft', 'Med', 'Hard']
        )
    ]
))

fig2.update_layout(
    title={
        'text': "🎯 Material Selection - Parallel Coordinates",
        'x': 0.5,
        'xanchor': 'center'
    },
    height=500,
    font=dict(size=11)
)

# Add explanation text
fig2.add_annotation(
    text="Drag on axes to filter materials",
    xref="paper", yref="paper",
    x=0.02, y=-0.1,
    showarrow=False,
    font=dict(size=10, color="gray")
)

register_plot(
    fig2,
    plot_id='material_pcp',
    metadata={'title': 'Material Properties Parallel Coordinates'}
)