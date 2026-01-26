import streamlit as st
import requests
from pathlib import Path
import sys

# Add root directory to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from backend.config.settings import settings

# Page config
st.set_page_config(
    page_title="Upload Receipt - Expense AI",
    page_icon="📤",
    layout="wide"
)

# API URL
API_URL = f"http://{settings.api_host}:{settings.api_port}/api"

# Custom CSS
st.markdown("""
<style>
    .upload-box {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f0f8ff;
    }
    .result-box {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📤 Upload Receipt")
st.markdown("Upload a photo or PDF of your receipt and let AI extract the information automatically.")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📷 Upload Your Receipt")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["jpg", "jpeg", "png", "pdf"],
        help="Supported formats: JPG, PNG, PDF (Max 10MB)",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Show file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        
        with st.expander("📄 File Details", expanded=False):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        # Display preview if image
        if uploaded_file.type.startswith("image"):
            st.image(uploaded_file, caption="Receipt Preview", use_column_width=True)
        
        st.markdown("---")
        
        # Processing options
        st.markdown("### ⚙️ Processing Options")
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            auto_save = st.checkbox(
                "💾 Save automatically",
                value=True,
                help="Automatically save the expense after processing"
            )
        
        with col_opt2:
            show_raw_data = st.checkbox(
                "🔍 Show raw OCR data",
                value=False,
                help="Display raw OCR extraction details"
            )
        
        # Process button
        if st.button("🚀 Process Receipt", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing receipt... This may take a few seconds."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Prepare request
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    data = {"auto_save": str(auto_save).lower()}
                    
                    # Send to API
                    response = requests.post(
                        f"{API_URL}/upload/receipt",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result["success"]:
                            st.success("✅ Receipt processed successfully!")
                            
                            ocr_data = result["ocr_result"]
                            
                            # Display results
                            st.markdown("### 📊 Extracted Information")
                            
                            # Create result columns
                            res_col1, res_col2, res_col3 = st.columns(3)
                            
                            with res_col1:
                                st.metric(
                                    "📅 Date",
                                    ocr_data.get("date", "Not detected") if ocr_data.get("date") else "Not detected"
                                )
                            
                            with res_col2:
                                st.metric(
                                    "🏪 Merchant",
                                    ocr_data.get("merchant", "Not detected") or "Not detected"
                                )
                            
                            with res_col3:
                                amount = ocr_data.get("amount", 0)
                                st.metric(
                                    "💰 Total",
                                    f"${amount:.2f}" if amount else "$0.00"
                                )
                            
                            # Confidence
                            confidence = ocr_data.get("confidence", 0)
                            st.progress(confidence, text=f"Confidence: {confidence*100:.1f}%")
                            
                            # Category suggestion
                            if ocr_data.get("category_id"):
                                st.info(f"💡 Suggested Category: **{ocr_data.get('category_name', 'Unknown')}**")
                            
                            # Show save status
                            if auto_save and result.get("expense_id"):
                                st.success(f"✅ Expense saved with ID: **{result['expense_id']}**")
                                
                                # Action buttons
                                col_action1, col_action2 = st.columns(2)
                                with col_action1:
                                    if st.button("📊 View in Dashboard", use_container_width=True):
                                        st.switch_page("pages/2_📊_Dashboard.py")
                                with col_action2:
                                    if st.button("➕ Add Another", use_container_width=True):
                                        st.rerun()
                            
                            # Raw OCR data
                            if show_raw_data:
                                with st.expander("🔍 Raw OCR Data", expanded=False):
                                    st.json(ocr_data)
                        
                        else:
                            st.error(f"❌ {result.get('message', 'Error processing receipt')}")
                    
                    else:
                        st.error(f"❌ Server error: {response.status_code}")
                        st.write(response.text)
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

with col2:
    # Tips and information
    st.markdown("### 💡 Tips for Best Results")
    
    st.markdown("""
    <div class="info-box">
    <h4>📸 Photo Quality</h4>
    <ul>
        <li>Take photos in good lighting</li>
        <li>Keep the receipt flat</li>
        <li>Avoid shadows and glare</li>
        <li>Ensure text is readable</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h4>🎯 What We Extract</h4>
    <ul>
        <li>📅 Date of purchase</li>
        <li>🏪 Merchant/Store name</li>
        <li>💰 Total amount</li>
        <li>🏷️ Suggested category</li>
        <li>📝 Line items (when clear)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Supported formats
    st.info("""
    **📋 Supported Formats:**
    - JPG, JPEG
    - PNG
    - PDF
    
    **📏 Size Limit:** 10MB
    """)
    
    # Quick stats
    st.markdown("---")
    st.markdown("### 📈 Quick Stats")
    
    try:
        # Fetch recent uploads count
        response = requests.get(f"{API_URL}/expenses/summary/total")
        if response.status_code == 200:
            data = response.json()
            
            st.metric("Total Expenses", data.get("total_count", 0))
            st.metric("Total Amount", f"${data.get('total_amount', 0):,.2f}")
    except:
        pass

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>🔒 Your data is secure and encrypted</p>
    <p>Need help? Check our <a href='#'>FAQ</a> or <a href='#'>Contact Support</a></p>
</div>
""", unsafe_allow_html=True)
