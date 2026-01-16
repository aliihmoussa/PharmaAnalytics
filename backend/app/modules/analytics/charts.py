"""Chart generation using Plotly and Seaborn."""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import polars as pl
import logging

logger = logging.getLogger(__name__)


def create_top_drugs_chart(data: List[Dict], limit: int = 10) -> go.Figure:
    """
    Create bar chart for top dispensed drugs.
    
    Args:
        data: List of dictionaries with drug information
        limit: Number of drugs to display
    
    Returns:
        Plotly figure
    """
    if not data:
        return go.Figure()
    
    # Prepare data
    drugs = data[:limit]
    drug_names = [d.get('drug_name', d.get('ARTICLE', '')) for d in drugs]
    quantities = [abs(d.get('quantity', d.get('QTY', 0))) for d in drugs]
    
    fig = go.Figure(data=[
        go.Bar(
            x=drug_names,
            y=quantities,
            marker_color='steelblue',
            text=[f"{q:,}" for q in quantities],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='Top Dispensed Drugs',
        xaxis_title='Drug Name',
        yaxis_title='Quantity Dispensed',
        height=500
    )
    
    return fig


def create_demand_trend_chart(data: List[Dict], date_column: str = 'date') -> go.Figure:
    """
    Create time-series line chart for drug demand.
    
    Args:
        data: List of dictionaries with time-series data
        date_column: Name of date column
    
    Returns:
        Plotly figure
    """
    if not data:
        return go.Figure()
    
    dates = [d.get(date_column) for d in data]
    quantities = [d.get('quantity', 0) for d in data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=quantities,
        mode='lines+markers',
        name='Demand',
        line=dict(color='royalblue', width=2)
    ))
    
    fig.update_layout(
        title='Drug Demand Trends Over Time',
        xaxis_title='Date',
        yaxis_title='Quantity Dispensed',
        height=500,
        hovermode='x unified'
    )
    
    return fig


def create_seasonal_heatmap(data: List[Dict]) -> go.Figure:
    """
    Create heatmap for seasonal patterns.
    
    Args:
        data: List of dictionaries with monthly/yearly data
    
    Returns:
        Plotly figure
    """
    if not data:
        return go.Figure()
    
    # Prepare data for heatmap
    # Assuming data has 'month', 'year', 'quantity' keys
    import pandas as pd
    
    df = pd.DataFrame(data)
    if 'month' in df.columns and 'year' in df.columns:
        pivot = df.pivot(index='year', columns='month', values='quantity')
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='Viridis',
            text=pivot.values,
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='Seasonal Demand Patterns',
            xaxis_title='Month',
            yaxis_title='Year',
            height=500
        )
    
    return fig


def create_department_comparison_chart(data: List[Dict]) -> go.Figure:
    """
    Create bar chart comparing department performance.
    
    Args:
        data: List of dictionaries with department metrics
    
    Returns:
        Plotly figure
    """
    if not data:
        return go.Figure()
    
    dept_ids = [str(d.get('department_id', d.get('C.R', ''))) for d in data]
    quantities = [d.get('total_dispensed', 0) for d in data]
    
    fig = go.Figure(data=[
        go.Bar(
            x=dept_ids,
            y=quantities,
            marker_color='coral',
            text=[f"{q:,}" for q in quantities],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='Department Performance Comparison',
        xaxis_title='Department ID',
        yaxis_title='Total Dispensed',
        height=500
    )
    
    return fig


def export_chart_html(fig: go.Figure, filepath: str):
    """Export chart as HTML file."""
    fig.write_html(filepath)
    logger.info(f"Chart exported to {filepath}")


def export_chart_image(fig: go.Figure, filepath: str, format: str = 'png'):
    """Export chart as image (PNG/SVG)."""
    if format == 'png':
        fig.write_image(filepath, format='png', width=1200, height=600)
    elif format == 'svg':
        fig.write_image(filepath, format='svg')
    logger.info(f"Chart exported to {filepath}")

