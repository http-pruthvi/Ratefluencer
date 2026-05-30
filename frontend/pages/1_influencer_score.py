import streamlit as st
import requests
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import apply_premium_style
from components.charts import render_gauge_chart, render_growth_timeline

apply_premium_style()

st.markdown("""
    <h2 style='margin-bottom: 5px; font-weight: 800;'>🔍 <span class='gradient-text'>Creator Profile Analyzer</span></h2>
    <p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;'>
        Enter an Instagram username to execute our multi-layer ML audit: Isolation Forest bot checks, SBERT brand indexing, and Prophet forecasting.
    </p>
""", unsafe_allow_html=True)

# Search Input Layout
col_input, col_btn = st.columns([5, 1])
with col_input:
    username = st.text_input("Instagram Username", "@tech_creator_45", placeholder="e.g. @fitness_model, @tech_guru")
with col_btn:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    search_triggered = st.button("Run Audit")

# Core inference block
if username or search_triggered:
    api_url = f"http://127.0.0.1:8000/api/influencer/{username.replace('@', '')}"
    
    with st.spinner("Analyzing profile statistics & running forecasting models..."):
        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("success"):
                    data = res_json["data"]
                    profile = data["profile"]
                    
                    # --- Main Score Dials Section ---
                    st.markdown("### 📊 Performance Scoring")
                    col_gauge1, col_gauge2, col_gauge3 = st.columns(3)
                    
                    with col_gauge1:
                        fig1 = render_gauge_chart(data["authenticity_score"], "Authenticity Score", "#ef4444")
                        st.plotly_chart(fig1, use_container_width=True)
                        st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-top:-20px;'>Isolation Forest bot risk detector</p>", unsafe_allow_html=True)
                        
                    with col_gauge2:
                        fig2 = render_gauge_chart(data["growth_score"], "Growth Forecast Score", "#3b82f6")
                        st.plotly_chart(fig2, use_container_width=True)
                        st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-top:-20px;'>Prophet 30-day time-series growth</p>", unsafe_allow_html=True)
                        
                    with col_gauge3:
                        fig3 = render_gauge_chart(data["ratefluencer_score"], "Ratefluencer Score™", "#10b981")
                        st.plotly_chart(fig3, use_container_width=True)
                        st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-top:-20px;'>XGBoost Campaign Success probability</p>", unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # --- Detailed Profile Audit Summary & Growth Graph ---
                    col_info, col_graph = st.columns([2, 3])
                    
                    with col_info:
                        st.markdown("### 📝 Profile Audit")
                        st.markdown(f"""
                            <div class='glass-card' style='padding: 20px;'>
                                <p style='margin:0; font-size: 1.35rem; font-weight:800; color:#818cf8;'>{profile['username']}</p>
                                <p style='color:#64748b; font-size:0.9rem; margin-top:2px; text-transform:uppercase;'>Niche: {profile['content_category']} • {profile['platform']}</p>
                                <p style='font-style:italic; color:#cbd5e1; font-size:0.95rem; margin-top:10px; line-height:1.5;'>
                                    "{profile['bio']}"
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Quantitative metrics table
                        st.markdown(f"""
                            <div class='glass-card' style='padding: 20px;'>
                                <table style='width:100%; border-collapse:collapse; color:#cbd5e1;'>
                                    <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'>
                                        <td style='padding:8px 0; color:#94a3b8;'>Followers</td>
                                        <td style='padding:8px 0; text-align:right; font-weight:700;'>{profile['followers']:,}</td>
                                    </tr>
                                    <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'>
                                        <td style='padding:8px 0; color:#94a3b8;'>Following</td>
                                        <td style='padding:8px 0; text-align:right; font-weight:700;'>{profile['following']:,}</td>
                                    </tr>
                                    <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'>
                                        <td style='padding:8px 0; color:#94a3b8;'>Engagement Rate</td>
                                        <td style='padding:8px 0; text-align:right; font-weight:700; color:#10b981;'>{profile['engagement_rate']*100:.2f}%</td>
                                    </tr>
                                    <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'>
                                        <td style='padding:8px 0; color:#94a3b8;'>Avg Likes</td>
                                        <td style='padding:8px 0; text-align:right; font-weight:700;'>{int(profile['avg_likes']):,}</td>
                                    </tr>
                                    <tr style='border-bottom:1px solid rgba(255,255,255,0.05);'>
                                        <td style='padding:8px 0; color:#94a3b8;'>Avg Comments</td>
                                        <td style='padding:8px 0; text-align:right; font-weight:700;'>{int(profile['avg_comments']):,}</td>
                                    </tr>
                                    <tr>
                                        <td style='padding:8px 0; color:#94a3b8;'>Weekly Post Freq</td>
                                        <td style='padding:8px 0; text-align:right; font-weight:700;'>{profile['posting_frequency']:.1f} posts/wk</td>
                                    </tr>
                                </table>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col_graph:
                        st.markdown("### 📈 Follower Trajectory Forecast")
                        fig_timeline = render_growth_timeline(data["historical_history"], data["predicted_history"])
                        st.plotly_chart(fig_timeline, use_container_width=True)
                        
                        growth_pct = data["growth_rate_30d_pct"]
                        arrow = "🔺" if growth_pct >= 0 else "🔻"
                        st.markdown(f"""
                            <div style='text-align: center; color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>
                                Estimated 30-Day Growth: <b style='color: {"#10b981" if growth_pct >= 0 else "#ef4444"};'>{arrow} {growth_pct:.2f}%</b>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    st.write("---")
                    
                    # --- Semantic Brand Matching Recommendations ---
                    st.markdown("### 🤝 Semantic Brand Matches")
                    st.markdown("<p style='color:#94a3b8; font-size:0.95rem; margin-bottom:15px;'>Top product campaigns semantically aligned to this creator's bio using SBERT vector cosine similarity search.</p>", unsafe_allow_html=True)
                    
                    # Call Brand Matches Endpoint
                    brand_api_url = f"http://127.0.0.1:8000/api/influencer/{profile['id']}/brand-matches"
                    brand_res = requests.get(brand_api_url, timeout=5)
                    
                    if brand_res.status_code == 200 and brand_res.json().get("success"):
                        brands = brand_res.json()["data"]
                        cols_brands = st.columns(len(brands))
                        
                        for idx, brand in enumerate(brands):
                            with cols_brands[idx]:
                                st.markdown(f"""
                                    <div class='glass-card' style='height: 250px; border-top: 3px solid #818cf8; display:flex; flex-direction:column; justify-content:space-between; padding: 18px;'>
                                        <div>
                                            <p style='margin:0; font-size: 1.15rem; font-weight:800; color:#ffffff;'>{brand['name']}</p>
                                            <span style='background:rgba(129, 140, 248, 0.15); color:#a5b4fc; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase;'>{brand['industry']}</span>
                                            <p style='color:#94a3b8; font-size:0.82rem; line-height:1.4; margin-top:10px;'>
                                                "{brand['description'][:110]}..."
                                            </p>
                                        </div>
                                        <div style='margin-top:auto;'>
                                            <div style='display:flex; justify-content:space-between; align-items:center; margin-top:10px;'>
                                                <span style='color:#64748b; font-size:0.8rem;'>Match Score</span>
                                                <span style='color:#10b981; font-weight:800; font-size:1.1rem;'>{brand['match_score']:.1f}%</span>
                                            </div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No matching campaigns found for this creator.")
                        
                else:
                    st.error(f"Error fetching data: {res_json.get('error')}")
            else:
                st.error("API server is offline. Please launch the backend FastAPI service first!")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
