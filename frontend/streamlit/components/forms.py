"""
Form components for Streamlit frontend
"""
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional


def expense_form(categories: List[Dict], default_values: Optional[Dict] = None) -> Optional[Dict]:
    """
    Render expense input form
    
    Args:
        categories: List of available categories
        default_values: Default values for form fields
        
    Returns:
        Dictionary with form data if submitted, None otherwise
    """
    default_values = default_values or {}
    
    with st.form("expense_form", clear_on_submit=True):
        st.subheader("💰 Expense Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input(
                "Date",
                value=default_values.get('date', datetime.now()),
                help="Date of the expense"
            )
            
            merchant = st.text_input(
                "Merchant",
                value=default_values.get('merchant', ''),
                placeholder="e.g., Walmart, Amazon",
                help="Store or service provider"
            )
            
            amount = st.number_input(
                "Amount ($)",
                min_value=0.01,
                value=default_values.get('amount', 0.0),
                step=0.01,
                format="%.2f",
                help="Total amount spent"
            )
        
        with col2:
            # Category selection
            category_options = {
                f"{cat['icon']} {cat['name']}": cat['id'] 
                for cat in categories
            }
            
            default_category = None
            if 'category_id' in default_values:
                for label, cat_id in category_options.items():
                    if cat_id == default_values['category_id']:
                        default_category = label
                        break
            
            selected_category = st.selectbox(
                "Category",
                options=list(category_options.keys()),
                index=list(category_options.keys()).index(default_category) if default_category else 0,
                help="Expense category"
            )
            
            payment_method = st.selectbox(
                "Payment Method",
                options=["Cash", "Debit Card", "Credit Card", "Transfer", "PayPal", "Venmo", "Other"],
                index=["Cash", "Debit Card", "Credit Card", "Transfer", "PayPal", "Venmo", "Other"].index(
                    default_values.get('payment_method', 'Credit Card').replace('_', ' ').title()
                ) if 'payment_method' in default_values else 2,
                help="How you paid"
            )
            
            is_recurring = st.checkbox(
                "Recurring expense",
                value=default_values.get('is_recurring', False),
                help="Check if this is a regular recurring expense"
            )
        
        description = st.text_area(
            "Description (optional)",
            value=default_values.get('description', ''),
            placeholder="Additional details about this expense...",
            help="Any additional information"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            submitted = st.form_submit_button(
                "💾 Save Expense",
                type="primary",
                use_container_width=True
            )
        with col3:
            cancelled = st.form_submit_button(
                "❌ Cancel",
                use_container_width=True
            )
        
        if submitted:
            if amount <= 0:
                st.error("⚠️ Amount must be greater than 0")
                return None
            
            return {
                "date": datetime.combine(date, datetime.min.time()).isoformat(),
                "merchant": merchant.strip(),
                "category_id": category_options[selected_category],
                "amount": amount,
                "description": description.strip(),
                "payment_method": payment_method.lower().replace(" ", "_"),
                "is_recurring": is_recurring,
                "source": "manual"
            }
        
        if cancelled:
            return {"cancelled": True}
    
    return None


def budget_form(categories: List[Dict], default_values: Optional[Dict] = None) -> Optional[Dict]:
    """
    Render budget configuration form
    
    Args:
        categories: List of available categories
        default_values: Default values for form fields
        
    Returns:
        Dictionary with form data if submitted, None otherwise
    """
    default_values = default_values or {}
    
    with st.form("budget_form", clear_on_submit=True):
        st.subheader("🎯 Budget Configuration")
        
        # Category selection
        category_options = {
            f"{cat['icon']} {cat['name']}": cat['id'] 
            for cat in categories
        }
        
        selected_category = st.selectbox(
            "Category",
            options=list(category_options.keys()),
            help="Select category to set budget for"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            month = st.date_input(
                "Month",
                value=default_values.get('month', datetime.now()),
                help="Month for this budget"
            )
            
            amount_limit = st.number_input(
                "Budget Limit ($)",
                min_value=1.0,
                value=default_values.get('amount_limit', 100.0),
                step=10.0,
                format="%.2f",
                help="Maximum amount for this category"
            )
        
        with col2:
            alert_threshold = st.slider(
                "Alert Threshold (%)",
                min_value=50,
                max_value=100,
                value=int(default_values.get('alert_threshold', 80) * 100),
                step=5,
                help="Get notified when spending reaches this percentage"
            )
        
        submitted = st.form_submit_button(
            "💾 Save Budget",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            return {
                "category_id": category_options[selected_category],
                "month": datetime(month.year, month.month, 1).isoformat(),
                "amount_limit": amount_limit,
                "alert_threshold": alert_threshold / 100
            }
    
    return None


def filter_form() -> Dict:
    """
    Render filter form for expenses
    
    Returns:
        Dictionary with filter parameters
    """
    with st.expander("🔍 Filters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            date_range = st.date_input(
                "Date Range",
                value=(
                    datetime.now().replace(day=1),
                    datetime.now()
                ),
                help="Filter by date range"
            )
            
            amount_range = st.slider(
                "Amount Range ($)",
                min_value=0.0,
                max_value=1000.0,
                value=(0.0, 1000.0),
                step=10.0,
                help="Filter by amount range"
            )
        
        with col2:
            categories = st.multiselect(
                "Categories",
                options=["Food", "Transportation", "Shopping", "Health", "Entertainment", "Other"],
                help="Filter by categories"
            )
            
            payment_methods = st.multiselect(
                "Payment Methods",
                options=["Cash", "Debit Card", "Credit Card", "Transfer", "PayPal", "Venmo"],
                help="Filter by payment method"
            )
        
        search = st.text_input(
            "🔎 Search",
            placeholder="Search merchant or description...",
            help="Search in merchant name or description"
        )
        
        return {
            "start_date": date_range[0] if isinstance(date_range, tuple) else date_range,
            "end_date": date_range[1] if isinstance(date_range, tuple) and len(date_range) > 1 else date_range,
            "min_amount": amount_range[0],
            "max_amount": amount_range[1],
            "categories": categories,
            "payment_methods": payment_methods,
            "search": search
        }


def confirm_dialog(title: str, message: str, confirm_text: str = "Confirm", cancel_text: str = "Cancel") -> bool:
    """
    Display confirmation dialog
    
    Args:
        title: Dialog title
        message: Dialog message
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        
    Returns:
        True if confirmed, False otherwise
    """
    st.warning(f"**{title}**")
    st.write(message)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(confirm_text, type="primary", use_container_width=True):
            return True
    
    with col2:
        if st.button(cancel_text, use_container_width=True):
            return False
    
    return False


def success_message(message: str, icon: str = "✅"):
    """Display success message"""
    st.markdown(f"""
    <div style='
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.25rem;
        margin: 1rem 0;
    '>
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)


def error_message(message: str, icon: str = "❌"):
    """Display error message"""
    st.markdown(f"""
    <div style='
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 0.25rem;
        margin: 1rem 0;
    '>
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)


def info_message(message: str, icon: str = "ℹ️"):
    """Display info message"""
    st.markdown(f"""
    <div style='
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #0c5460;
        border-radius: 0.25rem;
        margin: 1rem 0;
    '>
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)
