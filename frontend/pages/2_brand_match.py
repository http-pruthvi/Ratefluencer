import streamlit as st
import requests
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import apply_premium_style

apply_premium_style()

st.markdown("""
    <h2 style='margin-bottom: 5px; font-weight: 800;'>🤝 <span class='gradient-text'>Vector Campaign Matcher</span></h2>
    <p style='color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;'>
        Paste your campaign brief below. Our SBERT dense vector engine will semantically query our database of 1,000 influencers to find the absolute best fits.
    </p>
""", unsafe_allow_html=True)

# Brief input area
brief_text = st.text_area(
    "Campaign Marketing Brief / Ideal Creator Description",
    "We are seeking a developer or tech builder who makes daily tutorials about AI agents, cloud computing, and coding hacks. They should have a clean, minimalist workspace aesthetic and speak to software engineers.",
    height=120
)

col_btn_left, _ = st.columns([1, 4])
with col_btn_left:
    search_triggered = st.button("Search Creators")

# Execution block
if brief_text and search_triggered:
    api_url = "http://127.0.0.1:8000/api/influencer/search-by-brief"
    
    with st.spinner("Embedding campaign brief and running FAISS vector search..."):
        try:
            response = requests.post(api_url, json={"brief": brief_text}, timeout=10)
            
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("success"):
                    creators = res_json["data"]
                    
                    st.markdown("### 🎯 Ideal Creator Partnerships Discovered")
                    
                    if not creators:
                        st.warning("No matching creators were found in the database.")
                    
                    for idx, creator in enumerate(creators):
                        # Construct a clean visually outstanding card for each matching creator
                        st.markdown(f"""
                            <div class='glass-card' style='display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #818cf8; padding: 20px;'>
                                <div style='width: 75%;'>
                                    <div style='display: flex; align-items: center; gap: 12px;'>
                                        <h4 style='margin: 0; font-size: 1.3rem; font-weight: 800; color: #ffffff;'>{creator['username']}</h4>
                                        <span style='background: rgba(129, 140, 248, 0.15); color: #a5b4fc; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;'>{creator['content_category']}</span>
                                    </div>
                                    <p style='color: #64748b; font-size: 0.88rem; margin-top: 5px; font-weight: 600;'>
                                        Instagram • {creator['followers']:,} followers
                                    </p>
                                    <p style='color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin-top: 10px; font-style: italic;'>
                                        "{creator['bio']}"
                                    </p>
                                </div>
                                <div style='text-align: right; min-width: 140px;'>
                                    <p style='margin: 0; color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Match Relevance</p>
                                    <h2 style='margin: 5px 0 0 0; color: #10b981; font-weight: 800; font-size: 2.3rem; font-family: "Outfit", sans-serif;'>{creator['match_score']:.1f}%</h2>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # In Streamlit, let's render a quick button to view details for this creator
                        btn_col, _ = st.columns([1.5, 5])
                        with btn_col:
                            # Use a clean unique button key
                            if st.button(f"Analyze {creator['username']}", key=f"btn_creator_{idx}"):
                                # We can set session state to navigate
                                st.session_state["target_username"] = creator["username"]
                                st.switch_page("pages/1_influencer_score.py")
                        st.write("")
                else:
                    st.error(f"Search failed: {res_json.get('error')}")
            else:
                st.error("API server is offline. Please launch the backend FastAPI service first!")
        except Exception as e:
            st.error(f"Connection error: {e}")
