import plotly.graph_objects as go
from typing import List

def render_gauge_chart(score: float, title: str, color_hex: str = "#6366f1") -> go.Figure:
    """Creates a premium, minimal Plotly gauge chart styled for obsidian dark dashboards."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 18, 'family': 'Outfit, sans-serif', 'color': '#94a3b8'}},
        number={'font': {'size': 38, 'family': 'Outfit, sans-serif', 'color': '#ffffff'}, 'suffix': '/100'},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#334155'},
            'bar': {'color': color_hex, 'thickness': 0.28},
            'bgcolor': 'rgba(255, 255, 255, 0.02)',
            'borderwidth': 1,
            'bordercolor': 'rgba(255, 255, 255, 0.08)',
            'steps': [
                {'range': [0, 30], 'color': 'rgba(239, 68, 68, 0.05)'},
                {'range': [30, 70], 'color': 'rgba(245, 158, 11, 0.05)'},
                {'range': [70, 100], 'color': 'rgba(16, 185, 129, 0.05)'}
            ],
            'threshold': {
                'line': {'color': color_hex, 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=220,
    )
    
    return fig

def render_growth_timeline(historical: List[int], predicted: List[int]) -> go.Figure:
    """Renders an elegant historical and forecasted follower growth line chart with filled overlays."""
    # Build indexing arrays
    x_hist = [f"D-{30 - i}" for i in range(len(historical))]
    x_pred = [f"D+{i + 1}" for i in range(len(predicted))]
    
    # We stitch the last historical day to the first predicted day to make a continuous line
    x_pred_combined = [x_hist[-1]] + x_pred
    predicted_combined = [historical[-1]] + predicted
    
    fig = go.Figure()
    
    # Historical Trace
    fig.add_trace(go.Scatter(
        x=x_hist,
        y=historical,
        mode='lines+markers',
        name='Historical Followers',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=5, color='#818cf8'),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.04)'
    ))
    
    # Forecasted Trace (Prophet)
    fig.add_trace(go.Scatter(
        x=x_pred_combined,
        y=predicted_combined,
        mode='lines',
        name='30-Day Prophet Forecast',
        line=dict(color='#f43f5e', width=3, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(244, 63, 94, 0.02)'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=20, t=20, b=20),
        height=320,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='#94a3b8')
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(color='#64748b'),
            showticklabels=True,
            nticks=10
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(color='#64748b'),
            tickformat=","
        )
    )
    
    return fig
