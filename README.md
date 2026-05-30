# ⚡ Ratefluencer AI

> Predict Influence. Create Virality.

![Ratefluencer AI Hackathon 2026](https://img.shields.io/badge/Hackathon-Ratefluencer%20AI%202026-blueviolet?style=for-the-badge&logo=appveyor)
![Python 3.11](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-emerald?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red?style=for-the-badge&logo=streamlit)

Ratefluencer is an all-in-one, AI-powered creator intelligence auditing and autonomous campaign marketing execution engine. Built for digital brands seeking high-converting creator alignment and automated cross-platform script copywriting, Ratefluencer utilizes Isolation Forest anomaly checking to detect follower fraud, FB Prophet time-series forecasts to map growth, Sentence-BERT FAISS dense spaces to match campaigns semantically, and sequential LangGraph workflows to discover trends, script engaging vertical reels via Claude 3.5, and forecast virality metrics using Random Forests before publishing.

---

## 🏗️ System Architecture

The Ratefluencer platform implements a strictly decoupled, 6-layer design pattern:

```
                              +------------------------------------+
                              |     Streamlit Frontend Client      |
                              |   (Obsidian HSL UI, Plotly, CSS)   |
                              +-----------------+------------------+
                                                | HTTP REST API
                                                v
                              +-----------------+------------------+
                              |         FastAPI REST Gateway       |
                              |   (CORS, SQLite/Postgres ORM, schemas)
                              +--------+-----------------+---------+
                                       |                 |
                +----------------------+                 +-----------------------+
                |                                                                |
                v                                                                v
+-------------------------------+                      +-------------------------+-----+
| TRACK 1: Influencer Scorer    |                      | TRACK 2: AI Script Agent      |
+-------------------------------+                      +-------------------------------+
| * IsolationForest Bot Audit   |                      | * Multi-Feed Trend Collectors |
| * Prophet Timeline Forecast  |                      | * Dynamic Trend Ranker        |
| * SBERT Vector Brand Matcher  |                      | * Claude 3.5 Script Supervisor|
| * XGBoost Success Classifier  |                      | * RandomForest Virality Engine|
+-------------------------------+                      +-------------------------------+
```

---

## 🛠️ Technical Stack

| Layer | Component | Core Technology | Strategic Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend** | Dashboard Client | **Streamlit** + **Plotly** | Glassmorphic interface & radial gauges |
| **Gateway** | Rest Controller | **FastAPI** + **Uvicorn** | CORs compliant gateway endpoints |
| **Agent** | Orchestration | **LangGraph** (StateGraph) | Sequential campaign assembly nodes |
| **ML Engine** | Audits & Match | **scikit-learn**, **XGBoost**, **Prophet** | Anomaly checking, time-series, and classification |
| **NLP Vectors**| Brief Matching | **SentenceTransformers** + **FAISS** | Dense vector search (all-MiniLM-L6-v2) |
| **Feeds** | Ingestion Scrapers | **PRAW**, **Google Client**, **feedparser** | reddit subreddits, YouTube, and RSS |
| **Persistence**| Database & Queue | **PostgreSQL**, **SQLite**, **Redis** | SQLAlchemy relational storage and caches |

---

## 🚀 Quick Start Guide

Spin up the entire local Ratefluencer platform in under 3 minutes:

### 1. Clone the Repository & Configure
```bash
git clone https://github.com/http-pruthvi/Ratefluencer.git
cd Ratefluencer
cp .env.example .env
```
*(By default, `.env` points to local SQLite so it boots instantly without external services).*

### 2. Install Packages
```bash
pip install -r requirements.txt
```

### 3. Generate Database & Seed Mock Data
```bash
python data/synthetic/generate.py
```

### 4. Train All Machine Learning Classifiers
```bash
python models/train_all.py
python models/train_track2.py
```

### 5. Start Backend Services
Start the uvicorn rest server:
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 6. Start Streamlit Front-End Portal
In a new terminal window:
```bash
python -m streamlit run frontend/app.py --server.port 8501
```
Open your browser and navigate to `http://localhost:8501`.

*Alternatively, run the entire containerized suite including PostgreSQL and Redis:*
```bash
docker-compose up --build
```

---

## 🔌 API Endpoints Catalog

| Endpoint | Method | Input Parameters | Sample Output Payload (Truncated) |
| :--- | :--- | :--- | :--- |
| `GET /` | `GET` | None | `{"success": true, "data": {"status": "Online", "version": "1.0.0"}}` |
| `/api/influencer/{username}` | `GET` | String handle | `{"success": true, "data": {"authenticity_score": 96.5, "ratefluencer_score": 88.2}}` |
| `/api/influencer/analyze` | `POST` | Raw metrics JSON | `{"success": true, "data": {"authenticity_score": 21.4, "ratefluencer_score": 1.0}}` |
| `/api/influencer/{id}/brand-matches` | `GET` | Integer Creator ID | `{"success": true, "data": [{"name": "FitTrack Pro", "match_score": 95.8}]}` |
| `/api/influencer/search-by-brief` | `POST` | Brand brief string | `{"success": true, "data": [{"username": "@tech_creator_0", "match_score": 88.3}]}` |
| `/api/trends` | `GET` | Integer Limit | `{"success": true, "data": [{"topic": "Multi-agent systems", "trend_score": 95.2}]}` |
| `/api/trends/score` | `POST` | Custom topic string | `{"success": true, "data": {"topic": "SaaS growth", "trend_score": 80.5}}` |
| `/api/content/agent-pipeline` | `POST` | Custom topic & niche | `{"success": true, "data": {"script": "[HOOK]...", "virality_score": 79.5}}` |

### Sample Endpoint cURL Request:
Query the dense SBERT vector space for matching influencers:
```bash
curl -X POST "http://127.0.0.1:8000/api/influencer/search-by-brief" \
     -H "Content-Type: application/json" \
     -d '{"brief": "We seek a developer creating Python AI coding tutorials."}'
```

---

## 👥 Project Team

*   **http-pruthvi** — *Lead AI Architect & Core Systems Engineer* (https://github.com/http-pruthvi)
*   **Antigravity AI** — *Advanced Agentic Coding Partner* (Google DeepMind Team)
