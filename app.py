import streamlit as st
import pandas as pd
import numpy as np
import time
from streamlit_option_menu import option_menu

# Set page config
st.set_page_config(
    page_title="Excellent Mirror - HCL Tech Hackathon",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("public/assets/css/style.css")

# -----------------
# Header Navigation
# -----------------
selected = option_menu(
    menu_title=None,
    options=["Home", "Dashboard", "Predictions", "About End-to-End"],
    icons=["house", "bar-chart", "graph-up-arrow", "info-circle"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f0f8ff"},
        "icon": {"color": "#00bfff", "font-size": "18px"}, 
        "nav-link": {"font-family": "Poppins", "font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#e0f7fa"},
        "nav-link-selected": {"background-color": "#00bfff"},
    }
)

# -----------------
# Page Logic
# -----------------

if selected == "Home":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("public/assets/images/team.png", use_container_width=True)
    
    st.title("Excellent Mirror 🔮")
    st.subheader("Advanced AI Solution | HCL Tech Hackathon")
    
    st.markdown("---")
    
    st.info("Welcome to the next generation of data intelligence. Navigate through the tabs to explore our capabilities.")
    
    st.write("") # Spacer
    st.write("") 
    
    st.markdown("### Key Features")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🚀</div>
            <div class="feature-title">Scalable Arch</div>
            <div class="feature-desc">Built for extreme performance and unlimited growth potential using modern cloud tech.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Real-time Insights</div>
            <div class="feature-desc">Visualize complex data streams instantly with our advanced interactive dashboards.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">Predictive AI</div>
            <div class="feature-desc">Leverage cutting-edge machine learning models for accurate forecasting and trend analysis.</div>
        </div>
        """, unsafe_allow_html=True)

elif selected == "Dashboard":
    st.title("Data Dashboard")
    st.markdown("Visualize complex datasets with ease.")
    
    # Dummy data
    data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Line Chart")
        st.line_chart(data)
        
    with col2:
        st.subheader("Bar Chart")
        st.bar_chart(data)
        
    st.subheader("Data Summary")
    st.dataframe(data.describe(), use_container_width=True)

elif selected == "Predictions":
    st.title("AI Predictions")
    st.markdown("Run models to generate insights.")
    
    uploaded_file = st.file_uploader("Upload CSV for Prediction", type="csv")
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        # Placeholder for model logic
        with st.spinner("Running AI Model..."):
            time.sleep(2)
        st.balloons()
        st.write("Prediction complete! (Mock output)")

elif selected == "About End-to-End":
    st.title("About the Project")
    st.markdown("""
    ### Our Mission
    To bridge the gap between specific data analysis and actionable insights.
    
    ### Tech Stack
    - **Python 3.10+** (Backend Logic)
    - **Streamlit** (Frontend Interface)
    - **Scikit-Learn** (Machine Learning)
    - **Pandas & NumPy** (Data Processing)
    
    ### Team Excellent Mirror
    - **Praveen Kumar Jangir**
    - **Jaya Verma**
    - **Ruchika**
    - **Tarun Mandal**
    """)
    st.markdown("---")
    st.caption("© 2025 Excellent Mirror Team")
