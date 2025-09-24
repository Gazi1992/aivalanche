"""
Scientific Research Demo
Real-world scientific examples including experimental data, statistical analysis, and modeling
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy import stats

def create_scientific_plots():
    """Create scientific research visualizations"""
    plots = []

    # 1. Experimental Results Scatter with Error Bars
    # Simulating dose-response experiment
    doses = np.array([0, 0.1, 0.5, 1, 2.5, 5, 10, 20])
    response_mean = 100 / (1 + np.exp(-2*(doses - 5)))  # Sigmoid curve
    response_std = np.array([2, 3, 4, 5, 6, 5, 4, 3])

    # Individual data points
    n_replicates = 5
    individual_doses = np.repeat(doses, n_replicates)
    individual_responses = []
    for i, dose in enumerate(doses):
        individual_responses.extend(
            np.random.normal(response_mean[i], response_std[i], n_replicates)
        )

    fig1 = go.Figure()

    # Individual data points
    fig1.add_trace(go.Scatter(
        x=individual_doses,
        y=individual_responses,
        mode='markers',
        name='Individual measurements',
        marker=dict(size=8, color='lightblue', symbol='circle-open')
    ))

    # Mean with error bars
    fig1.add_trace(go.Scatter(
        x=doses,
        y=response_mean,
        mode='lines+markers',
        name='Mean ± SEM',
        error_y=dict(
            type='data',
            array=response_std / np.sqrt(n_replicates),
            visible=True
        ),
        marker=dict(size=10, color='darkblue'),
        line=dict(color='darkblue', width=2)
    ))

    fig1.update_layout(
        title="Dose-Response Curve with Replicates",
        xaxis_title="Concentration (μM)",
        yaxis_title="Response (%)",
        hovermode='x unified'
    )
    plots.append(('sci_dose_response', fig1, {
        'appearance': {'title': {'text': 'Dose-Response Analysis'}}
    }))

    # 2. Distribution Comparison - Box & Violin Plots
    # Simulating gene expression data
    np.random.seed(42)
    control = np.random.normal(100, 15, 50)
    treatment_a = np.random.normal(120, 20, 50)
    treatment_b = np.random.normal(140, 25, 50)
    treatment_c = np.random.normal(110, 18, 50)

    fig2 = go.Figure()

    # Box plots
    fig2.add_trace(go.Box(
        y=control, name='Control',
        boxpoints='outliers',
        marker_color='lightgray',
        boxmean='sd'
    ))
    fig2.add_trace(go.Box(
        y=treatment_a, name='Treatment A',
        boxpoints='outliers',
        marker_color='lightblue',
        boxmean='sd'
    ))
    fig2.add_trace(go.Box(
        y=treatment_b, name='Treatment B',
        boxpoints='outliers',
        marker_color='lightgreen',
        boxmean='sd'
    ))
    fig2.add_trace(go.Box(
        y=treatment_c, name='Treatment C',
        boxpoints='outliers',
        marker_color='lightcoral',
        boxmean='sd'
    ))

    fig2.update_layout(
        title="Gene Expression Levels Across Treatments",
        yaxis_title="Expression Level (FPKM)",
        showlegend=False
    )
    plots.append(('sci_gene_expression', fig2, {
        'appearance': {'title': {'text': 'Expression Analysis'}}
    }))

    # 3. Correlation Matrix Heatmap
    # Simulating metabolomics data
    metabolites = ['Glucose', 'Lactate', 'Pyruvate', 'ATP', 'NADH',
                   'Glutamine', 'Citrate', 'Succinate']
    n_samples = 100
    # Create correlated data
    base_data = np.random.randn(n_samples, len(metabolites))
    # Add correlations
    base_data[:, 1] = base_data[:, 0] * 0.8 + np.random.randn(n_samples) * 0.5  # Lactate ~ Glucose
    base_data[:, 2] = base_data[:, 1] * 0.7 + np.random.randn(n_samples) * 0.5  # Pyruvate ~ Lactate
    base_data[:, 3] = -base_data[:, 0] * 0.6 + np.random.randn(n_samples) * 0.5  # ATP ~ -Glucose
    base_data[:, 4] = base_data[:, 3] * 0.5 + np.random.randn(n_samples) * 0.5  # NADH ~ ATP

    corr_matrix = np.corrcoef(base_data.T)

    fig3 = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=metabolites,
        y=metabolites,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Pearson r")
    ))

    fig3.update_layout(
        title="Metabolite Correlation Matrix",
        xaxis_title="Metabolites",
        yaxis_title="Metabolites"
    )
    plots.append(('sci_correlation', fig3, {
        'appearance': {'title': {'text': 'Metabolite Correlations'}}
    }))

    # 4. Histogram with Distribution Fit
    # Simulating particle size distribution
    particle_sizes = np.random.lognormal(3, 0.5, 1000)

    fig4 = go.Figure()

    # Histogram
    fig4.add_trace(go.Histogram(
        x=particle_sizes,
        nbinsx=30,
        name='Measured',
        marker_color='lightblue',
        opacity=0.7,
        histnorm='probability density'
    ))

    # Fitted distribution
    x_range = np.linspace(particle_sizes.min(), particle_sizes.max(), 100)
    fitted_params = stats.lognorm.fit(particle_sizes)
    fitted_pdf = stats.lognorm.pdf(x_range, *fitted_params)

    fig4.add_trace(go.Scatter(
        x=x_range,
        y=fitted_pdf,
        mode='lines',
        name='Log-normal fit',
        line=dict(color='red', width=2)
    ))

    fig4.update_layout(
        title="Particle Size Distribution",
        xaxis_title="Particle Diameter (nm)",
        yaxis_title="Probability Density",
        barmode='overlay'
    )
    plots.append(('sci_particle_dist', fig4, {
        'appearance': {'title': {'text': 'Size Distribution'}}
    }))

    # 5. 3D Surface - Reaction Kinetics
    # Michaelis-Menten kinetics with competitive inhibition
    substrate = np.linspace(0.1, 10, 50)
    inhibitor = np.linspace(0, 5, 50)
    S, I = np.meshgrid(substrate, inhibitor)

    Vmax = 100
    Km = 2
    Ki = 1
    V = (Vmax * S) / (Km * (1 + I/Ki) + S)

    fig5 = go.Figure(data=[go.Surface(
        z=V,
        x=S,
        y=I,
        colorscale='Viridis',
        colorbar=dict(title="Reaction Rate")
    )])

    fig5.update_layout(
        title="Enzyme Kinetics - Competitive Inhibition",
        scene=dict(
            xaxis_title="[Substrate] (mM)",
            yaxis_title="[Inhibitor] (mM)",
            zaxis_title="Rate (μmol/min)"
        )
    )
    plots.append(('sci_kinetics_3d', fig5, {
        'appearance': {'title': {'text': 'Enzyme Kinetics'}}
    }))

    # 6. Parallel Coordinates - Multi-parameter Analysis
    # Simulating cell phenotype data
    n_cells = 100
    cell_data = pd.DataFrame({
        'Cell_Type': np.random.choice(['Type A', 'Type B', 'Type C'], n_cells),
        'Size': np.random.normal(10, 2, n_cells),
        'Granularity': np.random.normal(50, 10, n_cells),
        'Marker_1': np.random.normal(100, 20, n_cells),
        'Marker_2': np.random.normal(80, 15, n_cells),
        'Marker_3': np.random.normal(60, 25, n_cells)
    })

    # Color by cell type
    color_map = {'Type A': 0, 'Type B': 1, 'Type C': 2}
    cell_data['Color'] = cell_data['Cell_Type'].map(color_map)

    dimensions = []
    for col in ['Size', 'Granularity', 'Marker_1', 'Marker_2', 'Marker_3']:
        dimensions.append(dict(
            label=col,
            values=cell_data[col],
            range=[cell_data[col].min(), cell_data[col].max()]
        ))

    fig6 = go.Figure(data=go.Parcoords(
        dimensions=dimensions,
        line=dict(
            color=cell_data['Color'],
            colorscale='Viridis',
            showscale=True,
            cmin=0,
            cmax=2
        )
    ))

    fig6.update_layout(
        title="Cell Phenotype Multi-parameter Analysis"
    )
    plots.append(('sci_multiparameter', fig6, {
        'appearance': {'title': {'text': 'Multi-parameter Analysis'}}
    }))

    # 7. Contour Plot - 2D Density
    # Simulating protein-protein interaction strength
    x = np.linspace(-3, 3, 100)
    y = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x, y)

    # Multiple binding sites
    Z1 = np.exp(-((X - 1)**2 + (Y - 1)**2))
    Z2 = np.exp(-((X + 1)**2 + (Y + 1)**2))
    Z3 = 0.5 * np.exp(-((X - 0.5)**2 + (Y + 1.5)**2))
    Z = Z1 + Z2 + Z3

    fig7 = go.Figure(data=go.Contour(
        z=Z,
        x=x,
        y=y,
        colorscale='Hot',
        contours=dict(
            start=0,
            end=1,
            size=0.1,
            showlabels=True,
            labelfont=dict(size=10, color='white')
        ),
        colorbar=dict(title="Binding Affinity")
    ))

    fig7.update_layout(
        title="Protein Binding Site Analysis",
        xaxis_title="Position X (Å)",
        yaxis_title="Position Y (Å)"
    )
    plots.append(('sci_binding_sites', fig7, {
        'appearance': {'title': {'text': 'Binding Analysis'}}
    }))

    # 8. Violin Plot - Statistical Comparison
    # Simulating clinical trial results
    placebo = np.concatenate([
        np.random.normal(100, 10, 30),  # Non-responders
        np.random.normal(102, 12, 20)   # Mild responders
    ])

    drug_low = np.concatenate([
        np.random.normal(100, 10, 10),  # Non-responders
        np.random.normal(115, 8, 40)    # Responders
    ])

    drug_high = np.concatenate([
        np.random.normal(100, 10, 5),   # Non-responders
        np.random.normal(125, 10, 45)   # Strong responders
    ])

    fig8 = go.Figure()

    fig8.add_trace(go.Violin(
        y=placebo,
        name='Placebo',
        box_visible=True,
        meanline_visible=True,
        fillcolor='lightgray',
        opacity=0.6
    ))

    fig8.add_trace(go.Violin(
        y=drug_low,
        name='Low Dose',
        box_visible=True,
        meanline_visible=True,
        fillcolor='lightblue',
        opacity=0.6
    ))

    fig8.add_trace(go.Violin(
        y=drug_high,
        name='High Dose',
        box_visible=True,
        meanline_visible=True,
        fillcolor='lightgreen',
        opacity=0.6
    ))

    fig8.update_layout(
        title="Clinical Trial - Treatment Response Distribution",
        yaxis_title="Biomarker Level",
        violingap=0.3,
        violinmode='group'
    )
    plots.append(('sci_clinical_trial', fig8, {
        'appearance': {'title': {'text': 'Clinical Trial Results'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} scientific research visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_scientific_plots()
    print(result)