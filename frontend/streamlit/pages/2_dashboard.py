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
from frontend.streamlit.components.charts import create_pie_chart, create_line_chart

# Page config
st.set_page_config(
    page_title="Dashboard - Expense AI",
    page_icon="📊",
    layout="wide"
)

# API URL
API_URL = f"http://{settings.api_host}:{settings.api_port}/api"

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Dashboard")
st.markdown("Overview of your expenses and spending patterns")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    
    # Date range
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    # Amount filter
    with st.expander("💰 Amount Filter"):
        amount_range = st.slider(
            "Amount Range ($)",
            min_value=0.0,
            max_value=1000.0,
            value=(0.0, 1000.0),
            step=10.0
        )
    
    # Category filter
    with st.expander("🏷️ Category Filter"):
        try:
            response = requests.get(f"{API_URL}/analytics/by-category")
            if response.status_code == 200:
                categories_data = response.json()["categories"]
                category_names = [cat["category_name"] for cat in categories_data]
                selected_categories = st.multiselect(
                    "Categories",
                    options=category_names,
                    default=category_names
                )
        except:
            selected_categories = []
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()


# Helper functions
def fetch_expenses(start_date=None, end_date=None):
    """Fetch expenses from API"""
    params = {}
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    
    try:
        response = requests.get(f"{API_URL}/expenses/", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


# Fetch data
with st.spinner("Loading data..."):
    if isinstance(date_range, tuple) and len(date_range) == 2:
        expenses = fetch_expenses(date_range[0], date_range[1])
    else:
        expenses = fetch_expenses(date_range, date_range)

if not expenses:
    st.info("📭 No expenses found for the selected period. Upload a receipt or add expenses manually!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Upload Receipt", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📤_Upload_Receipt.py")
    with col2:
        if st.button("➕ Add Expense Manually", use_container_width=True):
            st.switch_page("app.py")
else:
    df = pd.DataFrame(expenses)
    
    # Filter by amount
    df = df[(df['amount'] >= amount_range[0]) & (df['amount'] <= amount_range[1])]
    
    # Key Metrics
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = df['amount'].sum()
        st.metric("💰 Total Spent", f"${total:,.2f}")
    
    with col2:
        count = len(df)
        st.metric("📝 Transactions", count)
    
    with col3:
        avg = df['amount'].mean()
        st.metric("📊 Average", f"${avg:,.2f}")
    
    with col4:
        max_expense = df['amount'].max()
        st.metric("🔝 Largest", f"${max_expense:,.2f}")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Spending by Category")
        
        try:
            response = requests.get(
                f"{API_URL}/analytics/by-category",
                params={
                    "start_date": date_range[0].isoformat() if isinstance(date_range, tuple) else date_range.isoformat(),
                    "end_date": date_range[1].isoformat() if isinstance(date_range, tuple) and len(date_range) > 1 else date_range.isoformat()
                }
            )
            if response.status_code == 200:
                cat_data = response.json()["categories"]
                df_cat = pd.DataFrame(cat_data)
                
                if len(df_cat) > 0:
                    fig = px.pie(
                        df_cat,
                        values='total_amount',
                        names='category_name',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No category data available")
        except Exception as e:
            st.error(f"Error loading category data: {e}")
    
    with col2:
        st.markdown("### 📅 Daily Trend")
        
        df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
        daily.columns = ['date', 'amount']
        
        fig = px.line(
            daily,
            x='date',
            y='amount',
            markers=True
        )
        fig.update_traces(line_color='#1f77b4', line_width=3)
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top Merchants
    st.markdown("### 🏪 Top Merchants")
    
    top_merchants = df.groupby('merchant')['amount'].agg(['sum', 'count']).sort_values('sum', ascending=False).head(10)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            x=top_merchants.index,
            y=top_merchants['sum'],
            labels={'x': 'Merchant', 'y': 'Total Spent ($)'},
            color=top_merchants['sum'],
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Top 5 Merchants**")
        for i, (merchant, row) in enumerate(top_merchants.head(5).iterrows(), 1):
            st.markdown(f"""
            **{i}. {merchant}**  
            💰 ${row['sum']:.2f} ({row['count']} visits)
            """)
    
    st.markdown("---")
    
    # Recent Transactions
    st.markdown("### 📋 Recent Transactions")
    
    # Sort and display
    df_sorted = df.sort_values('date', ascending=False).head(20)
    
    # Format for display
    display_df = df_sorted[['date', 'merchant', 'amount', 'payment_method']].copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d %H:%M')
    display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
    display_df.columns = ['Date', 'Merchant', 'Amount', 'Payment Method']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export to CSV", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "expenses.csv",
                "text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/3_📈_Analytics.py")
    
    with col3:
        if st.button("🔮 View Predictions", use_container_width=True):
            st.switch_page("pages/4_🔮_Predictions.py")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
</div>
""", unsafe_allow_html=True)
