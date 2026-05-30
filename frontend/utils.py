import streamlit as st

def apply_premium_style():
    """Injects high-end, responsive glassmorphic dark-mode styling into the Streamlit session."""
    st.set_page_config(
        page_title="Ratefluencer AI Platform",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for dark mode theme, fonts, borders, and animations
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600;700&display=swap');
        
        /* Global Background & Typography */
        html, body, [class*="css"], .stApp {
            background-color: #0b0f19;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, .stHeader {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            letter-spacing: -0.02em;
        }
        
        /* Sidebar custom aesthetic */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0e1626 0%, #060913 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        [data-testid="stSidebarNav"] {
            background-color: transparent !important;
        }
        
        /* Glow titles & linear gradients */
        .gradient-text {
            background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 50%, #4f46e5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        .glow-title {
            text-shadow: 0 0 25px rgba(99, 102, 241, 0.35);
        }
        
        /* Premium Card Styling */
        .glass-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(12px);
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 15px 40px rgba(99, 102, 241, 0.12);
            transform: translateY(-2px);
        }
        
        /* Accent Metrics */
        .metric-label {
            font-size: 0.9rem;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            color: #ffffff;
            margin: 0;
        }
        
        /* Video script custom highlighting bands */
        .script-band {
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 12px;
            border-left: 5px solid;
            font-size: 1.05rem;
            line-height: 1.6;
        }
        
        .band-hook {
            background: rgba(239, 68, 68, 0.06);
            border-color: #ef4444;
            color: #fca5a5;
        }
        
        .band-story {
            background: rgba(245, 158, 11, 0.06);
            border-color: #f59e0b;
            color: #fde047;
        }
        
        .band-insights {
            background: rgba(16, 185, 129, 0.06);
            border-color: #10b981;
            color: #6ee7b7;
        }
        
        .band-cta {
            background: rgba(99, 102, 241, 0.06);
            border-color: #6366f1;
            color: #c7d2fe;
        }
        
        /* Custom styled buttons */
        div.stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4) !important;
        }
        
        div.stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
        }
        
        /* Hide default Streamlit footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        </style>
    """, unsafe_allow_html=True)
