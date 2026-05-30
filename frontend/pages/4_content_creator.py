import streamlit as st
import requests
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import apply_premium_style
from components.charts import render_gauge_chart

apply_premium_style()

st.markdown("""
    <h2 style='margin-bottom: 5px; font-weight: 800;'>🎬 <span class='gradient-text'>AI Campaign Content Studio</span></h2>
    <p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;'>
        Trigger our autonomous LangGraph agent to generate viral video scripts, cross-platform captions, and predict campaign virality.
    </p>
""", unsafe_allow_html=True)

# Pull selected trend from session state if navigates from Page 3
selected_trend = st.session_state.get("selected_trend")
default_topic = ""
default_category = "tech"

if selected_trend:
    default_topic = selected_trend.get("topic", "")
    default_category = selected_trend.get("category", "tech")
else:
    default_topic = "AI agents are taking over coding in 2026"

# Input configurations
col_top1, col_top2 = st.columns([4, 2])
with col_top1:
    topic_input = st.text_input("Topic/Headline", default_topic, placeholder="e.g. AI coding benchmarks, Zone 2 Cardio secrets")
with col_top2:
    category_list = ["tech", "finance", "fitness", "fashion", "food", "travel", "gaming"]
    selected_cat = st.selectbox(
        "Niche Category", 
        category_list, 
        index=category_list.index(default_category) if default_category in category_list else 0
    )

col_act, _ = st.columns([1.5, 4.5])
with col_act:
    run_agent = st.button("Generate Campaign")

# Process Agent pipeline
if (topic_input and run_agent) or (selected_trend and "agent_ran" not in st.session_state):
    # Lock execution to prevent infinite refreshes
    st.session_state["agent_ran"] = True
    
    api_url = "http://127.0.0.1:8000/api/content/agent-pipeline"
    payload = {
        "topic": topic_input,
        "category": selected_cat
    }
    
    with st.spinner("Invoking LangGraph Agent workflow (Discovery -> Claude Script -> Publisher -> Virality Engine)..."):
        try:
            response = requests.post(api_url, json=payload, timeout=25)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("success"):
                    st.session_state["agent_result"] = res_json["data"]
                else:
                    st.error(f"Agent pipeline failed: {res_json.get('error')}")
            else:
                st.error("API server is offline. Please launch the backend FastAPI service first!")
        except Exception as e:
            st.error(f"Agent execution timeout or connection failed: {e}")

# Render results from session state if populated
if "agent_result" in st.session_state:
    res = st.session_state["agent_result"]
    script_text = res.get("script", "")
    
    # Let's break down script text into sections for premium color bands
    sections = {"hook": "", "story": "", "insights": "", "cta": ""}
    
    current_sec = None
    for line in script_text.split("\n"):
        line_s = line.strip()
        if not line_s:
            continue
            
        line_l = line_s.lower()
        if "[hook]" in line_l or "hook:" in line_l:
            current_sec = "hook"
            line_s = line_s.replace("[HOOK]", "").replace("[hook]", "").replace("HOOK:", "").strip()
        elif "[story]" in line_l or "story:" in line_l:
            current_sec = "story"
            line_s = line_s.replace("[STORY]", "").replace("[story]", "").replace("STORY:", "").strip()
        elif "[insights]" in line_l or "insights:" in line_l or "[insight]" in line_l:
            current_sec = "insights"
            line_s = line_s.replace("[INSIGHTS]", "").replace("[insights]", "").replace("[INSIGHT]", "").replace("INSIGHTS:", "").strip()
        elif "[cta]" in line_l or "cta:" in line_l:
            current_sec = "cta"
            line_s = line_s.replace("[CTA]", "").replace("[cta]", "").replace("CTA:", "").strip()
            
        if current_sec and line_s:
            sections[current_sec] += (" " if sections[current_sec] else "") + line_s
            
    # If standard tags were not matched in Claude output, fall back to showing the entire script in tech band
    if not any(sections.values()):
        sections["hook"] = script_text
        
    st.write("---")
    
    # Double layout columns: Left=Scripts/socials, Right=Virality dials
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("### 🎬 Generated Video Reel Script")
        st.markdown("<p style='color:#94a3b8; font-size:0.88rem; margin-top:-5px; margin-bottom:15px;'>Vertical video outline parsed by script supervisor.</p>", unsafe_allow_html=True)
        
        # Display highlight bands
        if sections["hook"]:
            st.markdown(f"""
                <div class='script-band band-hook'>
                    <b>🪝 HOOK (0-5s):</b><br/>{sections['hook']}
                </div>
            """, unsafe_allow_html=True)
            
        if sections["story"]:
            st.markdown(f"""
                <div class='script-band band-story'>
                    <b>📖 STORY (5-25s):</b><br/>{sections['story']}
                </div>
            """, unsafe_allow_html=True)
            
        if sections["insights"]:
            st.markdown(f"""
                <div class='script-band band-insights'>
                    <b>💡 INSIGHTS (25-50s):</b><br/>{sections['insights']}
                </div>
            """, unsafe_allow_html=True)
            
        if sections["cta"]:
            st.markdown(f"""
                <div class='script-band band-cta'>
                    <b>🎯 CALL TO ACTION (50-60s):</b><br/>{sections['cta']}
                </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        # Social Copy tabs
        st.markdown("### 📲 Multi-Channel Publishing")
        tab_li, tab_ig = st.tabs(["💼 LinkedIn Post", "📸 Instagram Caption"])
        
        with tab_li:
            st.text_area("LinkedIn Professional Copy", res.get("linkedin_post", ""), height=220)
            
        with tab_ig:
            st.text_area("Instagram Caption Copy", res.get("instagram_caption", ""), height=220)
            st.write(f"**Hashtags suggested:** `{' '.join(res.get('hashtags', []))}`")
            
    with col_right:
        st.markdown("### 🔮 Virality Forecasting")
        
        # Dial indicator
        vir_score = res.get("virality_score", 0.0)
        fig_vir = render_gauge_chart(vir_score, "Virality Rating", "#f43f5e")
        st.plotly_chart(fig_vir, use_container_width=True)
        
        # Forecasted statistics blocks
        col_views, col_likes, col_shares = st.columns(3)
        with col_views:
            st.markdown(f"""
                <div class='glass-card' style='text-align: center; padding: 12px;'>
                    <p class='metric-label' style='font-size:0.75rem;'>Est Views</p>
                    <p class='metric-value' style='font-size:1.35rem; color:#ffffff;'>{res.get('expected_views', 0):,}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_likes:
            st.markdown(f"""
                <div class='glass-card' style='text-align: center; padding: 12px;'>
                    <p class='metric-label' style='font-size:0.75rem;'>Est Likes</p>
                    <p class='metric-value' style='font-size:1.35rem; color:#ffffff;'>{res.get('expected_likes', 0):,}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_shares:
            st.markdown(f"""
                <div class='glass-card' style='text-align: center; padding: 12px;'>
                    <p class='metric-label' style='font-size:0.75rem;'>Est Shares</p>
                    <p class='metric-value' style='font-size:1.35rem; color:#ffffff;'>{res.get('expected_shares', 0):,}</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        # Insights list
        st.markdown("#### 📝 Script Structure Critiques")
        insights = res.get("insights", [])
        for ins in insights:
            if "present" in ins.lower() or "optimal" in ins.lower():
                st.markdown(f"🟢 {ins}")
            else:
                st.markdown(f"🟡 {ins}")
                
        st.write("")
        # Clean session state option to run another
        if st.button("Reset Content Studio", key="btn_reset"):
            st.session_state.pop("agent_result", None)
            st.session_state.pop("agent_ran", None)
            st.session_state.pop("selected_trend", None)
            st.rerun()
