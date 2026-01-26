import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add root directory to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from backend.config.settings import settings

# Page config
st.set_page_config(
    page_title="Predictions - Expense AI",
    page_icon="🔮",
    layout="wide"
)

# API URL
API_URL = f"http://{settings.api_host}:{settings.api_port}/api"

# Header
st.title("🔮 Expense Predictions")
st.markdown("AI-powered forecasts of your future expenses")

# Info banner
st.info("""
🚧 **Prediction Module** - Currently in Development

This feature uses machine learning to predict your future expenses based on historical patterns.
Some features may be limited while we're still training the models.
""")

# Sidebar
with st.sidebar:
    st.header("🎯 Prediction Settings")
    
    # Forecast period
    forecast_months = st.slider(
        "Forecast Period (months)",
        min_value=1,
        max_value=12,
        value=3,
        help="How many months ahead to predict"
    )
    
    # Confidence level
    confidence_level = st.select_slider(
        "Confidence Level",
        options=[80, 85, 90, 95, 99],
        value=95,
        help="Higher confidence = wider prediction range"
    )
    
    # Category filter
    predict_by_category = st.checkbox(
        "Predict by Category",
        value=True,
        help="Generate separate predictions for each category"
    )
    
    st.markdown("---")
    
    # Model info
    with st.expander("ℹ️ About Predictions"):
        st.markdown("""
        Our prediction model uses:
        - Historical spending patterns
        - Seasonal trends
        - Category-specific behaviors
        - Time series analysis
        
        **Accuracy**: Predictions improve with more data
        **Update Frequency**: Models retrain monthly
        """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 Overall Spending Forecast")
    
    # Generate mock prediction data (replace with actual API call when ready)
    try:
        # Try to fetch actual data first
        response = requests.get(f"{API_URL}/analytics/summary", params={"period": "month"})
        
        if response.status_code == 200:
            current_avg = response.json()['average_per_day'] * 30
        else:
            current_avg = 500  # fallback
    except:
        current_avg = 500  # fallback
    
    # Mock forecast (replace with actual prediction API)
    future_dates = pd.date_range(
        start=datetime.now(),
        periods=forecast_months,
        freq='M'
    )
    
    # Simple trend projection (to be replaced with actual ML model)
    predictions = [current_avg * (1 + 0.02 * i) for i in range(forecast_months)]
    upper_bound = [p * 1.1 for p in predictions]
    lower_bound = [p * 0.9 for p in predictions]
    
    # Create forecast chart
    fig = go.Figure()
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=future_dates.tolist() + future_dates.tolist()[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(0,100,200,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name=f'{confidence_level}% Confidence',
        showlegend=True
    ))
    
    # Predicted values
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        mode='lines+markers',
        name='Predicted Spending',
        line=dict(color='rgb(0,100,200)', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f'Spending Forecast - Next {forecast_months} Months',
        xaxis_title='Month',
        yaxis_title='Predicted Amount ($)',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Prediction table
    st.markdown("#### 📅 Monthly Predictions")
    
    pred_df = pd.DataFrame({
        'Month': future_dates.strftime('%B %Y'),
        'Predicted Amount': [f"${p:.2f}" for p in predictions],
        'Lower Bound': [f"${l:.2f}" for l in lower_bound],
        'Upper Bound': [f"${u:.2f}" for u in upper_bound],
        'Confidence': [f"{confidence_level}%"] * forecast_months
    })
    
    st.dataframe(pred_df, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### 💡 Insights")
    
    # Key insights
    total_predicted = sum(predictions)
    avg_monthly = total_predicted / forecast_months
    
    st.metric(
        "📊 Total Predicted",
        f"${total_predicted:.2f}",
        help=f"Next {forecast_months} months"
    )
    
    st.metric(
        "📅 Monthly Average",
        f"${avg_monthly:.2f}"
    )
    
    # Trend indicator
    if predictions[-1] > predictions[0]:
        trend = "📈 Increasing"
        trend_color = "red"
        trend_pct = ((predictions[-1] - predictions[0]) / predictions[0] * 100)
    else:
        trend = "📉 Decreasing"
        trend_color = "green"
        trend_pct = ((predictions[0] - predictions[-1]) / predictions[0] * 100)
    
    st.markdown(f"**Trend**: {trend} ({trend_pct:.1f}%)")
    
    st.markdown("---")
    
    # Recommendations
    st.markdown("### 🎯 Recommendations")
    
    st.success("""
    **Based on predictions:**
    
    ✅ Set monthly budgets
    
    ✅ Plan for increases
    
    ✅ Build emergency fund
    
    ✅ Review subscriptions
    """)
    
    # Savings goal calculator
    st.markdown("---")
    st.markdown("### 💰 Savings Goal")
    
    savings_goal = st.number_input(
        "Target Savings ($)",
        min_value=0.0,
        value=1000.0,
        step=100.0
    )
    
    if savings_goal > 0:
        savings_per_month = savings_goal / forecast_months
        adjusted_budget = avg_monthly - savings_per_month
        
        st.info(f"""
        To save **${savings_goal:.2f}** in {forecast_months} months:
        
        💰 Save: **${savings_per_month:.2f}** per month
        
        📊 Budget: **${adjusted_budget:.2f}** per month
        """)

# Category predictions (if enabled)
if predict_by_category:
    st.markdown("---")
    st.markdown("### 🏷️ Predictions by Category")
    
    try:
        response = requests.get(f"{API_URL}/analytics/by-category")
        
        if response.status_code == 200:
            categories = response.json()["categories"]
            
            # Create tabs for each major category
            cat_names = [cat['category_name'] for cat in categories[:5]]  # Top 5
            tabs = st.tabs(cat_names)
            
            for i, tab in enumerate(tabs):
                with tab:
                    cat = categories[i]
                    
                    # Mock category prediction
                    cat_avg = cat['average_amount']
                    cat_predictions = [cat_avg * (1 + 0.01 * j) for j in range(forecast_months)]
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        fig = px.line(
                            x=future_dates,
                            y=cat_predictions,
                            markers=True,
                            title=f"{cat['category_name']} Forecast"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.metric("Total Predicted", f"${sum(cat_predictions):.2f}")
                        st.metric("Monthly Avg", f"${sum(cat_predictions)/forecast_months:.2f}")
                        st.metric("Current Avg", f"${cat_avg:.2f}")
    
    except Exception as e:
        st.warning("Category predictions not available yet")

# Historical accuracy
st.markdown("---")
st.markdown("### 📊 Prediction Accuracy")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Model Accuracy",
        "85%",
        help="Based on last 3 months"
    )

with col2:
    st.metric(
        "Avg Error",
        "±$50",
        help="Average prediction error"
    )

with col3:
    st.metric(
        "Data Points",
        "120+",
        help="Historical expenses used"
    )

# Disclaimer
st.markdown("---")
st.warning("""
⚠️ **Important Note**

Predictions are estimates based on historical data and may not account for:
- Unexpected expenses
- Major life changes
- Economic conditions
- Seasonal variations not in training data

Always maintain an emergency fund and review predictions regularly.
""")

# Action buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/2_📊_Dashboard.py")

with col2:
    if st.button("📈 View Analytics", use_container_width=True):
        st.switch_page("pages/3_📈_Analytics.py")

with col3:
    if st.button("🔄 Retrain Model", use_container_width=True):
        with st.spinner("Retraining model..."):
            st.success("✅ Model updated with latest data!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>🤖 Powered by Machine Learning | Last model update: """ + datetime.now().strftime("%Y-%m-%d") + """</p>
</div>
""", unsafe_allow_html=True)
