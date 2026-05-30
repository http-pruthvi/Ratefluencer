import streamlit as st
import os

import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import apply_premium_style

# Apply global premium glassmorphism styles
apply_premium_style()

# Header Section
st.markdown("""
    <div style='text-align: center; padding: 40px 0 20px 0;'>
        <h1 class='glow-title' style='font-size: 3.8rem; margin: 0; font-weight: 800;'>
            ⚡ <span class='gradient-text'>Ratefluencer AI</span>
        </h1>
        <p style='font-size: 1.35rem; color: #94a3b8; font-weight: 400; max-width: 700px; margin: 15px auto;'>
            The unified AI-powered Influencer Intelligence & Autonomous Viral Content Creation Platform built for Hackathon 2026.
        </p>
    </div>
""", unsafe_allow_html=True)

# Grid Layout for Market Statistics / Pitch
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class='glass-card' style='text-align: center; border-left: 4px solid #f43f5e;'>
            <p class='metric-label'>The Marketing Problem</p>
            <p class='metric-value' style='color: #f43f5e;'>$15 Billion</p>
            <p style='color: #94a3b8; margin-top: 10px; font-size: 0.95rem; line-height: 1.5;'>
                Wasted annually on inflated vanity metrics, bot followings, and misaligned brand partnerships.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='glass-card' style='text-align: center; border-left: 4px solid #10b981;'>
            <p class='metric-label'>Ratefluencer ROI</p>
            <p class='metric-value' style='color: #10b981;'>+30% ROI</p>
            <p style='color: #94a3b8; margin-top: 10px; font-size: 0.95rem; line-height: 1.5;'>
                Brands experience enhanced campaign conversions utilizing our 9-feature XGBoost Campaign Success predictor.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class='glass-card' style='text-align: center; border-left: 4px solid #6366f1;'>
            <p class='metric-label'>Creator Performance</p>
            <p class='metric-value' style='color: #6366f1;'>2x Faster</p>
            <p style='color: #94a3b8; margin-top: 10px; font-size: 0.95rem; line-height: 1.5;'>
                Follower growth driven by our autonomous LangGraph trend scraper, Claude script builder, and virality assessor.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Spacing
st.write("---")

# Platforms Features overview
col_track1, col_track2 = st.columns(2)

with col_track1:
    st.markdown("""
        <div class='glass-card' style='height: 380px;'>
            <h3 style='margin-top:0; display:flex; align-items:center; gap:10px;'>
                🛡️ Track 1: Influencer Intelligence
            </h3>
            <p style='color:#94a3b8; line-height:1.6;'>
                De-risk your advertising spend using four specialized layers of AI analysis.
            </p>
            <ul style='color:#cbd5e1; line-height:1.8; padding-left:20px;'>
                <li><b>Authenticity Score:</b> Detects bot networks using Isolation Forest engagement anomalies.</li>
                <li><b>Growth Score:</b> Projects 30-day follower trajectory using Prophet time-series models.</li>
                <li><b>Brand Match Score:</b> Matches brand criteria using SBERT + FAISS vector indexes.</li>
                <li><b>Ratefluencer Score™:</b> Outputs 0-100 success rates using 9-feature XGBoost.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Profile Scorer", key="launch_score"):
        st.switch_page("pages/1_influencer_score.py")

with col_track2:
    st.markdown("""
        <div class='glass-card' style='height: 380px;'>
            <h3 style='margin-top:0; display:flex; align-items:center; gap:10px;'>
                🎬 Track 2: Autonomous Viral Agent
            </h3>
            <p style='color:#94a3b8; line-height:1.6;'>
                Automate your entire content operation through our multi-agent LangGraph workflow.
            </p>
            <ul style='color:#cbd5e1; line-height:1.8; padding-left:20px;'>
                <li><b>Trend Discovyer:</b> Scrapes live technical articles from Reddit, YouTube and RSS.</li>
                <li><b>Content generation:</b> Generates high-impact 30-60s video scripts using Claude API.</li>
                <li><b>Social Publisher:</b> Composes professional LinkedIn posts and Instagram captions.</li>
                <li><b>Virality Estimator:</b> Forecasts views, likes, and shares using a Random Forest regressor.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Content Studio", key="launch_studio"):
        st.switch_page("pages/3_trend_discovery.py")

# Bottom Footer Architecture Note
st.markdown("""
    <div style='text-align: center; margin-top: 50px; color: #64748b; font-size: 0.85rem;'>
        Ratefluencer Architecture Stack: FastAPI • Streamlit • scikit-learn • XGBoost • Prophet • SentenceTransformers • LangGraph • Claude 3.5 Sonnet
    </div>
""", unsafe_allow_html=True)
