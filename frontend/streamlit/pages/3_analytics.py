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
    page_title="Analytics - Expense AI",
    page_icon="📈",
    layout="wide"
)

# API URL
API_URL = f"http://{settings.api_host}:{settings.api_port}/api"

# Header
st.title("📈 Advanced Analytics")
st.markdown("Deep insights into your spending patterns and trends")

# Sidebar
with st.sidebar:
    st.header("⚙️ Analysis Settings")
    
    # Period selection
    period = st.selectbox(
        "Analysis Period",
        options=["Week", "Month", "Quarter", "Year"],
        index=1
    )
    
    period_map = {
        "Week": "week",
        "Month": "month",
        "Quarter": "quarter",
        "Year": "year"
    }
    
    # Comparison
    show_comparison = st.checkbox("📊 Show Period Comparison", value=True)
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        show_trends = st.checkbox("📈 Show Trends", value=True)
        show_anomalies = st.checkbox("⚠️ Detect Anomalies", value=True)
        show_predictions = st.checkbox("🔮 Show Predictions", value=False)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📅 Time Analysis", "🏷️ Categories", "🔍 Insights"])

with tab1:
    st.markdown("### 📊 Spending Overview")
    
    # Fetch summary
    try:
        response = requests.get(
            f"{API_URL}/analytics/summary",
            params={"period": period_map[period]}
        )
        
        if response.status_code == 200:
            summary = response.json()
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Total Expenses",
                    f"${summary['total_expenses']:,.2f}"
                )
            
            with col2:
                st.metric(
                    "📝 Transactions",
                    f"{summary['total_transactions']}"
                )
            
            with col3:
                st.metric(
                    "📊 Avg per Transaction",
                    f"${summary.get('average_per_transaction', 0):,.2f}"
                )
            
            with col4:
                st.metric(
                    "📅 Avg per Day",
                    f"${summary['average_per_day']:,.2f}"
                )
            
            st.markdown("---")
            
            # Category breakdown
            st.markdown("### 🎯 Spending Breakdown")
            
            response_cat = requests.get(f"{API_URL}/analytics/by-category")
            if response_cat.status_code == 200:
                cat_data = response_cat.json()["categories"]
                df_cat = pd.DataFrame(cat_data)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Pie chart
                    fig = px.pie(
                        df_cat,
                        values='total_amount',
                        names='category_name',
                        title='Spending Distribution',
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Bar chart
                    fig = px.bar(
                        df_cat.sort_values('total_amount', ascending=True).tail(10),
                        x='total_amount',
                        y='category_name',
                        orientation='h',
                        title='Top Categories',
                        labels={'total_amount': 'Amount ($)', 'category_name': 'Category'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading data: {e}")

with tab2:
    st.markdown("### 📅 Time-based Analysis")
    
    try:
        # Trends
        response = requests.get(
            f"{API_URL}/analytics/trends",
            params={"period": period_map[period], "group_by": "day"}
        )
        
        if response.status_code == 200:
            trends = response.json()
            df_trends = pd.DataFrame(trends)
            
            if len(df_trends) > 0:
                # Line chart
                fig = px.line(
                    df_trends,
                    x='date',
                    y='total',
                    title=f'Spending Trend ({period})',
                    markers=True,
                    labels={'date': 'Date', 'total': 'Amount ($)'}
                )
                fig.update_traces(line_color='#1f77b4', line_width=3)
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📈 Highest Day", f"${df_trends['total'].max():,.2f}")
                
                with col2:
                    st.metric("📉 Lowest Day", f"${df_trends['total'].min():,.2f}")
                
                with col3:
                    st.metric("📊 Average Day", f"${df_trends['total'].mean():,.2f}")
        
        # Monthly comparison
        if show_comparison:
            st.markdown("---")
            st.markdown("### 📊 Monthly Comparison")
            
            response = requests.get(
                f"{API_URL}/analytics/monthly-comparison",
                params={"months": 6}
            )
            
            if response.status_code == 200:
                monthly = response.json()
                df_monthly = pd.DataFrame(monthly)
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=df_monthly['month_name'],
                    y=df_monthly['total'],
                    name='Total Spending',
                    marker_color='lightblue'
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_monthly['month_name'],
                    y=df_monthly['count'],
                    name='Transaction Count',
                    yaxis='y2',
                    line=dict(color='red', width=2)
                ))
                
                fig.update_layout(
                    title='Monthly Comparison',
                    xaxis_title='Month',
                    yaxis_title='Total Amount ($)',
                    yaxis2=dict(
                        title='Transactions',
                        overlaying='y',
                        side='right'
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading trends: {e}")

with tab3:
    st.markdown("### 🏷️ Category Deep Dive")
    
    try:
        response = requests.get(f"{API_URL}/analytics/by-category")
        
        if response.status_code == 200:
            cat_data = response.json()["categories"]
            df_cat = pd.DataFrame(cat_data)
            
            # Category selector
            selected_category = st.selectbox(
                "Select Category",
                options=df_cat['category_name'].tolist()
            )
            
            cat_info = df_cat[df_cat['category_name'] == selected_category].iloc[0]
            
            # Category metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Total", f"${cat_info['total_amount']:,.2f}")
            
            with col2:
                st.metric("📝 Count", cat_info['transaction_count'])
            
            with col3:
                st.metric("📊 Average", f"${cat_info['average_amount']:,.2f}")
            
            with col4:
                st.metric("📈 % of Total", f"{cat_info['percentage']:.1f}%")
            
            st.markdown("---")
            
            # Detailed table
            st.markdown("#### 📋 All Categories")
            
            display_df = df_cat[['category_name', 'total_amount', 'transaction_count', 'average_amount', 'percentage']].copy()
            display_df.columns = ['Category', 'Total ($)', 'Count', 'Average ($)', '%']
            display_df = display_df.sort_values('Total ($)', ascending=False)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
    
    except Exception as e:
        st.error(f"Error loading categories: {e}")

with tab4:
    st.markdown("### 🔍 Insights & Recommendations")
    
    try:
        # Get statistics
        response = requests.get(f"{API_URL}/analytics/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            
            st.markdown("#### 💡 Key Findings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **📊 Spending Pattern**
                - Total Expenses: {stats['total_expenses']}
                - Average per Expense: ${stats['average_expense']:.2f}
                - Largest Expense: ${stats['max_expense']:.2f}
                """)
            
            with col2:
                st.success(f"""
                **🎯 Category Insights**
                - Most Frequent: {stats.get('favorite_category', 'N/A')}
                - This Month: ${stats['this_month_total']:,.2f}
                """)
            
            # Anomalies
            if show_anomalies:
                st.markdown("---")
                st.markdown("#### ⚠️ Unusual Expenses")
                
                response_anom = requests.get(f"{API_URL}/analytics/anomalies")
                
                if response_anom.status_code == 200:
                    anomalies = response_anom.json()
                    
                    if len(anomalies) > 0:
                        df_anom = pd.DataFrame(anomalies)
                        
                        st.warning(f"Found {len(anomalies)} unusual expenses")
                        
                        display_anom = df_anom[['date', 'merchant', 'amount', 'category']].head(10)
                        display_anom['date'] = pd.to_datetime(display_anom['date']).dt.strftime('%Y-%m-%d')
                        display_anom['amount'] = display_anom['amount'].apply(lambda x: f"${x:.2f}")
                        
                        st.dataframe(display_anom, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ No unusual expenses detected")
            
            # Recommendations
            st.markdown("---")
            st.markdown("#### 💡 Recommendations")
            
            st.markdown("""
            **Based on your spending patterns:**
            
            1. 🎯 **Budget Optimization**: Consider setting monthly limits for your top spending categories
            2. 📊 **Track Trends**: Monitor your spending patterns to identify potential savings
            3. ⚠️ **Review Anomalies**: Check unusual expenses for potential errors or fraudulent charges
            4. 💰 **Saving Opportunity**: Look for ways to reduce spending in high-expense categories
            """)
    
    except Exception as e:
        st.error(f"Error loading insights: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 Want more detailed analysis? Try our prediction feature!</p>
</div>
""", unsafe_allow_html=True)
