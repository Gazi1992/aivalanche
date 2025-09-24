"""
Multi-Format Animation Demo
Testing various animation approaches that can work through the executor
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
import base64
import io
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_agg import FigureCanvasAgg

def create_animation_outputs():
    """Create various types of animations that can be displayed on frontend"""
    outputs = []

    # ============================================
    # 1. PLOTLY NATIVE ANIMATION (Already works)
    # ============================================

    x = np.linspace(0, 4*np.pi, 100)
    frames = []
    for phase in np.linspace(0, 2*np.pi, 30):
        y = np.sin(x + phase)
        frames.append(go.Frame(
            data=[go.Scatter(x=x, y=y, mode='lines', line=dict(color='blue', width=2))],
            name=str(phase)
        ))

    fig_plotly = go.Figure(
        data=[go.Scatter(x=x, y=np.sin(x), mode='lines')],
        frames=frames
    )

    fig_plotly.update_layout(
        title="Plotly Native Animation",
        updatemenus=[{
            'type': 'buttons',
            'buttons': [
                {'label': 'Play', 'method': 'animate',
                 'args': [None, {'frame': {'duration': 50}}]},
                {'label': 'Pause', 'method': 'animate',
                 'args': [[None], {'frame': {'duration': 0}}]}
            ]
        }],
        sliders=[{
            'steps': [{'args': [[f.name]], 'label': str(i), 'method': 'animate'}
                     for i, f in enumerate(frames)],
            'active': 0
        }]
    )

    register_plot(fig_plotly, plot_id='native_plotly_anim', metadata={
        'appearance': {'title': {'text': 'Plotly Animation'}},
        'type': 'animation',
        'animation_type': 'plotly_native'
    })

    # ============================================
    # 2. ANIMATED GIF GENERATION
    # ============================================

    # Create frames for a simple animated GIF
    gif_frames = []
    fig_size = (400, 300)

    for i in range(20):
        img = Image.new('RGB', fig_size, 'white')
        draw = ImageDraw.Draw(img)

        # Draw animated circle
        radius = 20 + i * 5
        center_x = 200
        center_y = 150
        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius, center_y + radius],
            outline='blue', width=2
        )

        # Draw animated sine wave
        for x in range(0, 400, 5):
            y = 150 + 50 * np.sin((x + i * 20) * 0.02)
            draw.ellipse([x-2, y-2, x+2, y+2], fill='red')

        gif_frames.append(img)

    # Save as animated GIF
    gif_buffer = io.BytesIO()
    gif_frames[0].save(
        gif_buffer,
        format='GIF',
        save_all=True,
        append_images=gif_frames[1:],
        duration=50,
        loop=0
    )
    gif_data = base64.b64encode(gif_buffer.getvalue()).decode()

    # Create a Plotly figure that displays the GIF
    fig_gif = go.Figure()
    fig_gif.add_layout_image(
        dict(
            source=f"data:image/gif;base64,{gif_data}",
            xref="paper", yref="paper",
            x=0, y=1,
            sizex=1, sizey=1,
            xanchor="left", yanchor="top"
        )
    )
    fig_gif.update_layout(
        title="Animated GIF Embedded",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    register_plot(fig_gif, plot_id='animated_gif', metadata={
        'appearance': {'title': {'text': 'GIF Animation'}},
        'type': 'animation',
        'animation_type': 'gif_embedded',
        'gif_data': gif_data
    })

    # ============================================
    # 3. HTML/CSS ANIMATION
    # ============================================

    # Create HTML with CSS animations
    html_animation = """
    <div style="width: 100%; height: 400px; position: relative; background: #f0f0f0;">
        <style>
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-100px); }
            }
            @keyframes rotate {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            .bouncing-ball {
                width: 50px;
                height: 50px;
                background: radial-gradient(circle, #4CAF50, #45a049);
                border-radius: 50%;
                position: absolute;
                bottom: 50px;
                left: 50%;
                animation: bounce 2s infinite;
            }
            .rotating-square {
                width: 60px;
                height: 60px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                position: absolute;
                top: 50px;
                left: 100px;
                animation: rotate 3s linear infinite;
            }
            .progress-bar {
                width: 80%;
                height: 20px;
                background: #ddd;
                position: absolute;
                bottom: 10px;
                left: 10%;
                overflow: hidden;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                animation: progress 4s ease-in-out infinite;
            }
            @keyframes progress {
                0% { width: 0%; }
                50% { width: 100%; }
                100% { width: 0%; }
            }
        </style>
        <div class="bouncing-ball"></div>
        <div class="rotating-square"></div>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        <h3 style="text-align: center; padding-top: 200px;">CSS Animations Running!</h3>
    </div>
    """

    # Create a Plotly figure with HTML
    fig_html = go.Figure()
    fig_html.add_annotation(
        text=html_animation,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=1)  # Small font size as we're using this for positioning
    )
    fig_html.update_layout(
        title="HTML/CSS Animation",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    register_plot(fig_html, plot_id='html_css_anim', metadata={
        'appearance': {'title': {'text': 'HTML/CSS Animation'}},
        'type': 'animation',
        'animation_type': 'html_css',
        'html_content': html_animation
    })

    # ============================================
    # 4. FRAME-BY-FRAME IMAGES AS PLOTLY SUBPLOTS
    # ============================================

    from plotly.subplots import make_subplots

    # Generate frames as static images
    n_frames = 6
    fig_frames = make_subplots(
        rows=2, cols=3,
        subplot_titles=[f"Frame {i+1}" for i in range(n_frames)]
    )

    t_values = np.linspace(0, 2*np.pi, n_frames)
    x = np.linspace(0, 4*np.pi, 100)

    for i in range(n_frames):
        row = i // 3 + 1
        col = i % 3 + 1
        y = np.sin(x + t_values[i])

        fig_frames.add_trace(
            go.Scatter(x=x, y=y, mode='lines', showlegend=False),
            row=row, col=col
        )

    fig_frames.update_layout(
        title="Animation as Frame Sequence",
        showlegend=False
    )

    register_plot(fig_frames, plot_id='frame_sequence', metadata={
        'appearance': {'title': {'text': 'Frame Sequence'}},
        'type': 'animation',
        'animation_type': 'frame_sequence'
    })

    # ============================================
    # 5. ANIMATED SVG PATH
    # ============================================

    svg_animation = """
    <svg width="500" height="300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1">
                    <animate attributeName="stop-color"
                        values="rgb(255,255,0);rgb(255,0,0);rgb(255,255,0)"
                        dur="3s" repeatCount="indefinite" />
                </stop>
                <stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1">
                    <animate attributeName="stop-color"
                        values="rgb(255,0,0);rgb(255,255,0);rgb(255,0,0)"
                        dur="3s" repeatCount="indefinite" />
                </stop>
            </linearGradient>
        </defs>

        <!-- Animated path -->
        <path d="M10,150 Q250,50 490,150" stroke="url(#gradient1)" stroke-width="4" fill="none">
            <animate attributeName="d"
                values="M10,150 Q250,50 490,150;M10,150 Q250,250 490,150;M10,150 Q250,50 490,150"
                dur="2s" repeatCount="indefinite" />
        </path>

        <!-- Animated circle along path -->
        <circle r="10" fill="blue">
            <animateMotion dur="3s" repeatCount="indefinite">
                <mpath href="#motionPath" />
            </animateMotion>
        </circle>

        <!-- Moving text -->
        <text x="250" y="280" text-anchor="middle" font-size="20" fill="purple">
            SVG Animation!
            <animateTransform attributeName="transform"
                type="scale"
                values="1;1.5;1"
                dur="2s"
                repeatCount="indefinite" />
        </text>
    </svg>
    """

    # Encode SVG as base64
    svg_data = base64.b64encode(svg_animation.encode()).decode()

    fig_svg = go.Figure()
    fig_svg.add_layout_image(
        dict(
            source=f"data:image/svg+xml;base64,{svg_data}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=1, sizey=1,
            xanchor="center", yanchor="middle"
        )
    )
    fig_svg.update_layout(
        title="SVG Animation",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    register_plot(fig_svg, plot_id='svg_animation', metadata={
        'appearance': {'title': {'text': 'SVG Animation'}},
        'type': 'animation',
        'animation_type': 'svg',
        'svg_content': svg_animation
    })

    # ============================================
    # 6. DATA-DRIVEN ANIMATION WITH SLIDER
    # ============================================

    # Create time series data
    dates = pd.date_range('2024-01', periods=12, freq='M')
    categories = ['Sales', 'Marketing', 'Development', 'Support']

    # Create cumulative data
    data_frames = []
    for i in range(1, 13):
        values = np.cumsum(np.random.randn(4, i), axis=1)
        if i > 1:
            values[:, -1] = values[:, -2] + np.random.randn(4) * 5

        frame_data = []
        for j, cat in enumerate(categories):
            frame_data.append(go.Scatter(
                x=dates[:i],
                y=values[j] if i == 1 else values[j, :i],
                mode='lines+markers',
                name=cat
            ))

        data_frames.append(go.Frame(
            data=frame_data,
            name=f'Month_{i}'
        ))

    fig_timeline = go.Figure(
        data=[go.Scatter(x=[dates[0]], y=[0], mode='lines+markers', name=cat)
              for cat in categories],
        frames=data_frames
    )

    fig_timeline.update_layout(
        title="Time Series Animation",
        xaxis_title="Date",
        yaxis_title="Value",
        updatemenus=[{
            'type': 'buttons',
            'buttons': [
                {'label': 'Play', 'method': 'animate',
                 'args': [None, {'frame': {'duration': 500, 'redraw': True}}]},
                {'label': 'Pause', 'method': 'animate',
                 'args': [[None], {'frame': {'duration': 0}}]}
            ]
        }],
        sliders=[{
            'steps': [
                {
                    'args': [[f'Month_{i+1}']],
                    'label': dates[i].strftime('%b'),
                    'method': 'animate'
                } for i in range(12)
            ],
            'active': 0,
            'y': -0.1
        }]
    )

    register_plot(fig_timeline, plot_id='timeline_animation', metadata={
        'appearance': {'title': {'text': 'Time Series Animation'}},
        'type': 'animation',
        'animation_type': 'timeline'
    })

    return "Created 6 different animation types"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_animation_outputs()
    print(result)