"""
Healthcare Analytics Demo
Real-world healthcare examples including patient data, clinical metrics, and health outcomes
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_healthcare_plots():
    """Create healthcare analytics visualizations"""
    plots = []

    # 1. Patient Vitals Time Series
    # Simulating ICU patient monitoring data
    hours = np.arange(0, 48, 0.5)  # 48 hours, every 30 minutes
    heart_rate = 75 + 10 * np.sin(hours/6) + np.random.normal(0, 3, len(hours))
    bp_systolic = 120 + 8 * np.sin(hours/8) + np.random.normal(0, 4, len(hours))
    bp_diastolic = 80 + 5 * np.sin(hours/8) + np.random.normal(0, 3, len(hours))
    spo2 = 97 + 2 * np.sin(hours/4) + np.random.normal(0, 1, len(hours))
    spo2 = np.clip(spo2, 92, 100)

    fig1 = go.Figure()

    # Heart rate
    fig1.add_trace(go.Scatter(
        x=hours, y=heart_rate,
        mode='lines',
        name='Heart Rate',
        line=dict(color='red', width=2),
        yaxis='y'
    ))

    # Blood pressure
    fig1.add_trace(go.Scatter(
        x=hours, y=bp_systolic,
        mode='lines',
        name='BP Systolic',
        line=dict(color='blue', width=2, dash='solid'),
        yaxis='y2'
    ))

    fig1.add_trace(go.Scatter(
        x=hours, y=bp_diastolic,
        mode='lines',
        name='BP Diastolic',
        line=dict(color='blue', width=2, dash='dash'),
        yaxis='y2'
    ))

    # SpO2
    fig1.add_trace(go.Scatter(
        x=hours, y=spo2,
        mode='lines',
        name='SpO2',
        line=dict(color='green', width=2),
        yaxis='y3'
    ))

    fig1.update_layout(
        title="Patient Vitals Monitoring - 48 Hour Trend",
        xaxis=dict(title="Hours", domain=[0.1, 1]),
        yaxis=dict(title="Heart Rate (bpm)", side="left", position=0, color="red"),
        yaxis2=dict(title="Blood Pressure (mmHg)", overlaying="y", side="left", position=0.05, color="blue"),
        yaxis3=dict(title="SpO2 (%)", overlaying="y", side="right", color="green"),
        hovermode='x unified'
    )
    plots.append(('health_vitals', fig1, {
        'appearance': {'title': {'text': 'Patient Vitals'}}
    }))

    # 2. Disease Prevalence Heatmap
    # Age groups vs conditions
    age_groups = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '80+']
    conditions = ['Diabetes', 'Hypertension', 'Asthma', 'Heart Disease', 'Cancer', 'Arthritis']

    # Create realistic prevalence data (percentage)
    prevalence = np.array([
        [2, 1, 8, 0.5, 0.1, 0.5],      # 0-10
        [5, 3, 10, 1, 0.5, 2],          # 11-20
        [8, 8, 9, 2, 1, 5],             # 21-30
        [12, 15, 8, 5, 3, 10],          # 31-40
        [18, 25, 7, 10, 8, 20],         # 41-50
        [25, 35, 6, 18, 15, 35],        # 51-60
        [30, 45, 5, 28, 20, 45],        # 61-70
        [35, 55, 4, 35, 25, 55],        # 71-80
        [40, 60, 3, 40, 30, 60]         # 80+
    ])

    fig2 = go.Figure(data=go.Heatmap(
        z=prevalence,
        x=conditions,
        y=age_groups,
        colorscale='YlOrRd',
        text=prevalence.round(1),
        texttemplate='%{text}%',
        textfont={"size": 10},
        colorbar=dict(title="Prevalence (%)")
    ))

    fig2.update_layout(
        title="Disease Prevalence by Age Group",
        xaxis_title="Condition",
        yaxis_title="Age Group"
    )
    plots.append(('health_prevalence', fig2, {
        'appearance': {'title': {'text': 'Disease Prevalence'}}
    }))

    # 3. Treatment Outcome Sankey
    fig3 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Patients", "Surgery", "Medication", "Therapy",
                   "Full Recovery", "Partial Recovery", "Ongoing Care", "Readmission"],
            color=["blue", "green", "green", "green",
                   "darkgreen", "yellow", "orange", "red"]
        ),
        link=dict(
            source=[0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3],
            target=[1, 2, 3, 4, 5, 6, 4, 5, 7, 5, 6],
            value=[300, 500, 200, 180, 90, 30, 350, 100, 50, 140, 60]
        )
    )])

    fig3.update_layout(
        title="Patient Treatment Pathways and Outcomes",
        font_size=10
    )
    plots.append(('health_treatment_flow', fig3, {
        'appearance': {'title': {'text': 'Treatment Pathways'}}
    }))

    # 4. Hospital Capacity Indicators
    fig4 = go.Figure()

    # ICU Capacity
    fig4.add_trace(go.Indicator(
        mode="gauge+number",
        value=78,
        title={'text': "ICU Occupancy (%)"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 60], 'color': "lightgreen"},
                   {'range': [60, 85], 'color': "yellow"},
                   {'range': [85, 100], 'color': "red"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}},
        domain={'x': [0, 0.45], 'y': [0.5, 1]}
    ))

    # ER Wait Time
    fig4.add_trace(go.Indicator(
        mode="number+delta",
        value=3.5,
        title={'text': "ER Wait Time (hours)"},
        delta={'reference': 2.0, 'increasing': {'color': "red"}},
        domain={'x': [0.55, 1], 'y': [0.5, 1]}
    ))

    # Bed Availability
    fig4.add_trace(go.Indicator(
        mode="number+delta",
        value=42,
        title={'text': "Available Beds"},
        delta={'reference': 50, 'decreasing': {'color': "orange"}},
        domain={'x': [0, 0.45], 'y': [0, 0.45]}
    ))

    # Staff Ratio
    fig4.add_trace(go.Indicator(
        mode="number",
        value=4.2,
        title={'text': "Nurse:Patient Ratio"},
        number={'suffix': ":1"},
        domain={'x': [0.55, 1], 'y': [0, 0.45]}
    ))

    fig4.update_layout(
        title="Hospital Capacity Dashboard"
    )
    plots.append(('health_capacity', fig4, {
        'appearance': {'title': {'text': 'Hospital Capacity'}}
    }))

    # 5. Clinical Trial Results - Box Plots
    np.random.seed(42)
    placebo = np.concatenate([
        np.random.normal(0, 2, 30),    # No improvement
        np.random.normal(5, 3, 20)     # Placebo effect
    ])

    drug_a = np.concatenate([
        np.random.normal(0, 2, 10),    # Non-responders
        np.random.normal(15, 4, 40)    # Responders
    ])

    drug_b = np.concatenate([
        np.random.normal(0, 2, 5),     # Non-responders
        np.random.normal(20, 5, 45)    # Strong responders
    ])

    combination = np.concatenate([
        np.random.normal(0, 2, 3),     # Non-responders
        np.random.normal(25, 4, 47)    # Best response
    ])

    fig5 = go.Figure()

    fig5.add_trace(go.Box(
        y=placebo,
        name='Placebo',
        boxpoints='outliers',
        marker_color='lightgray',
        boxmean='sd'
    ))

    fig5.add_trace(go.Box(
        y=drug_a,
        name='Drug A',
        boxpoints='outliers',
        marker_color='lightblue',
        boxmean='sd'
    ))

    fig5.add_trace(go.Box(
        y=drug_b,
        name='Drug B',
        boxpoints='outliers',
        marker_color='lightgreen',
        boxmean='sd'
    ))

    fig5.add_trace(go.Box(
        y=combination,
        name='A + B',
        boxpoints='outliers',
        marker_color='lightcoral',
        boxmean='sd'
    ))

    fig5.update_layout(
        title="Clinical Trial - Treatment Efficacy Comparison",
        yaxis_title="Improvement Score",
        showlegend=False
    )
    plots.append(('health_clinical_trial', fig5, {
        'appearance': {'title': {'text': 'Clinical Trial Results'}}
    }))

    # 6. Epidemic Spread Model
    days = np.arange(0, 180)
    # SIR model simulation
    S = 1000000  # Susceptible
    I = 100      # Infected
    R = 0        # Recovered

    beta = 0.5   # Transmission rate
    gamma = 0.1  # Recovery rate

    susceptible = []
    infected = []
    recovered = []

    for day in days:
        susceptible.append(S)
        infected.append(I)
        recovered.append(R)

        dS = -beta * S * I / 1000000
        dI = beta * S * I / 1000000 - gamma * I
        dR = gamma * I

        S = max(0, S + dS)
        I = max(0, I + dI)
        R = R + dR

    fig6 = go.Figure()

    fig6.add_trace(go.Scatter(
        x=days, y=susceptible,
        mode='lines',
        name='Susceptible',
        line=dict(color='blue', width=2),
        stackgroup='one'
    ))

    fig6.add_trace(go.Scatter(
        x=days, y=infected,
        mode='lines',
        name='Infected',
        line=dict(color='red', width=2),
        stackgroup='one'
    ))

    fig6.add_trace(go.Scatter(
        x=days, y=recovered,
        mode='lines',
        name='Recovered',
        line=dict(color='green', width=2),
        stackgroup='one'
    ))

    fig6.update_layout(
        title="Epidemic Spread Model (SIR)",
        xaxis_title="Days",
        yaxis_title="Population",
        hovermode='x unified'
    )
    plots.append(('health_epidemic', fig6, {
        'appearance': {'title': {'text': 'Epidemic Model'}}
    }))

    # 7. Medical Imaging Histogram
    # Simulating pixel intensity distribution from medical scan
    normal_tissue = np.random.normal(100, 20, 5000)
    abnormal_tissue = np.random.normal(150, 15, 1000)

    fig7 = go.Figure()

    fig7.add_trace(go.Histogram(
        x=normal_tissue,
        nbinsx=50,
        name='Normal Tissue',
        marker_color='green',
        opacity=0.7,
        histnorm='probability'
    ))

    fig7.add_trace(go.Histogram(
        x=abnormal_tissue,
        nbinsx=50,
        name='Abnormal Tissue',
        marker_color='red',
        opacity=0.7,
        histnorm='probability'
    ))

    fig7.update_layout(
        title="Medical Imaging - Tissue Density Distribution",
        xaxis_title="Pixel Intensity",
        yaxis_title="Probability",
        barmode='overlay'
    )
    plots.append(('health_imaging', fig7, {
        'appearance': {'title': {'text': 'Medical Imaging'}}
    }))

    # 8. Healthcare Cost Breakdown
    categories = ['Emergency', 'Surgery', 'Medications', 'Lab Tests',
                  'Imaging', 'Consultation', 'Therapy', 'Other']
    costs = [12000, 25000, 8000, 3500, 4500, 2000, 6000, 1500]

    fig8 = go.Figure(data=[go.Pie(
        labels=categories,
        values=costs,
        hole=0.4,
        marker=dict(
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
                   '#FECA57', '#48DBFB', '#FF9FF3', '#C7ECEE'],
            line=dict(color='white', width=2)
        ),
        textinfo='label+percent',
        textposition='outside',
        pull=[0.1 if c == max(costs) else 0 for c in costs]
    )])

    total_cost = sum(costs)
    fig8.update_layout(
        title="Healthcare Cost Breakdown by Service",
        annotations=[dict(
            text=f'Total<br>${total_cost:,}',
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )]
    )
    plots.append(('health_costs', fig8, {
        'appearance': {'title': {'text': 'Healthcare Costs'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} healthcare analytics visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_healthcare_plots()
    print(result)