import streamlit as st
import requests
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import apply_premium_style

apply_premium_style()

st.markdown("""
    <h2 style='margin-bottom: 5px; font-weight: 800;'>🔥 <span class='gradient-text'>Live Trend Discovery</span></h2>
    <p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;'>
        Real-time hot-spots consolidated across subreddits, YouTube technology feeds, and RSS. Ranked dynamically by volume, velocity, and novelty.
    </p>
""", unsafe_allow_html=True)

# Main action layout
col_refresh, _ = st.columns([1, 5])
with col_refresh:
    refresh_btn = st.button("Refresh Feeds")

api_url = "http://127.0.0.1:8000/api/trends"

with st.spinner("Harvesting live API feeds and executing trend scoring algorithms..."):
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("success"):
                trends = res_json["data"]
                
                st.markdown("### 🏆 Top 10 Ranked Tech Trends")
                st.write("")
                
                if not trends:
                    st.warning("No trends collected. Please check feed connectivity.")
                else:
                    # Table Headers
                    st.markdown("""
                        <div style='display: grid; grid-template-columns: 0.8fr 1.2fr 4.2fr 2.3fr 1.5fr; gap: 10px; border-bottom: 2px solid rgba(255,255,255,0.08); padding-bottom: 10px; margin-bottom: 15px; font-weight: 700; color: #94a3b8; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;'>
                            <div>Rank</div>
                            <div>Source</div>
                            <div>Trending Topic</div>
                            <div style='text-align: center;'>Trend Score</div>
                            <div style='text-align: right; padding-right: 15px;'>Action</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Table Rows
                    for idx, trend in enumerate(trends[:10]):
                        source_tag = trend["source"]
                        color = "#ff4500" if source_tag == "Reddit" else ("#ff0000" if source_tag == "YouTube" else "#0ea5e9")
                        
                        col_rank, col_src, col_topic, col_score, col_act = st.columns([0.8, 1.2, 4.2, 2.3, 1.5])
                        
                        with col_rank:
                            st.markdown(f"<div style='padding-top: 10px; font-weight: 800; font-size: 1.1rem; color: #cbd5e1;'>#{idx+1}</div>", unsafe_allow_html=True)
                            
                        with col_src:
                            st.markdown(f"<div style='padding-top: 10px;'><span style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); color: {color}; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;'>{source_tag}</span></div>", unsafe_allow_html=True)
                            
                        with col_topic:
                            st.markdown(f"""
                                <div style='padding-top: 8px;'>
                                    <b style='color: #ffffff; font-size: 0.98rem;'>{trend['title']}</b><br/>
                                    <span style='color: #64748b; font-size: 0.8rem;'>Velocity: {trend['velocity_factor']*100:.0f}% • Engagement: {trend['engagement_factor']*100:.0f}%</span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        with col_score:
                            st.markdown(f"<div style='text-align: center; color: #ffffff; font-weight: 800; font-size: 1rem; margin-bottom: 2px;'>{trend['trend_score']:.1f} / 100</div>", unsafe_allow_html=True)
                            st.progress(min(1.0, max(0.0, trend["trend_score"] / 100.0)))
                            
                        with col_act:
                            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                            if st.button("Script", key=f"btn_trend_{idx}"):
                                st.session_state["selected_trend"] = trend
                                # Pop old results
                                st.session_state.pop("agent_result", None)
                                st.session_state.pop("agent_ran", None)
                                st.switch_page("pages/4_content_creator.py")
                                
                        st.markdown("<div style='border-bottom: 1px solid rgba(255,255,255,0.03); margin: 8px 0;'></div>", unsafe_allow_html=True)
            else:
                st.error(f"Failed to fetch trends: {res_json.get('error')}")
        else:
            st.error("API server is offline. Please launch the backend FastAPI service first!")
    except Exception as e:
        st.error(f"Connection error: {e}")
