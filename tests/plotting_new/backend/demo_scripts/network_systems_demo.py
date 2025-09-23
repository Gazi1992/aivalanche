"""
Network & Systems Demo
Real-world IT and network examples including traffic flow, system monitoring, and performance metrics
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_network_plots():
    """Create network and systems visualizations"""
    plots = []

    # 1. Network Traffic Time Series
    # Simulating 24-hour network traffic pattern
    hours = np.linspace(0, 24, 288)  # 5-minute intervals
    # Base traffic pattern with peaks during business hours
    base_traffic = 100 + 50 * np.sin((hours - 6) * np.pi / 12)
    base_traffic = np.where((hours >= 9) & (hours <= 17), base_traffic + 150, base_traffic)

    # Add some noise and spikes
    incoming = base_traffic + np.random.normal(0, 20, len(hours))
    outgoing = base_traffic * 0.7 + np.random.normal(0, 15, len(hours))

    # Add some traffic spikes
    spike_indices = [50, 120, 200]
    for idx in spike_indices:
        incoming[idx:idx+3] += 200
        outgoing[idx:idx+3] += 150

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=hours, y=incoming,
        mode='lines',
        name='Incoming Traffic',
        fill='tozeroy',
        line=dict(color='blue', width=1),
        fillcolor='rgba(0, 0, 255, 0.3)'
    ))

    fig1.add_trace(go.Scatter(
        x=hours, y=outgoing,
        mode='lines',
        name='Outgoing Traffic',
        fill='tozeroy',
        line=dict(color='green', width=1),
        fillcolor='rgba(0, 255, 0, 0.3)'
    ))

    fig1.update_layout(
        title="Network Traffic Analysis - 24 Hour Period",
        xaxis_title="Hour of Day",
        yaxis_title="Bandwidth (Mbps)",
        hovermode='x unified'
    )
    plots.append(('net_traffic', fig1, {
        'appearance': {'title': {'text': 'Network Traffic'}}
    }))

    # 2. Server Performance Heatmap
    # CPU usage across servers and time
    servers = [f'Server-{i:02d}' for i in range(1, 13)]
    time_slots = [f'{h:02d}:00' for h in range(24)]

    # Generate realistic CPU usage patterns
    cpu_usage = np.random.normal(40, 15, (12, 24))
    # Add patterns: higher usage during business hours
    cpu_usage[:, 9:18] += 25
    # Some servers are more loaded
    cpu_usage[0:3, :] += 15
    cpu_usage[8:10, :] += 10
    # Clip to valid range
    cpu_usage = np.clip(cpu_usage, 0, 100)

    fig2 = go.Figure(data=go.Heatmap(
        z=cpu_usage,
        x=time_slots,
        y=servers,
        colorscale='RdYlGn_r',
        text=cpu_usage.round(0),
        texttemplate='%{text}%',
        textfont={"size": 8},
        colorbar=dict(title="CPU Usage (%)")
    ))

    fig2.update_layout(
        title="Server Farm CPU Usage Monitoring",
        xaxis_title="Time of Day",
        yaxis_title="Server"
    )
    plots.append(('net_server_heat', fig2, {
        'appearance': {'title': {'text': 'Server Performance'}}
    }))

    # 3. Network Topology - Sankey
    fig3 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Internet", "Firewall", "Load Balancer",
                   "Web Server 1", "Web Server 2", "Web Server 3",
                   "App Server 1", "App Server 2",
                   "Database Primary", "Database Replica",
                   "Storage", "Backup"],
            color=["red", "orange", "yellow",
                   "lightblue", "lightblue", "lightblue",
                   "lightgreen", "lightgreen",
                   "purple", "purple",
                   "gray", "darkgray"]
        ),
        link=dict(
            source=[0, 1, 2, 2, 2, 3, 4, 5, 3, 4, 5, 6, 7, 8, 9, 8, 9],
            target=[1, 2, 3, 4, 5, 6, 6, 7, 7, 7, 6, 8, 9, 10, 10, 11, 11],
            value=[1000, 950, 300, 300, 350, 150, 150, 175, 150, 150, 175, 300, 325, 400, 200, 100, 50]
        )
    )])

    fig3.update_layout(
        title="Network Architecture Data Flow",
        font_size=10
    )
    plots.append(('net_topology', fig3, {
        'appearance': {'title': {'text': 'Network Topology'}}
    }))

    # 4. System Metrics Dashboard
    fig4 = go.Figure()

    # CPU Usage Gauge
    fig4.add_trace(go.Indicator(
        mode="gauge+number",
        value=73,
        title={'text': "CPU Usage (%)"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 50], 'color': "lightgreen"},
                   {'range': [50, 80], 'color': "yellow"},
                   {'range': [80, 100], 'color': "red"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}},
        domain={'x': [0, 0.45], 'y': [0.5, 1]}
    ))

    # Memory Usage
    fig4.add_trace(go.Indicator(
        mode="gauge+number",
        value=16.8,
        title={'text': "Memory Usage (GB)"},
        gauge={'axis': {'range': [0, 32]},
               'bar': {'color': "green"},
               'steps': [
                   {'range': [0, 16], 'color': "lightgray"},
                   {'range': [16, 24], 'color': "yellow"},
                   {'range': [24, 32], 'color': "red"}]},
        domain={'x': [0.55, 1], 'y': [0.5, 1]}
    ))

    # Disk I/O
    fig4.add_trace(go.Indicator(
        mode="number+delta",
        value=245,
        title={'text': "Disk I/O (MB/s)"},
        delta={'reference': 200, 'increasing': {'color': "red"}},
        domain={'x': [0, 0.45], 'y': [0, 0.45]}
    ))

    # Network Latency
    fig4.add_trace(go.Indicator(
        mode="number+delta",
        value=12.5,
        title={'text': "Network Latency (ms)"},
        delta={'reference': 15, 'decreasing': {'color': "green"}},
        domain={'x': [0.55, 1], 'y': [0, 0.45]}
    ))

    fig4.update_layout(
        title="System Performance Dashboard"
    )
    plots.append(('net_dashboard', fig4, {
        'appearance': {'title': {'text': 'System Dashboard'}}
    }))

    # 5. API Response Times - Box Plots
    endpoints = ['/api/users', '/api/products', '/api/orders', '/api/auth', '/api/search']

    # Generate response time distributions
    response_times = []
    for i, endpoint in enumerate(endpoints):
        base_time = 50 + i * 20
        times = np.concatenate([
            np.random.normal(base_time, 10, 80),  # Normal responses
            np.random.exponential(base_time * 2, 15),  # Some slow responses
            np.random.uniform(base_time * 3, base_time * 5, 5)  # Outliers
        ])
        response_times.append(times)

    fig5 = go.Figure()

    for endpoint, times in zip(endpoints, response_times):
        fig5.add_trace(go.Box(
            y=times,
            name=endpoint,
            boxpoints='outliers'
        ))

    fig5.update_layout(
        title="API Endpoint Response Time Analysis",
        yaxis_title="Response Time (ms)",
        showlegend=False
    )
    plots.append(('net_api_response', fig5, {
        'appearance': {'title': {'text': 'API Performance'}}
    }))

    # 6. Error Rate Scatter
    # Errors vs request volume
    hours_day = np.arange(24)
    request_volume = 1000 + 500 * np.sin((hours_day - 6) * np.pi / 12)
    request_volume = np.where((hours_day >= 9) & (hours_day <= 17), request_volume + 2000, request_volume)

    # Error rate increases with volume but with some randomness
    error_rate = 0.5 + 0.001 * request_volume + np.random.normal(0, 0.3, len(hours_day))
    error_rate = np.clip(error_rate, 0, 5)

    # Color by severity
    severity = np.where(error_rate > 3, 'Critical',
                        np.where(error_rate > 2, 'Warning', 'Normal'))
    colors = {'Normal': 'green', 'Warning': 'yellow', 'Critical': 'red'}

    fig6 = go.Figure()

    for sev in ['Normal', 'Warning', 'Critical']:
        mask = severity == sev
        fig6.add_trace(go.Scatter(
            x=request_volume[mask],
            y=error_rate[mask],
            mode='markers',
            name=sev,
            marker=dict(size=10, color=colors[sev]),
            text=[f"Hour {h}" for h in hours_day[mask]]
        ))

    fig6.update_layout(
        title="Error Rate vs Request Volume",
        xaxis_title="Requests per Hour",
        yaxis_title="Error Rate (%)"
    )
    plots.append(('net_errors', fig6, {
        'appearance': {'title': {'text': 'Error Analysis'}}
    }))

    # 7. Database Query Performance - Waterfall
    query_stages = ['Parse', 'Plan', 'Index Scan', 'Join', 'Filter', 'Sort', 'Network', 'Total']
    times = [5, 12, 45, 28, 15, 8, 3, 116]

    fig7 = go.Figure(go.Waterfall(
        x=query_stages,
        y=times,
        text=[f"{t} ms" for t in times],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))

    fig7.update_layout(
        title="Database Query Execution Breakdown",
        yaxis_title="Time (milliseconds)",
        showlegend=False
    )
    plots.append(('net_db_perf', fig7, {
        'appearance': {'title': {'text': 'Query Performance'}}
    }))

    # 8. Service Dependency Graph - 3D Network
    # Create a 3D visualization of service dependencies
    n_services = 20
    np.random.seed(42)

    # Generate positions for services in 3D space
    theta = np.random.uniform(0, 2*np.pi, n_services)
    phi = np.random.uniform(0, np.pi, n_services)
    r = np.random.uniform(0.5, 1.5, n_services)

    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)

    # Service types determine color
    service_types = np.random.choice(['Web', 'API', 'Database', 'Cache', 'Queue'], n_services)
    type_colors = {'Web': 'blue', 'API': 'green', 'Database': 'red', 'Cache': 'yellow', 'Queue': 'purple'}
    colors = [type_colors[t] for t in service_types]

    # Create some connections
    edge_trace = []
    for i in range(n_services):
        # Each service connects to 1-3 others
        n_connections = np.random.randint(1, 4)
        targets = np.random.choice([j for j in range(n_services) if j != i], n_connections, replace=False)

        for target in targets:
            edge_trace.append(go.Scatter3d(
                x=[x[i], x[target]],
                y=[y[i], y[target]],
                z=[z[i], z[target]],
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))

    fig8 = go.Figure(data=edge_trace)

    # Add service nodes
    fig8.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers+text',
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=1, color='white')
        ),
        text=[f"Service-{i}" for i in range(n_services)],
        textposition='top center',
        textfont=dict(size=8),
        hovertext=[f"Service-{i}<br>Type: {t}" for i, t in enumerate(service_types)],
        hoverinfo='text'
    ))

    fig8.update_layout(
        title="Service Dependency Network - 3D View",
        showlegend=False,
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            zaxis=dict(showgrid=False, zeroline=False, visible=False)
        )
    )
    plots.append(('net_service_3d', fig8, {
        'appearance': {'title': {'text': 'Service Network'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} network and systems visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_network_plots()
    print(result)