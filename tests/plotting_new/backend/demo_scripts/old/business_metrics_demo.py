"""
Business Metrics Demo
Real-world business examples including sales, KPIs, and performance tracking
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_business_plots():
    """Create business metrics visualizations"""
    plots = []

    # 1. Sales Performance Bar Chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    actual_sales = [120, 135, 155, 142, 165, 178, 195, 188, 210, 198, 220, 245]
    target_sales = [130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240]

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        name='Actual Sales',
        x=months,
        y=actual_sales,
        text=[f'${v}k' for v in actual_sales],
        textposition='outside',
        marker_color='rgb(55, 83, 109)'
    ))
    fig1.add_trace(go.Bar(
        name='Target Sales',
        x=months,
        y=target_sales,
        text=[f'${v}k' for v in target_sales],
        textposition='outside',
        marker_color='rgb(180, 180, 180)',
        opacity=0.5
    ))
    fig1.update_layout(
        title="Monthly Sales Performance vs Target",
        yaxis_title="Sales ($1000s)",
        barmode='group',
        hovermode='x unified'
    )
    plots.append(('biz_sales_bar', fig1, {
        'appearance': {'title': {'text': 'Sales Performance'}}
    }))

    # 2. Revenue Breakdown Pie Chart
    categories = ['Product Sales', 'Services', 'Subscriptions', 'Licensing', 'Support']
    revenue = [3500, 2100, 1800, 750, 450]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    fig2 = go.Figure(data=[go.Pie(
        labels=categories,
        values=revenue,
        hole=0.4,  # Make it a donut chart
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textposition='outside',
        pull=[0.1, 0, 0, 0, 0]  # Pull out the largest segment
    )])
    fig2.update_layout(
        title="Revenue Breakdown by Category",
        annotations=[dict(text='2024', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    plots.append(('biz_revenue_pie', fig2, {
        'appearance': {'title': {'text': 'Revenue Breakdown'}}
    }))

    # 3. Sales Conversion Funnel
    stages = ['Website Visits', 'Sign-ups', 'Trial Users', 'Active Users', 'Paying Customers', 'Premium Tier']
    values = [15000, 4500, 2000, 1200, 800, 350]

    fig3 = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        opacity=0.8,
        marker=dict(
            color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
        )
    ))
    fig3.update_layout(
        title="Customer Conversion Funnel",
    )
    plots.append(('biz_funnel', fig3, {
        'appearance': {'title': {'text': 'Conversion Funnel'}}
    }))

    # 4. Market Share Treemap
    labels = ['Total Market',
              'Our Company', 'Product A', 'Product B', 'Product C',
              'Competitor 1', 'Comp1-P1', 'Comp1-P2',
              'Competitor 2', 'Comp2-P1', 'Comp2-P2',
              'Others', 'Other1', 'Other2', 'Other3']
    parents = ['',
               'Total Market', 'Our Company', 'Our Company', 'Our Company',
               'Total Market', 'Competitor 1', 'Competitor 1',
               'Total Market', 'Competitor 2', 'Competitor 2',
               'Total Market', 'Others', 'Others', 'Others']
    values = [0,
              0, 25, 15, 10,
              0, 20, 12,
              0, 10, 5,
              0, 5, 3, 5]

    fig4 = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colorscale='Blues',
            line=dict(width=2)
        ),
        textinfo="label+value+percent parent"
    ))
    fig4.update_layout(
        title="Market Share Analysis"
    )
    plots.append(('biz_market_share', fig4, {
        'appearance': {'title': {'text': 'Market Share'}}
    }))

    # 5. KPI Indicators Dashboard
    fig5 = go.Figure()

    # Revenue indicator
    fig5.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=8.7,
        title={'text': "Revenue (M$)"},
        delta={'reference': 7.5},
        gauge={'axis': {'range': [None, 10]},
               'bar': {'color': "darkgreen"},
               'steps': [
                   {'range': [0, 5], 'color': "lightgray"},
                   {'range': [5, 8], 'color': "gray"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 9}},
        domain={'x': [0, 0.45], 'y': [0, 1]}
    ))

    # Customer satisfaction indicator
    fig5.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=85,
        title={'text': "Customer Satisfaction (%)"},
        delta={'reference': 78},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 50], 'color': "lightgray"},
                   {'range': [50, 80], 'color': "gray"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}},
        domain={'x': [0.55, 1], 'y': [0, 1]}
    ))

    fig5.update_layout(
        title="Key Performance Indicators",
    )
    plots.append(('biz_kpi', fig5, {
        'appearance': {'title': {'text': 'KPI Dashboard'}}
    }))

    # 6. Revenue Waterfall Chart
    categories = ['Q1 Revenue', 'New Customers', 'Upsells', 'Churn', 'Q2 Revenue',
                  'New Products', 'Price Increase', 'Q3 Revenue']
    values = [5000, 800, 400, -300, 5900, 600, 200, 6700]

    fig6 = go.Figure(go.Waterfall(
        x=categories,
        y=values,
        text=[f"${v:+,.0f}" if v != 5000 and v != 5900 and v != 6700 else f"${v:,.0f}" for v in values],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},
        totals={"marker": {"color": "blue"}}
    ))
    fig6.update_layout(
        title="Quarterly Revenue Flow Analysis",
        yaxis_title="Revenue ($)",
        showlegend=False
    )
    plots.append(('biz_revenue_waterfall', fig6, {
        'appearance': {'title': {'text': 'Revenue Flow'}}
    }))

    # 7. Department Budget - Simple Hierarchical Bar Chart
    departments = ['Engineering', 'R&D', 'DevOps', 'QA',
                   'Direct Sales', 'Channel', 'Online',
                   'Digital Mkt', 'Events', 'Content',
                   'HR', 'Finance', 'Legal']
    values = [30, 25, 15, 10, 20, 15, 10, 12, 8, 5, 8, 10, 7]
    colors = ['#3498db']*4 + ['#2ecc71']*3 + ['#e74c3c']*3 + ['#f39c12']*3  # Operations, Sales, Marketing, Admin

    fig7 = go.Figure(data=[
        go.Bar(
            x=departments,
            y=values,
            text=[f'${v}M' for v in values],
            textposition='outside',
            marker=dict(
                color=colors,
                line=dict(color='white', width=1)
            )
        )
    ])

    # Add department grouping annotations
    fig7.add_annotation(x=1.5, y=-8, text="Operations", showarrow=False, font=dict(size=10, color='#3498db'))
    fig7.add_annotation(x=5, y=-8, text="Sales", showarrow=False, font=dict(size=10, color='#2ecc71'))
    fig7.add_annotation(x=8, y=-8, text="Marketing", showarrow=False, font=dict(size=10, color='#e74c3c'))
    fig7.add_annotation(x=11, y=-8, text="Admin", showarrow=False, font=dict(size=10, color='#f39c12'))
    fig7.update_layout(
        title="Department Budget Allocation"
    )
    plots.append(('biz_budget_sunburst', fig7, {
        'appearance': {'title': {'text': 'Budget Allocation'}}
    }))

    # 8. Growth Metrics Line Chart
    dates = pd.date_range('2024-01', '2024-12', freq='M')
    users = [1000, 1150, 1380, 1650, 2000, 2450, 3000, 3600, 4200, 4800, 5400, 6000]
    revenue = [50, 58, 70, 85, 105, 130, 160, 195, 230, 265, 300, 340]

    fig8 = go.Figure()

    # Users on primary y-axis
    fig8.add_trace(go.Scatter(
        x=dates,
        y=users,
        mode='lines+markers',
        name='Active Users',
        line=dict(color='blue', width=3),
        marker=dict(size=8),
        yaxis='y'
    ))

    # Revenue on secondary y-axis
    fig8.add_trace(go.Scatter(
        x=dates,
        y=revenue,
        mode='lines+markers',
        name='Revenue ($k)',
        line=dict(color='green', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))

    fig8.update_layout(
        title="Growth Metrics - Users & Revenue",
        xaxis=dict(title="Month"),
        yaxis=dict(title="Active Users", side="left", color="blue"),
        yaxis2=dict(title="Revenue ($1000s)", overlaying="y", side="right", color="green"),
        hovermode='x unified'
    )
    plots.append(('biz_growth', fig8, {
        'appearance': {'title': {'text': 'Growth Metrics'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} business metrics visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_business_plots()
    print(result)