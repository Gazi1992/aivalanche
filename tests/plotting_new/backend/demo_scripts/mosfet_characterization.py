"""
Demo Script: MOSFET Characterization Analysis
Advanced visualization with parameter sweeps and 3D surface plots
"""

# Load MOSFET characteristic data
df = load_data('mosfet_characteristic_dense.csv')
print(f"MOSFET Data: {df.shape[0]} measurements")
print(f"Parameters: {list(df.columns)}")

# Get unique gate voltages for family curves
vgs_values = sorted(df['vgs'].unique())
print(f"\nGate voltages (V_GS): {vgs_values}")

# Create I-V characteristic family curves
fig = go.Figure()

# Use a color scale for different V_GS values
colors = px.colors.sequential.Plasma
n_colors = len(vgs_values)

for i, vgs in enumerate(vgs_values):
    df_vgs = df[df['vgs'] == vgs].sort_values('vds')
    color_idx = int(i * (len(colors) - 1) / (n_colors - 1))
    
    fig.add_trace(go.Scatter(
        x=df_vgs['vds'], 
        y=df_vgs['ids'],
        mode='lines',
        name=f'V_GS = {vgs}V',
        line=dict(width=2, color=colors[color_idx])
    ))

fig.update_layout(
    title='MOSFET Output Characteristics (I_D vs V_DS)',
    xaxis_title='Drain-Source Voltage V_DS (V)',
    yaxis_title='Drain Current I_D (A)',
    hovermode='x unified',
    template='plotly_white'
)
register_plot(fig, plot_id='mosfet_iv_curves',
              metadata={'device': 'MOSFET', 'type': 'output_characteristics'})

# Create 3D surface plot
fig_3d = go.Figure(data=[go.Scatter3d(
    x=df['vds'],
    y=df['vgs'],
    z=df['ids'],
    mode='markers',
    marker=dict(
        size=3,
        color=df['ids'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title='I_D (A)')
    )
)])

fig_3d.update_layout(
    title='MOSFET 3D Characteristic Surface',
    scene=dict(
        xaxis_title='V_DS (V)',
        yaxis_title='V_GS (V)',
        zaxis_title='I_D (A)',
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
    ),
    height=600
)
register_plot(fig_3d, plot_id='mosfet_3d_surface',
              metadata={'visualization': '3D', 'interactive': True})

# Transconductance analysis (gm = dI_D/dV_GS at fixed V_DS)
vds_fixed = 5.0  # Choose a V_DS value in saturation
df_gm = df[df['vds'] == vds_fixed].sort_values('vgs')

if len(df_gm) > 1:
    # Calculate transconductance
    gm = np.gradient(df_gm['ids'].values, df_gm['vgs'].values)
    
    fig_gm = make_subplots(rows=2, cols=1,
                           subplot_titles=('Transfer Characteristics',
                                         'Transconductance (gm)'),
                           shared_xaxes=True)
    
    # Transfer characteristics
    fig_gm.add_trace(go.Scatter(x=df_gm['vgs'], y=df_gm['ids'],
                                mode='lines+markers', name='I_D',
                                line=dict(color='blue', width=2)),
                     row=1, col=1)
    
    # Transconductance
    fig_gm.add_trace(go.Scatter(x=df_gm['vgs'].values, y=gm,
                                mode='lines+markers', name='gm',
                                line=dict(color='red', width=2)),
                     row=2, col=1)
    
    fig_gm.update_xaxes(title_text='Gate Voltage V_GS (V)', row=2, col=1)
    fig_gm.update_yaxes(title_text='I_D (A)', row=1, col=1)
    fig_gm.update_yaxes(title_text='gm (S)', row=2, col=1)
    fig_gm.update_layout(title=f'MOSFET Transfer Analysis at V_DS = {vds_fixed}V',
                        height=600)
    
    register_plot(fig_gm, plot_id='mosfet_transconductance',
                  metadata={'analysis': 'small_signal', 'vds': vds_fixed})
    
    # Find threshold voltage (simplified extraction)
    threshold_current = 1e-6  # 1 µA threshold
    above_threshold = df_gm[df_gm['ids'] > threshold_current]
    if len(above_threshold) > 0:
        vth = above_threshold.iloc[0]['vgs']
        print(f"\n=== Device Parameters ===")
        print(f"Estimated Threshold Voltage (V_th): {vth:.2f} V")
        print(f"Maximum Transconductance: {gm.max():.3e} S")

# Output resistance analysis (r_o = dV_DS/dI_D in saturation)
vgs_sat = 3.0  # Gate voltage in saturation
df_ro = df[df['vgs'] == vgs_sat].sort_values('vds')
# Focus on saturation region (higher V_DS values)
df_sat = df_ro[df_ro['vds'] > 2.0]

if len(df_sat) > 1:
    ro = np.gradient(df_sat['vds'].values, df_sat['ids'].values)
    avg_ro = np.mean(np.abs(ro[np.isfinite(ro)]))
    print(f"Output Resistance (r_o) at V_GS={vgs_sat}V: {avg_ro:.1f} Ω")

print(f"\n=== Analysis Complete ===")
print(f"✓ Generated {len(datasets)} dataset(s)")
print(f"✓ Created I-V family curves")
print(f"✓ Built 3D characteristic surface")
print(f"✓ Analyzed small-signal parameters")