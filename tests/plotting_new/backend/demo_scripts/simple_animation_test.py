"""
Simple Animation Test
Minimal example to test if animations work
"""

import plotly.graph_objects as go
import numpy as np

# Create a simple animated sine wave
x = np.linspace(0, 2*np.pi, 50)

# Create frames
frames = []
for phase in np.linspace(0, 2*np.pi, 10):
    y = np.sin(x + phase)
    frames.append(go.Frame(
        data=[go.Scatter(x=x, y=y, mode='lines', line=dict(width=3))],
        name=f'frame_{phase:.2f}'
    ))

# Create figure with frames
fig = go.Figure(
    data=[go.Scatter(x=x, y=np.sin(x), mode='lines', line=dict(width=3))],
    frames=frames
)

# Add minimal layout without animation controls
fig.update_layout(
    title="Simple Animation Test",
    showlegend=False
)

print(f"Figure has {len(frames)} frames")
print(f"Layout has updatemenus: {fig.layout.updatemenus is not None}")
print(f"Layout has sliders: {fig.layout.sliders is not None}")

# Show the figure structure for debugging
import json
fig_dict = json.loads(fig.to_json())
print(f"Figure has frames key: {'frames' in fig_dict}")
print(f"Number of frames in dict: {len(fig_dict.get('frames', []))}")

# If running through executor, register the plot
if 'register_plot' in globals():
    register_plot(fig, plot_id='simple_animation', metadata={
        'appearance': {'title': {'text': 'Animation Test'}}
    })
    print("Animation test plot registered")
else:
    print("Running outside executor - showing figure structure only")