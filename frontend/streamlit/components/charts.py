"""
Chart components for Streamlit frontend
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict
import streamlit as st


def create_pie_chart(data: pd.DataFrame, values: str, names: str, title: str = ""):
    """
    Create a pie chart
    
    Args:
        data: DataFrame with data
        values: Column name for values
        names: Column name for labels
        title: Chart title
    """
    fig = px.pie(
        data,
        values=values,
        names=names,
        title=title,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig


def create_line_chart(data: pd.DataFrame, x: str, y: str, title: str = ""):
    """
    Create a line chart for trends
    
    Args:
        data: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis
        title: Chart title
    """
    fig = px.line(
        data,
        x=x,
        y=y,
        title=title,
        markers=True
    )
    
    fig.update_traces(
        line_color='#1f77b4',
        line_width=3,
        marker=dict(size=8)
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    
    return fig


def create_bar_chart(data: pd.DataFrame, x: str, y: str, title: str = "", color: str = None):
    """
    Create a bar chart
    
    Args:
        data: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis
        title: Chart title
        color: Column for color grouping
    """
    fig = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        color=color,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_layout(
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title(),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    
    return fig


def create_category_comparison_chart(categories_data: List[Dict]):
    """
    Create comparison chart for categories
    
    Args:
        categories_data: List of category dictionaries
    """
    df = pd.DataFrame(categories_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Total Amount',
        x=df['category_name'],
        y=df['total_amount'],
        text=df['total_amount'].apply(lambda x: f'${x:.2f}'),
        textposition='outside',
        marker_color='#4CAF50'
    ))
    
    fig.update_layout(
        title='Spending by Category',
        xaxis_title='Category',
        yaxis_title='Amount ($)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
        showlegend=False
    )
    
    return fig


def create_monthly_trend_chart(monthly_data: List[Dict]):
    """
    Create monthly trend chart
    
    Args:
        monthly_data: List of monthly data dictionaries
    """
    df = pd.DataFrame(monthly_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['month_name'],
        y=df['total'],
        mode='lines+markers',
        name='Total',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=10),
        fill='tonexty',
        fillcolor='rgba(33, 150, 243, 0.1)'
    ))
    
    fig.update_layout(
        title='Monthly Spending Trend',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    
    return fig


def create_gauge_chart(current: float, limit: float, title: str = "Budget Usage"):
    """
    Create gauge chart for budget tracking
    
    Args:
        current: Current spending
        limit: Budget limit
        title: Chart title
    """
    percentage = (current / limit * 100) if limit > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 80},  # Alert threshold
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "orange"},
                {'range': [100, 150], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig


def create_heatmap(data: pd.DataFrame, x: str, y: str, values: str, title: str = ""):
    """
    Create heatmap
    
    Args:
        data: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis
        values: Column for values
        title: Chart title
    """
    pivot_data = data.pivot(index=y, columns=x, values=values)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Blues',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title()
    )
    
    return fig


def display_metric_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """
    Display a metric card
    
    Args:
        label: Metric label
        value: Metric value
        delta: Change indicator
        icon: Icon to display
    """
    st.markdown(f"""
    <div style='
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    '>
        <div style='font-size: 2rem;'>{icon}</div>
        <div style='font-size: 0.875rem; color: #666; margin-top: 0.5rem;'>{label}</div>
        <div style='font-size: 1.75rem; font-weight: bold; margin-top: 0.25rem;'>{value}</div>
        {f"<div style='font-size: 0.875rem; color: {'green' if '+' in str(delta) else 'red'}; margin-top: 0.25rem;'>{delta}</div>" if delta else ""}
    </div>
    """, unsafe_allow_html=True)
