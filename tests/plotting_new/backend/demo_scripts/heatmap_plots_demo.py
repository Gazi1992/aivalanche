"""
Heatmap and 2D density plots demonstration script
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from scipy import stats

def create_heatmap_plots():
    """Create comprehensive heatmap and 2D density plot demonstrations"""
    plots = []

    # 1. Basic Heatmap
    z_basic = [[1, 20, 30, 50, 1],
               [20, 1, 60, 80, 30],
               [30, 60, 1, -10, 20],
               [50, 80, -10, 1, 40],
               [1, 30, 20, 40, 1]]

    x_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    y_labels = ['Morning', 'Noon', 'Afternoon', 'Evening', 'Night']

    fig1 = go.Figure(data=go.Heatmap(
        z=z_basic,
        x=x_labels,
        y=y_labels,
        colorscale='Viridis',
        text=z_basic,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    fig1.update_layout(
        title="Basic Heatmap - Weekly Activity Pattern",
        xaxis_title="Day of Week",
        yaxis_title="Time of Day"
    )
    plots.append(('heatmap_1', fig1, {
        'appearance': {
            'title': {'text': 'Basic Heatmap', 'fontSize': 20}
        }
    }))

    # 2. Correlation Matrix Heatmap
    np.random.seed(42)
    df_corr = pd.DataFrame(np.random.randn(100, 6),
                           columns=['Var1', 'Var2', 'Var3', 'Var4', 'Var5', 'Var6'])
    df_corr['Var2'] = df_corr['Var1'] * 0.5 + np.random.randn(100) * 0.2
    df_corr['Var3'] = -df_corr['Var1'] * 0.7 + np.random.randn(100) * 0.3
    correlation_matrix = df_corr.corr()

    fig2 = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(correlation_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    fig2.update_layout(
        title="Correlation Matrix Heatmap",
        xaxis_title="Variables",
        yaxis_title="Variables"
    )
    plots.append(('heatmap_2', fig2, {
        'appearance': {
            'title': {'text': 'Correlation Matrix', 'fontSize': 20}
        }
    }))

    # 3. 2D Density Contour Plot
    np.random.seed(42)
    x_density = np.random.normal(2, 1, 500)
    y_density = np.random.normal(2, 1, 500)

    fig3 = go.Figure(go.Histogram2dContour(
        x=x_density,
        y=y_density,
        colorscale='Blues',
        reversescale=False,
        xaxis='x',
        yaxis='y'
    ))
    fig3.update_layout(
        title="2D Density Contour Plot",
        xaxis_title="X Variable",
        yaxis_title="Y Variable"
    )
    plots.append(('heatmap_3', fig3, {
        'appearance': {
            'title': {'text': '2D Density Contour', 'fontSize': 20}
        }
    }))

    # 4. 2D Histogram (Density Heatmap)
    fig4 = go.Figure(go.Histogram2d(
        x=x_density,
        y=y_density,
        nbinsx=30,
        nbinsy=30,
        colorscale='Hot',
        colorbar=dict(title="Count")
    ))
    fig4.update_layout(
        title="2D Histogram - Density Heatmap",
        xaxis_title="X Variable",
        yaxis_title="Y Variable"
    )
    plots.append(('heatmap_4', fig4, {
        'appearance': {
            'title': {'text': '2D Histogram', 'fontSize': 20}
        }
    }))

    # 5. Annotated Heatmap
    z_annotated = [[.1, .3, .5, .7, .9],
                   [1, .8, .6, .4, .2],
                   [.2, 0, .5, .7, .9],
                   [.9, .8, .4, .2, 0],
                   [.3, .4, .5, .6, .7]]

    fig5 = go.Figure(data=go.Heatmap(
        z=z_annotated,
        text=[[f'{val:.1%}' for val in row] for row in z_annotated],
        texttemplate="%{text}",
        textfont={"size": 12},
        colorscale='Greens',
        showscale=True,
        colorbar=dict(title="Percentage", tickformat='.0%')
    ))
    fig5.update_layout(
        title="Annotated Heatmap - Performance Metrics",
        xaxis_title="Metrics",
        yaxis_title="Categories",
        xaxis=dict(tickmode='array', tickvals=list(range(5)),
                   ticktext=['Metric A', 'Metric B', 'Metric C', 'Metric D', 'Metric E']),
        yaxis=dict(tickmode='array', tickvals=list(range(5)),
                   ticktext=['Cat 1', 'Cat 2', 'Cat 3', 'Cat 4', 'Cat 5'])
    )
    plots.append(('heatmap_5', fig5, {
        'appearance': {
            'title': {'text': 'Annotated Heatmap', 'fontSize': 20}
        }
    }))

    # 6. Calendar Heatmap
    import datetime
    base = datetime.datetime(2023, 1, 1)
    dates = [base + datetime.timedelta(days=x) for x in range(365)]
    values = np.random.randint(0, 100, 365)

    # Create a matrix for calendar view (7 days x 52 weeks)
    calendar_data = np.zeros((7, 53))
    for i, date in enumerate(dates):
        week = date.isocalendar()[1] - 1
        day = date.weekday()
        if week < 53:
            calendar_data[day, week] = values[i]

    fig6 = go.Figure(data=go.Heatmap(
        z=calendar_data,
        colorscale='YlOrRd',
        showscale=True,
        colorbar=dict(title="Activity"),
        hoverongaps=False
    ))
    fig6.update_layout(
        title="Calendar Heatmap - 2023 Daily Activity",
        xaxis_title="Week of Year",
        yaxis_title="Day of Week",
        yaxis=dict(tickmode='array', tickvals=list(range(7)),
                   ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    )
    plots.append(('heatmap_6', fig6, {
        'appearance': {
            'title': {'text': 'Calendar Heatmap', 'fontSize': 20}
        }
    }))

    # 7. Diverging Heatmap
    z_diverging = np.random.randn(20, 20)

    fig7 = go.Figure(data=go.Heatmap(
        z=z_diverging,
        colorscale='RdYlBu',
        zmid=0,
        colorbar=dict(title="Deviation")
    ))
    fig7.update_layout(
        title="Diverging Heatmap - Deviation from Mean",
        xaxis_title="Sample",
        yaxis_title="Feature"
    )
    plots.append(('heatmap_7', fig7, {
        'appearance': {
            'title': {'text': 'Diverging Heatmap', 'fontSize': 20}
        }
    }))

    # 8. Clustered Heatmap with Dendrograms
    # Simulate clustered data
    np.random.seed(42)
    n_samples = 30
    n_features = 20
    data_clustered = np.zeros((n_samples, n_features))

    # Create 3 clusters
    for i in range(10):
        data_clustered[i, :5] = np.random.randn(5) + 2
        data_clustered[i+10, 5:10] = np.random.randn(5) + 2
        data_clustered[i+20, 10:15] = np.random.randn(5) + 2

    data_clustered += np.random.randn(n_samples, n_features) * 0.5

    fig8 = go.Figure(data=go.Heatmap(
        z=data_clustered,
        colorscale='Spectral',
        colorbar=dict(title="Value")
    ))
    fig8.update_layout(
        title="Clustered Heatmap - Gene Expression Data",
        xaxis_title="Genes",
        yaxis_title="Samples"
    )
    plots.append(('heatmap_8', fig8, {
        'appearance': {
            'title': {'text': 'Clustered Heatmap', 'fontSize': 20}
        }
    }))

    # 9. Contour Plot
    x_contour = np.linspace(-3, 3, 100)
    y_contour = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x_contour, y_contour)
    Z = np.sin(np.sqrt(X**2 + Y**2))

    fig9 = go.Figure(data=go.Contour(
        x=x_contour,
        y=y_contour,
        z=Z,
        colorscale='Jet',
        contours=dict(
            coloring='heatmap',
            showlabels=True,
            labelfont=dict(size=12, color='white')
        )
    ))
    fig9.update_layout(
        title="Contour Plot - 2D Function Visualization",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(('heatmap_9', fig9, {
        'appearance': {
            'title': {'text': 'Contour Plot', 'fontSize': 20}
        }
    }))

    # 10. Filled Contour Plot
    fig10 = go.Figure(data=go.Contour(
        x=x_contour,
        y=y_contour,
        z=Z,
        colorscale='Earth',
        contours_coloring='fill',
        line_smoothing=0.85,
        contours=dict(
            showlabels=True,
            labelfont=dict(size=12)
        )
    ))
    fig10.update_layout(
        title="Filled Contour Plot - Topographic Map Style",
        xaxis_title="Longitude",
        yaxis_title="Latitude"
    )
    plots.append(('heatmap_10', fig10, {
        'appearance': {
            'title': {'text': 'Filled Contour Plot', 'fontSize': 20}
        }
    }))

    # 11. Time Series Heatmap
    hours = list(range(24))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    z_time = np.random.randint(10, 100, size=(7, 24))

    fig11 = go.Figure(data=go.Heatmap(
        z=z_time,
        x=hours,
        y=days,
        colorscale='Plasma',
        colorbar=dict(title="Traffic")
    ))
    fig11.update_layout(
        title="Time Series Heatmap - Weekly Traffic Pattern",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week"
    )
    plots.append(('heatmap_11', fig11, {
        'appearance': {
            'title': {'text': 'Time Series Heatmap', 'fontSize': 20}
        }
    }))

    # 12. Hexbin Plot
    np.random.seed(42)
    x_hex = np.random.randn(5000)
    y_hex = np.random.randn(5000)

    fig12 = go.Figure(go.Histogram2d(
        x=x_hex,
        y=y_hex,
        nbinsx=40,
        nbinsy=40,
        colorscale='YlOrRd',
        colorbar=dict(title="Density")
    ))
    fig12.update_layout(
        title="Hexbin Plot - Density Distribution",
        xaxis_title="X Variable",
        yaxis_title="Y Variable"
    )
    plots.append(('heatmap_12', fig12, {
        'appearance': {
            'title': {'text': 'Hexbin Density Plot', 'fontSize': 20}
        }
    }))

    # 13. Confusion Matrix
    actual = ['A', 'B', 'C', 'D', 'E']
    predicted = ['A', 'B', 'C', 'D', 'E']
    confusion = [[85, 5, 3, 4, 3],
                 [2, 88, 5, 3, 2],
                 [1, 4, 90, 3, 2],
                 [2, 2, 3, 89, 4],
                 [3, 2, 1, 4, 90]]

    fig13 = go.Figure(data=go.Heatmap(
        z=confusion,
        x=predicted,
        y=actual,
        colorscale='Blues',
        text=confusion,
        texttemplate="%{text}",
        textfont={"size": 14},
        colorbar=dict(title="Count")
    ))
    fig13.update_layout(
        title="Confusion Matrix - Classification Results",
        xaxis_title="Predicted Class",
        yaxis_title="Actual Class"
    )
    plots.append(('heatmap_13', fig13, {
        'appearance': {
            'title': {'text': 'Confusion Matrix', 'fontSize': 20}
        }
    }))

    # 14. Geographic Heatmap
    # Simulate temperature data for US states
    states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    temp_data = np.random.randint(20, 100, size=(len(states), len(months)))

    fig14 = go.Figure(data=go.Heatmap(
        z=temp_data,
        x=months,
        y=states,
        colorscale='Turbo',
        colorbar=dict(title="Temperature (°F)")
    ))
    fig14.update_layout(
        title="Geographic Heatmap - Monthly Temperature by State",
        xaxis_title="Month",
        yaxis_title="State"
    )
    plots.append(('heatmap_14', fig14, {
        'appearance': {
            'title': {'text': 'Geographic Heatmap', 'fontSize': 20}
        }
    }))

    # 15. Treemap
    labels = ["Total", "North", "NE", "NY", "MA", "CT", "South", "FL", "GA", "TX",
              "West", "CA", "WA", "OR", "Central", "IL", "OH", "MI"]
    parents = ["", "Total", "North", "NE", "NE", "NE", "Total", "South", "South", "South",
               "Total", "West", "West", "West", "Total", "Central", "Central", "Central"]
    values = [0, 0, 0, 10, 15, 8, 0, 20, 12, 25, 0, 30, 18, 10, 0, 15, 12, 8]

    fig15 = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value",
        marker=dict(colorscale='Rainbow')
    ))
    fig15.update_layout(
        title="Treemap - Regional Sales Distribution",
        margin=dict(t=50, l=25, r=25, b=25)
    )
    plots.append(('heatmap_15', fig15, {
        'appearance': {
            'title': {'text': 'Treemap Visualization', 'fontSize': 20}
        }
    }))

    # 16. Sunburst Chart
    fig16 = go.Figure(go.Sunburst(
        labels=["Total", "Q1", "Q2", "Q3", "Q4",
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        parents=["", "Total", "Total", "Total", "Total",
                 "Q1", "Q1", "Q1", "Q2", "Q2", "Q2",
                 "Q3", "Q3", "Q3", "Q4", "Q4", "Q4"],
        values=[0, 0, 0, 0, 0,
                10, 15, 12, 18, 20, 16,
                22, 25, 20, 18, 15, 12],
        marker=dict(colorscale='Sunset')
    ))
    fig16.update_layout(
        title="Sunburst Chart - Quarterly & Monthly Breakdown",
        margin=dict(t=50, l=0, r=0, b=0)
    )
    plots.append(('heatmap_16', fig16, {
        'appearance': {
            'title': {'text': 'Sunburst Chart', 'fontSize': 20}
        }
    }))

    # 17. Matrix Plot with Gaps
    z_gaps = np.random.randn(20, 20)
    # Add some gaps (NaN values)
    mask = np.random.random((20, 20)) < 0.1
    z_gaps[mask] = np.nan

    fig17 = go.Figure(data=go.Heatmap(
        z=z_gaps,
        colorscale='Viridis',
        hoverongaps=False,
        connectgaps=False,
        colorbar=dict(title="Value")
    ))
    fig17.update_layout(
        title="Matrix Plot with Missing Data",
        xaxis_title="Column",
        yaxis_title="Row"
    )
    plots.append(('heatmap_17', fig17, {
        'appearance': {
            'title': {'text': 'Matrix with Gaps', 'fontSize': 20}
        }
    }))

    # 18. Radial Heatmap
    theta = np.linspace(0, 360, 37)
    r = np.linspace(0, 10, 11)
    theta_grid, r_grid = np.meshgrid(theta, r)
    z_radial = r_grid * np.sin(theta_grid * np.pi / 180)

    fig18 = go.Figure(go.Barpolar(
        r=r.flatten(),
        theta=theta.flatten(),
        marker_color=z_radial.flatten(),
        marker=dict(
            colorscale='HSV',
            showscale=True,
            colorbar=dict(title="Value")
        )
    ))
    fig18.update_layout(
        title="Radial Heatmap - Polar Coordinate Data",
        polar=dict(
            radialaxis=dict(visible=True),
            angularaxis=dict(visible=True)
        )
    )
    plots.append(('heatmap_18', fig18, {
        'appearance': {
            'title': {'text': 'Radial Heatmap', 'fontSize': 20}
        }
    }))

    # 19. Bivariate Histogram
    np.random.seed(42)
    x_bi = np.random.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]], 1000)

    fig19 = go.Figure(go.Histogram2d(
        x=x_bi[:, 0],
        y=x_bi[:, 1],
        nbinsx=50,
        nbinsy=50,
        colorscale='Inferno',
        colorbar=dict(title="Frequency")
    ))
    fig19.update_layout(
        title="Bivariate Histogram - Joint Distribution",
        xaxis_title="Variable 1",
        yaxis_title="Variable 2"
    )
    plots.append(('heatmap_19', fig19, {
        'appearance': {
            'title': {'text': 'Bivariate Histogram', 'fontSize': 20}
        }
    }))

    # 20. Sankey Diagram
    fig20 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Input A", "Input B", "Process 1", "Process 2", "Output X", "Output Y"],
            color=["blue", "blue", "green", "green", "red", "red"]
        ),
        link=dict(
            source=[0, 1, 0, 1, 2, 3, 2, 3],
            target=[2, 2, 3, 3, 4, 4, 5, 5],
            value=[8, 4, 2, 8, 8, 4, 2, 6]
        )
    )])
    fig20.update_layout(
        title="Sankey Diagram - Process Flow Visualization",
        font_size=10
    )
    plots.append(('heatmap_20', fig20, {
        'appearance': {
            'title': {'text': 'Sankey Diagram', 'fontSize': 20}
        }
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} heatmap and 2D density plot demonstrations"

# Execute when module is run
if __name__ == "__main__" or True:  # Always execute when imported
    result = create_heatmap_plots()
    print(result)