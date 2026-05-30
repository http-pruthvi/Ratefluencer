# ⚡ Ratefluencer AI Platform

Ratefluencer is an AI-powered Influencer Intelligence & Autonomous Content Creation Platform built for the **2026 AI Hackathon**. The system de-risks influencer marketing campaigns by uncovering engagement fraud, forecasting follower trajectory, semantically matching campaigns to creators, and autonomously scripting, analyzing, and publishing viral content using a multi-agent **LangGraph** workflow.

---

## 🏗️ System Architecture

Ratefluencer operates two core product tracks within a decoupled microservices design:

```
                                      +------------------------------------+
                                      |         Streamlit Frontend         |
                                      +-----------------+------------------+
                                                        | REST API
                                                        v
                                      +-----------------+------------------+
                                      |          FastAPI Backend           |
                                      +--------+-----------------+---------+
                                               |                 |
                        +----------------------+                 +-----------------------+
                        |                                                                |
                        v                                                                v
+-----------------------+-----------------------+      +---------------------------------+---------------------+
|        TRACK 1: Influencer Intelligence       |      |          TRACK 2: Autonomous Content Agent          |
+-----------------------------------------------+      +-------------------------------------------------------+
| 1. Authenticity: Isolation Forest Bot Audit   |      | 1. Discovery: PRAW Reddit, YouTube & Tech RSS Scraper |
| 2. Growth: Prophet Time-Series Forecast      |      | 2. Ranking: Multi-Metric Calibrated Trend Ranker      |
| 3. Brand Match: SBERT Semantic Vector Indexes  |      | 3. Creation: Claude 3.5 Sonnet Scripting (Hook/Story) |
| 4. Scorer: XGBoost Success Classifier (9 Feat)|      | 4. Virality: Random Forest Engagement Estimator       |
+-----------------------------------------------+      +-------------------------------------------------------+
```

---

## 🛠️ Tech Stack & Dependencies

*   **API Framework:** FastAPI + Python 3.11+
*   **Machine Learning:** scikit-learn, XGBoost (GradientBoosting), FB Prophet
*   **Semantic Vector Space:** SentenceTransformers (`all-MiniLM-L6-v2`), FAISS
*   **Orchestration Agent:** LangGraph (StateGraph Workflow)
*   **Generative AI:** Anthropic Claude API (`claude-3-5-sonnet`)
*   **Databases:** PostgreSQL (SQLAlchemy ORM), SQLite (Dynamic Fallback), Redis (Cache)
*   **Frontend UI:** Streamlit (Obsidian Dark Theme + HSL Glassmorphic styles)
*   **Data Feeds:** PRAW (Reddit), google-api-python-client (YouTube), feedparser (RSS)

---

## 🚀 Installation & Execution

### 1. Requirements Setup
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*By default, the `.env` has `DATABASE_URL` configured to `sqlite:///./ratefluencer.db` so the system can run instantly on local machines without Docker or Postgres configs.*

### 3. Generate Database & Seed Data
Generate 1,000 highly realistic influencer records, including bot anomalies (10%), time-series curves, brand campaign profiles, and pre-cached scripts:
```bash
python data/synthetic/generate.py
```

### 4. Fit & Archive Machine Learning Models
Train the `IsolationForest` authenticity model and the campaign performance classifier, saving pickle weights into `models/saved/`:
```bash
python models/train_all.py
```

### 5. Launch FastAPI Backend
Launch the uvicorn CORS server locally:
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 6. Start Streamlit UI Dashboard
In a separate terminal, launch the Streamlit frontend client:
```bash
streamlit run frontend/app.py
```
*Open your browser and navigate to the local client address (usually `http://localhost:8501`).*

---

## 🐳 Running with Docker

Provision the full PostgreSQL database, Redis caches, FastAPI server, and Streamlit client under Docker Compose:
```bash
docker-compose up --build
```
The Streamlit app will load on `http://localhost:8501`, connecting automatically to the API gateway on `http://localhost:8000`.

---

## 📦 Verification Test Suite
Execute our comprehensive end-to-end integration test validating database schemas, models, vector matching, trend collections, and the LangGraph sequential workflow:
```bash
python tests/run_tests.py
```

---

## 🏆 Hackathon High-Fidelity Mock Fallback (Bulletproof Demo)

To ensure a flawless live evaluation without active third-party API tokens, Ratefluencer implements **intelligent offline fallbacks**:

1.  **AI Script Generation (No Anthropic Key):** Replaces Claude network calls with dynamic category templates from `mock_scripts.json` performing real-time keyword replacement mapping the selected topic.
2.  **Social Scrapers (No PRAW/YouTube Keys):** Seamlessly shifts from active APIs to multi-thread simulated trend generators returning realistic technical threads and videos.
3.  **Semantic Vectors (Offline HF weights):** Activates a pure Python character TF-IDF bag-of-words vector space matching SBERT dimensions exactly if HuggingFace weights are inaccessible offline.
4.  **Database (No PostgreSQL Server):** Dynamic SQLAlchemy connection block automatically detects PostgreSQL connection errors and shifts to a local SQLite `ratefluencer.db` instantly.
