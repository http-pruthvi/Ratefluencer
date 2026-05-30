import streamlit as st
import requests
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import apply_premium_style

apply_premium_style()

st.markdown("""
    <h2 style='margin-bottom: 5px; font-weight: 800;'>🔥 <span class='gradient-text'>Live Trend Intelligence</span></h2>
    <p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;'>
        Real-time hot-spots aggregated from technical subreddits, science/tech YouTube, and RSS feeds. Ranked dynamically by volume, velocity, and engagement.
    </p>
""", unsafe_allow_html=True)

# Main action layout
col_refresh, _ = st.columns([1, 5])
with col_refresh:
    refresh_btn = st.button("Refresh Trends")

api_url = "http://127.0.0.1:8000/api/trends"

with st.spinner("Harvesting live API feeds and executing trend scoring algorithms..."):
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("success"):
                trends = res_json["data"]
                
                st.markdown("### 🏆 Top Discovered Trends Today")
                
                if not trends:
                    st.warning("No trends collected. Please check feed connectivity.")
                
                # Grid of cards: 2 columns for card spacing
                for idx in range(0, len(trends), 2):
                    col_left, col_right = st.columns(2)
                    
                    # Left Column Card
                    if idx < len(trends):
                        trend = trends[idx]
                        source_tag = trend["source"]
                        color = "#ff4500" if source_tag == "Reddit" else ("#ff0000" if source_tag == "YouTube" else "#0ea5e9")
                        
                        with col_left:
                            st.markdown(f"""
                                <div class='glass-card' style='height: 290px; display:flex; flex-direction:column; justify-content:space-between; border-left: 4px solid {color}; padding: 22px;'>
                                    <div>
                                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                                            <span style='background:rgba(255,255,255,0.05); color:{color}; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase;'>{source_tag}</span>
                                            <span style='color:#cbd5e1; font-weight:800; font-size:1.15rem;'>⚡ {trend['trend_score']:.1f}</span>
                                        </div>
                                        <h4 style='margin:12px 0 0 0; font-size: 1.15rem; font-weight:700; color:#ffffff; line-height:1.4;'>{trend['title']}</h4>
                                    </div>
                                    
                                    <div style='margin-top:auto;'>
                                        <div style='display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:15px; border-top:1px solid rgba(255,255,255,0.04); padding-top:10px;'>
                                            <div style='font-size:0.8rem; color:#64748b;'>Velocity: <b style='color:#cbd5e1;'>{trend['velocity_factor']*100:.0f}%</b></div>
                                            <div style='font-size:0.8rem; color:#64748b;'>Engagement: <b style='color:#cbd5e1;'>{trend['engagement_factor']*100:.0f}%</b></div>
                                            <div style='font-size:0.8rem; color:#64748b;'>Novelty: <b style='color:#cbd5e1;'>{trend['novelty_factor']*100:.0f}%</b></div>
                                            <div style='font-size:0.8rem; color:#64748b;'>Volume: <b style='color:#cbd5e1;'>{trend['volume_factor']*100:.0f}%</b></div>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Navigation button
                            if st.button("Script with Agent", key=f"btn_trend_{idx}"):
                                st.session_state["selected_trend"] = trend
                                st.switch_page("pages/4_content_creator.py")
                                
                    # Right Column Card
                    if idx + 1 < len(trends):
                        trend = trends[idx + 1]
                        source_tag = trend["source"]
                        color = "#ff4500" if source_tag == "Reddit" else ("#ff0000" if source_tag == "YouTube" else "#0ea5e9")
                        
                        with col_right:
                            st.markdown(f"""
                                <div class='glass-card' style='height: 290px; display:flex; flex-direction:column; justify-content:space-between; border-left: 4px solid {color}; padding: 22px;'>
                                    <div>
                                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                                            <span style='background:rgba(255,255,255,0.05); color:{color}; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase;'>{source_tag}</span>
                                            <span style='color:#cbd5e1; font-weight:800; font-size:1.15rem;'>⚡ {trend['trend_score']:.1f}</span>
                                        </div>
                                        <h4 style='margin:12px 0 0 0; font-size: 1.15rem; font-weight:700; color:#ffffff; line-height:1.4;'>{trend['title']}</h4>
                                    </div>
                                    
                                    <div style='margin-top:auto;'>
                                        <div style='display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:15px; border-top:1px solid rgba(255,255,255,0.04); padding-top:10px;'>
                                            <div style='font-size:0.8rem; color:#64748b;'>Velocity: <b style='color:#cbd5e1;'>{trend['velocity_factor']*100:.0f}%</b></div>
                                            <div style='font-size:0.8rem; color:#64748b;'>Engagement: <b style='color:#cbd5e1;'>{trend['engagement_factor']*100:.0f}%</b></div>
                                            <div style='font-size:0.8rem; color:#64748b;'>Novelty: <b style='color:#cbd5e1;'>{trend['novelty_factor']*100:.0f}%</b></div>
                                            <div style='font-size:0.8rem; color:#64748b;'>Volume: <b style='color:#cbd5e1;'>{trend['volume_factor']*100:.0f}%</b></div>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Navigation button
                            if st.button("Script with Agent", key=f"btn_trend_{idx+1}"):
                                st.session_state["selected_trend"] = trend
                                st.switch_page("pages/4_content_creator.py")
                            
            else:
                st.error(f"Failed to fetch trends: {res_json.get('error')}")
        else:
            st.error("API server is offline. Please launch the backend FastAPI service first!")
    except Exception as e:
        st.error(f"Connection error: {e}")
