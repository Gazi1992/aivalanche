"""
Statistical plots demonstration script
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from scipy import stats

def create_statistical_plots():
    """Create comprehensive statistical plot demonstrations"""
    plots = []

    # Generate sample data
    np.random.seed(42)

    # 1. Basic Box Plot
    data1 = [np.random.normal(100, 10, 200),
             np.random.normal(90, 20, 200),
             np.random.normal(95, 15, 200),
             np.random.normal(110, 25, 200)]

    fig1 = go.Figure()
    for i, d in enumerate(data1):
        fig1.add_trace(go.Box(y=d, name=f'Group {i+1}'))

    fig1.update_layout(
        title="1. Basic Box Plot - Group Comparisons",
        yaxis_title="Values",
        showlegend=False
    )
    plots.append(('stat_1', fig1, {
        'appearance': {
            'title': {'text': 'Basic Box Plot', 'fontSize': 20}
        }
    }))

    # 2. Horizontal Box Plot
    fig2 = go.Figure()
    for i, d in enumerate(data1):
        fig2.add_trace(go.Box(x=d, name=f'Category {i+1}'))

    fig2.update_layout(
        title="2. Horizontal Box Plot",
        xaxis_title="Values"
    )
    plots.append(('stat_2', fig2, {
        'appearance': {
            'title': {'text': 'Horizontal Box Plot', 'fontSize': 20}
        }
    }))

    # 3. Box Plot with Points
    fig3 = go.Figure()
    for i, d in enumerate(data1[:2]):
        fig3.add_trace(go.Box(
            y=d,
            name=f'Sample {i+1}',
            boxpoints='all',  # Show all points
            jitter=0.3,
            pointpos=-1.8,
            marker_color=['blue', 'red'][i]
        ))

    fig3.update_layout(
        title="3. Box Plot with All Points Shown",
        yaxis_title="Values"
    )
    plots.append(('stat_3', fig3, {
        'appearance': {
            'title': {'text': 'Box Plot with Points', 'fontSize': 20}
        }
    }))

    # 4. Violin Plot
    df_violin = pd.DataFrame({
        'Day': np.repeat(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], 100),
        'Sales': np.concatenate([
            np.random.normal(100, 15, 100),
            np.random.normal(110, 20, 100),
            np.random.normal(105, 15, 100),
            np.random.normal(120, 25, 100),
            np.random.normal(125, 20, 100)
        ])
    })

    fig4 = go.Figure()
    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
        fig4.add_trace(go.Violin(
            y=df_violin[df_violin['Day'] == day]['Sales'],
            name=day,
            box_visible=True,
            meanline_visible=True
        ))

    fig4.update_layout(
        title="4. Violin Plot - Distribution Shape",
        yaxis_title="Sales",
        xaxis_title="Day of Week"
    )
    plots.append(('stat_4', fig4, {
        'appearance': {
            'title': {'text': 'Violin Plot', 'fontSize': 20}
        }
    }))

    # 5. Split Violin Plot (for comparing two groups)
    df_split = pd.DataFrame({
        'Score': np.concatenate([
            np.random.normal(75, 10, 200),
            np.random.normal(85, 12, 200)
        ]),
        'Group': ['Control'] * 200 + ['Treatment'] * 200,
        'Category': np.tile(['A', 'B'], 200)
    })

    fig5 = go.Figure()

    fig5.add_trace(go.Violin(
        x=df_split['Category'][df_split['Group'] == 'Control'],
        y=df_split['Score'][df_split['Group'] == 'Control'],
        name='Control',
        side='negative',
        line_color='blue'
    ))

    fig5.add_trace(go.Violin(
        x=df_split['Category'][df_split['Group'] == 'Treatment'],
        y=df_split['Score'][df_split['Group'] == 'Treatment'],
        name='Treatment',
        side='positive',
        line_color='red'
    ))

    fig5.update_layout(
        title="5. Split Violin Plot - Group Comparison",
        yaxis_title="Score",
        violingap=0,
        violingroupgap=0,
        violinmode='overlay'
    )
    plots.append(('stat_5', fig5, {
        'appearance': {
            'title': {'text': 'Split Violin Plot', 'fontSize': 20}
        }
    }))

    # 6. Histogram with Normal Distribution Overlay
    data_hist = np.random.normal(100, 15, 1000)

    fig6 = go.Figure()
    fig6.add_trace(go.Histogram(
        x=data_hist,
        nbinsx=30,
        name='Data',
        opacity=0.7,
        marker_color='lightblue'
    ))

    # Add normal distribution curve
    x_range = np.linspace(min(data_hist), max(data_hist), 100)
    y_normal = stats.norm.pdf(x_range, np.mean(data_hist), np.std(data_hist)) * len(data_hist) * 5

    fig6.add_trace(go.Scatter(
        x=x_range,
        y=y_normal,
        mode='lines',
        name='Normal Fit',
        line=dict(color='red', width=2)
    ))

    fig6.update_layout(
        title="6. Histogram with Normal Distribution Overlay",
        xaxis_title="Value",
        yaxis_title="Frequency",
        bargap=0.1
    )
    plots.append(('stat_6', fig6, {
        'appearance': {
            'title': {'text': 'Histogram with Normal Fit', 'fontSize': 20}
        }
    }))

    # 7. Q-Q Plot
    theoretical_quantiles = np.random.normal(0, 1, 300)
    sample = np.random.normal(0.5, 1.5, 300)
    qq = stats.probplot(sample, dist="norm")

    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=qq[0][0],
        y=qq[0][1],
        mode='markers',
        name='Data',
        marker=dict(color='blue', size=5)
    ))

    # Add reference line
    fig7.add_trace(go.Scatter(
        x=[-3, 3],
        y=[-3, 3],
        mode='lines',
        name='Normal',
        line=dict(color='red', dash='dash')
    ))

    fig7.update_layout(
        title="7. Q-Q Plot - Normality Test",
        xaxis_title="Theoretical Quantiles",
        yaxis_title="Sample Quantiles"
    )
    plots.append(('stat_7', fig7, {
        'appearance': {
            'title': {'text': 'Q-Q Plot', 'fontSize': 20}
        }
    }))

    # 8. Distribution Plot (Distplot)
    fig8 = go.Figure()

    # Multiple distributions
    dist1 = np.random.normal(100, 10, 500)
    dist2 = np.random.gamma(2, 2, 500) * 20
    dist3 = np.random.exponential(20, 500) + 60

    for data, name, color in [(dist1, 'Normal', 'blue'),
                              (dist2, 'Gamma', 'red'),
                              (dist3, 'Exponential', 'green')]:
        # Create histogram
        hist, bins = np.histogram(data, bins=30, density=True)
        bin_centers = (bins[:-1] + bins[1:]) / 2

        fig8.add_trace(go.Scatter(
            x=bin_centers,
            y=hist,
            mode='lines',
            name=name,
            line=dict(color=color, width=2),
            fill='tozeroy',
            opacity=0.3
        ))

    fig8.update_layout(
        title="8. Distribution Comparison Plot",
        xaxis_title="Value",
        yaxis_title="Density"
    )
    plots.append(('stat_8', fig8, {
        'appearance': {
            'title': {'text': 'Distribution Plot', 'fontSize': 20}
        }
    }))

    # 9. Box Plot with Notches
    fig9 = go.Figure()
    for i in range(3):
        y_data = np.random.normal(100 + i*10, 15, 100)
        fig9.add_trace(go.Box(
            y=y_data,
            name=f'Dataset {i+1}',
            notched=True,  # Show notches
            marker_color=['#3498db', '#e74c3c', '#2ecc71'][i]
        ))

    fig9.update_layout(
        title="9. Notched Box Plot - Confidence Intervals",
        yaxis_title="Values"
    )
    plots.append(('stat_9', fig9, {
        'appearance': {
            'title': {'text': 'Notched Box Plot', 'fontSize': 20}
        }
    }))

    # 10. Grouped Box Plot
    df_grouped = pd.DataFrame({
        'Method': np.repeat(['Method A', 'Method B', 'Method C'], 300),
        'Site': np.tile(np.repeat(['Site 1', 'Site 2', 'Site 3'], 100), 3),
        'Yield': np.concatenate([
            np.random.normal(100, 10, 100), np.random.normal(105, 12, 100), np.random.normal(95, 8, 100),
            np.random.normal(110, 15, 100), np.random.normal(115, 10, 100), np.random.normal(105, 12, 100),
            np.random.normal(90, 12, 100), np.random.normal(95, 15, 100), np.random.normal(85, 10, 100)
        ])
    })

    fig10 = px.box(df_grouped, x='Site', y='Yield', color='Method',
                   title="10. Grouped Box Plot - Multi-factor Analysis")
    plots.append(('stat_10', fig10, {
        'appearance': {
            'title': {'text': 'Grouped Box Plot', 'fontSize': 20}
        }
    }))

    # 11. Ridgeline Plot
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']

    fig11 = go.Figure()

    for i, cat in enumerate(categories):
        data = np.random.normal(100 + i*5, 10 + i*2, 200)

        # Create violin for ridgeline effect
        fig11.add_trace(go.Violin(
            x=data,
            y=[i] * len(data),
            name=cat,
            orientation='h',
            side='positive',
            width=0.7,
            points=False,
            line_color=['#667eea', '#764ba2', '#f093fb', '#fccb90', '#c3f0ca'][i]
        ))

    fig11.update_layout(
        title="11. Ridgeline Plot - Distribution by Category",
        xaxis_title="Value",
        yaxis=dict(
            ticktext=categories,
            tickvals=list(range(len(categories)))
        ),
        showlegend=False
    )
    plots.append(('stat_11', fig11, {
        'appearance': {
            'title': {'text': 'Ridgeline Plot', 'fontSize': 20}
        }
    }))

    # 12. Error Bars Plot
    x_error = np.arange(1, 11)
    y_error = np.random.randint(50, 100, 10)
    error_vals = np.random.randint(5, 15, 10)

    fig12 = go.Figure()
    fig12.add_trace(go.Scatter(
        x=x_error,
        y=y_error,
        mode='lines+markers',
        error_y=dict(
            type='data',
            array=error_vals,
            visible=True
        ),
        marker=dict(size=8, color='blue'),
        line=dict(width=2)
    ))

    fig12.update_layout(
        title="12. Line Plot with Error Bars",
        xaxis_title="Measurement",
        yaxis_title="Value"
    )
    plots.append(('stat_12', fig12, {
        'appearance': {
            'title': {'text': 'Error Bars Plot', 'fontSize': 20}
        }
    }))

    # 13. Strip Plot (Dot Plot)
    df_strip = pd.DataFrame({
        'Treatment': np.repeat(['Control', 'Drug A', 'Drug B', 'Drug C'], 50),
        'Response': np.concatenate([
            np.random.normal(50, 10, 50),
            np.random.normal(60, 12, 50),
            np.random.normal(65, 15, 50),
            np.random.normal(55, 8, 50)
        ])
    })

    fig13 = px.strip(df_strip, x='Treatment', y='Response',
                     title="13. Strip Plot - Individual Data Points",
                     color='Treatment')
    fig13.update_traces(jitter=1)
    plots.append(('stat_13', fig13, {
        'appearance': {
            'title': {'text': 'Strip Plot', 'fontSize': 20}
        }
    }))

    # 14. Cumulative Distribution Function (CDF)
    data_cdf = np.random.normal(100, 15, 1000)
    sorted_data = np.sort(data_cdf)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

    fig14 = go.Figure()
    fig14.add_trace(go.Scatter(
        x=sorted_data,
        y=cdf,
        mode='lines',
        name='Empirical CDF',
        line=dict(color='blue', width=2)
    ))

    # Add theoretical CDF
    x_theoretical = np.linspace(min(data_cdf), max(data_cdf), 100)
    y_theoretical = stats.norm.cdf(x_theoretical, np.mean(data_cdf), np.std(data_cdf))

    fig14.add_trace(go.Scatter(
        x=x_theoretical,
        y=y_theoretical,
        mode='lines',
        name='Theoretical CDF',
        line=dict(color='red', dash='dash', width=2)
    ))

    fig14.update_layout(
        title="14. Cumulative Distribution Function",
        xaxis_title="Value",
        yaxis_title="Cumulative Probability"
    )
    plots.append(('stat_14', fig14, {
        'appearance': {
            'title': {'text': 'CDF Plot', 'fontSize': 20}
        }
    }))

    # 15. Beeswarm Plot
    np.random.seed(42)
    n_points = 150
    groups = np.repeat(['A', 'B', 'C'], n_points)
    values = np.concatenate([
        np.random.normal(100, 10, n_points),
        np.random.normal(110, 15, n_points),
        np.random.normal(95, 12, n_points)
    ])

    # Add jitter for beeswarm effect
    group_nums = pd.Categorical(groups).codes
    x_positions = group_nums + np.random.uniform(-0.2, 0.2, len(groups))

    fig15 = go.Figure()
    for i, group in enumerate(['A', 'B', 'C']):
        mask = groups == group
        fig15.add_trace(go.Scatter(
            x=x_positions[mask],
            y=values[mask],
            mode='markers',
            name=f'Group {group}',
            marker=dict(size=6, opacity=0.6)
        ))

    fig15.update_layout(
        title="15. Beeswarm Plot - Dense Data Points",
        xaxis=dict(
            ticktext=['A', 'B', 'C'],
            tickvals=[0, 1, 2],
            title="Group"
        ),
        yaxis_title="Value"
    )
    plots.append(('stat_15', fig15, {
        'appearance': {
            'title': {'text': 'Beeswarm Plot', 'fontSize': 20}
        }
    }))

    # 16. Kernel Density Estimation
    data_kde = np.random.normal(100, 15, 200)

    # Calculate KDE
    kde = stats.gaussian_kde(data_kde)
    x_kde = np.linspace(data_kde.min(), data_kde.max(), 100)
    y_kde = kde(x_kde)

    fig16 = go.Figure()

    # Add histogram
    fig16.add_trace(go.Histogram(
        x=data_kde,
        nbinsx=20,
        name='Histogram',
        opacity=0.5,
        yaxis='y2'
    ))

    # Add KDE
    fig16.add_trace(go.Scatter(
        x=x_kde,
        y=y_kde,
        mode='lines',
        name='KDE',
        line=dict(color='red', width=2)
    ))

    fig16.update_layout(
        title="16. Kernel Density Estimation",
        xaxis_title="Value",
        yaxis_title="Density",
        yaxis2=dict(
            overlaying='y',
            side='right',
            title='Frequency'
        )
    )
    plots.append(('stat_16', fig16, {
        'appearance': {
            'title': {'text': 'KDE Plot', 'fontSize': 20}
        }
    }))

    # 17. Raincloud Plot (Combination)
    fig17 = go.Figure()

    for i, group in enumerate(['Control', 'Treatment']):
        data = np.random.normal(100 + i*20, 15, 100)

        # Add violin (half)
        fig17.add_trace(go.Violin(
            y=data,
            x=[group] * len(data),
            name=group,
            side='negative',
            line_color=['blue', 'red'][i],
            meanline_visible=True,
            width=0.5
        ))

        # Add strip plot
        # Simply use the group name without jitter for now
        fig17.add_trace(go.Scatter(
            x=[group] * len(data),
            y=data,
            mode='markers',
            name=f'{group} points',
            marker=dict(size=4, opacity=0.5, color=['blue', 'red'][i]),
            showlegend=False
        ))

    fig17.update_layout(
        title="17. Raincloud Plot - Combined Visualization",
        xaxis_title="Group",
        yaxis_title="Value",
        violingap=0
    )
    plots.append(('stat_17', fig17, {
        'appearance': {
            'title': {'text': 'Raincloud Plot', 'fontSize': 20}
        }
    }))

    # 18. Statistical Summary Plot
    categories_summary = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023']
    means = [100, 110, 108, 115]
    stds = [10, 12, 11, 13]

    fig18 = go.Figure()

    # Add mean line
    fig18.add_trace(go.Scatter(
        x=categories_summary,
        y=means,
        mode='lines+markers',
        name='Mean',
        error_y=dict(type='data', array=stds, visible=True),
        marker=dict(size=10, color='blue'),
        line=dict(width=2)
    ))

    # Add confidence interval
    upper = [m + 1.96*s for m, s in zip(means, stds)]
    lower = [m - 1.96*s for m, s in zip(means, stds)]

    fig18.add_trace(go.Scatter(
        x=categories_summary + categories_summary[::-1],
        y=upper + lower[::-1],
        fill='toself',
        fillcolor='rgba(0,100,255,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        name='95% CI'
    ))

    fig18.update_layout(
        title="18. Statistical Summary with Confidence Intervals",
        xaxis_title="Quarter",
        yaxis_title="Revenue (M$)"
    )
    plots.append(('stat_18', fig18, {
        'appearance': {
            'title': {'text': 'Statistical Summary', 'fontSize': 20}
        }
    }))

    # 19. Correlogram
    # Generate correlated data
    n_vars = 6
    n_obs = 100
    cov_matrix = np.random.rand(n_vars, n_vars)
    cov_matrix = (cov_matrix + cov_matrix.T) / 2  # Make symmetric
    np.fill_diagonal(cov_matrix, 1)  # Set diagonal to 1

    data_corr = np.random.multivariate_normal(np.zeros(n_vars), cov_matrix, n_obs)
    df_corr = pd.DataFrame(data_corr, columns=[f'Var{i+1}' for i in range(n_vars)])

    correlation_matrix = df_corr.corr()

    fig19 = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(correlation_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))

    fig19.update_layout(
        title="19. Correlogram - Variable Relationships",
        xaxis_title="Variables",
        yaxis_title="Variables"
    )
    plots.append(('stat_19', fig19, {
        'appearance': {
            'title': {'text': 'Correlogram', 'fontSize': 20}
        }
    }))

    # 20. Population Pyramid
    age_groups = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81+']
    male_population = [15, 20, 25, 22, 18, 15, 12, 8, 4]
    female_population = [14, 19, 24, 23, 19, 16, 14, 10, 6]

    fig20 = go.Figure()

    fig20.add_trace(go.Bar(
        y=age_groups,
        x=[-m for m in male_population],  # Negative for left side
        name='Male',
        orientation='h',
        marker=dict(color='lightblue')
    ))

    fig20.add_trace(go.Bar(
        y=age_groups,
        x=female_population,
        name='Female',
        orientation='h',
        marker=dict(color='pink')
    ))

    fig20.update_layout(
        title="20. Population Pyramid",
        xaxis_title="Population (millions)",
        yaxis_title="Age Group",
        barmode='relative',
        bargap=0.1,
        xaxis=dict(
            tickvals=[-20, -10, 0, 10, 20],
            ticktext=['20', '10', '0', '10', '20']
        )
    )
    plots.append(('stat_20', fig20, {
        'appearance': {
            'title': {'text': 'Population Pyramid', 'fontSize': 20}
        }
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} statistical plot demonstrations"

# Execute when module is run
if __name__ == "__main__" or True:  # Always execute when imported
    result = create_statistical_plots()
    print(result)