"""Chart styling and theme configuration."""

from typing import Dict
import plotly.graph_objects as go

# Default color palette
COLOR_PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'accent': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd'
}

# Arabic font configuration (if needed)
ARABIC_FONTS = {
    'family': 'Arial, "DejaVu Sans", sans-serif',
    'size': 12
}

# Default layout template
DEFAULT_LAYOUT = {
    'font': ARABIC_FONTS,
    'title_font_size': 18,
    'xaxis_title_font_size': 14,
    'yaxis_title_font_size': 14,
    'plot_bgcolor': 'white',
    'paper_bgcolor': 'white',
    'margin': dict(l=50, r=50, t=80, b=50)
}


def apply_theme(fig: go.Figure, theme: str = 'default') -> go.Figure:
    """
    Apply theme to Plotly figure.
    
    Args:
        fig: Plotly figure
        theme: Theme name ('default', 'dark', etc.)
    
    Returns:
        Updated figure
    """
    if theme == 'default':
        fig.update_layout(**DEFAULT_LAYOUT)
    elif theme == 'dark':
        fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font_color='white'
        )
    
    return fig

