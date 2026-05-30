# 🛡️ Ratefluencer System Architecture Guide

Ratefluencer AI Platform is a modular, decoupled microservices ecosystem that delivers influencer intelligence auditing (Track 1) and autonomous content scripting/virality forecasting (Track 2) for corporate digital marketing.

---

## 🏗️ 1. Six-Layer Decoupled Design

The software follows a strictly isolated 6-layer architectural layout:

```
+-------------------------------------------------------------+
| 1. Frontend Layer: Streamlit Obsidian Dark UI, Plotly Charts|
+------------------------------+------------------------------+
                               | REST JSON
                               v
+-------------------------------------------------------------+
| 2. Gateway Layer: FastAPI CORS REST Gateway                 |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 3. Agent Layer: Sequential LangGraph Agent Pipeline          |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 4. ML Models: XGBoost, IsolationForest, SBERT Vector, RF    |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 5. Ingestion: PRAW Reddit, YouTube APIs, RSS Feedparser     |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 6. Persistence: PostgreSQL/SQLite SQLAlchemy ORM, Redis Cache|
+-------------------------------------------------------------+
```

### Layer Details:
1.  **Frontend Layer (Presentation):** Injects premium custom CSS styling (vibrant titles, Outfit/Inter typography, and glassmorphic metric borders) directly into the Streamlit session. Standardizes gauge indicator sweeps and forecasting timelines using Plotly wrappers.
2.  **Gateway Layer (API Control):** Exposes 8 REST endpoints validating client requests against Pydantic schema serializers. Implements global CORS parameters for front-end client rendering.
3.  **Agent Layer (Orchestration):** Orchestrates sequential states (`trend_node` → `script_node` → `caption_node` → `virality_node`) carrying custom states. Implements a thread-safe Python fallback runner to bypass graph failures if the third-party `langgraph` package is missing.
4.  **Core ML Models Layer (Intelligence):** Archives pre-trained pickle weights (`models/saved/*.pkl`) comprising an Isolation Forest anomaly classifier, a Prophet forecaster, an SBERT vector index, and a Random Forest regressor.
5.  **Ingestion & Scraping Layer (Data Acquisition):** Integrates PRAW Reddit, YouTube Data API, and Feedparser RSS, complete with robust, offline simulated trend generators to ensure out-of-the-box demo coverage.
6.  **Persistence & Cache Layer (Storage):** Directs database session management via SQLAlchemy. Connection managers automatically fallback from default PostgreSQL ports (`5432`) to a local SQLite `ratefluencer.db` file if Postgres services are offline, facilitating instant local startup.

---

## 📊 2. Data Flow Architecture

The dynamic system execution pipelines map as follows:

```mermaid
sequenceDiagram
    autonumber
    actor User as Corporate Brand / Creator
    participant UI as Streamlit UI Dashboard
    participant API as FastAPI Gateway
    participant Agent as LangGraph Orchestrator
    participant DB as Postgres/SQLite Database
    participant ML as ML Models Layer (XGBoost, SBERT, RF)

    User->>UI: Input Instagram username
    UI->>API: GET /api/influencer/{username}
    API->>DB: Query username record
    alt Username not in DB
        DB-->>API: Not found
        API->>DB: Dynamically simulate & seed organic profile
    end
    API->>ML: Pass profile dictionary to Authenticity & Scorer models
    ML-->>API: Return bot audits, Prophet growth forecasts, SBERT matches
    API-->>UI: Deliver full scorecard JSON
    UI-->>User: Render Gauge indicators & follow curves

    User->>UI: Select live trending topic
    UI->>API: POST /api/content/agent-pipeline
    API->>Agent: Invoke Compiled StateGraph(topic)
    Agent->>ML: Claude Script generator & RF Virality Predictor
    ML-->>Agent: Compose script, captions, & predict views/likes
    Agent-->>API: Return final campaign state
    API-->>UI: Return unified response
    UI-->>User: Format highlighted script bands, copy socials, & show meters
```

---

## 🤖 3. Machine Learning Model Selection & Mathematical Justifications

### A. Bot & Fraud Detection: `IsolationForest`
*   **Why:** Follower fraud (bought followings and bot farms) does not have labeled supervision datasets. Standard supervised classification is impractical.
*   **Math:** Bots are outliers (anomalies) in high-dimensional feature spaces. `Isolation Forest` isolates anomalies by randomly partitioning feature ranges. Because anomalies require fewer splits to be isolated, they appear closer to the root of decision trees (shorter average path lengths $h(x)$).
*   **Features:** $[ER, \log_{10}(Followers/Following), SpikeScore]$. If a bot dump occurs, the spike score rises, producing low average paths, resulting in low Authenticity Scores.

### B. Follower Growth Forecasting: `FB Prophet`
*   **Why:** Traditional ARIMA models require strict stationary time-series data and do not handle sudden spikes or strong weekly social networking seasonality (e.g. higher engagements on weekends).
*   **Math:** Prophet models time-series as an additive regression:
    $$y(t) = g(t) + s(t) + h(t) + \epsilon_t$$
    where $g(t)$ represents non-periodic growth trends, $s(t)$ models weekly seasonality, and $h(t)$ incorporates outlier events. This captures organic creator scaling accurately.

### C. Campaign Brief Matching: `Sentence-BERT` (SBERT)
*   **Why:** Standard lexical search (TF-IDF/BM25) fails to capture semantic meaning (e.g. "active gym-wear brand" will not match a bio "weightlifter sharing nutrition tips" since there is no overlapping vocabulary).
*   **Math:** SBERT uses Siamese networks to project text sentences into a highly structured 384-dimensional vector space. Semantic similarity is calculated as the cosine between text embeddings $\vec{u}$ and $\vec{v}$:
    $$\text{Similarity} = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}$$
    yielding robust match relevance scores.

### D. Campaign Success: `XGBoost` / `GradientBoosting`
*   **Why:** XGBoost represents the gold-standard algorithm for tabular feature data. It consistently outperforms deep neural networks on low-dimensional structured records.
*   **Math:** It iteratively fits decision trees by minimizing an objective function containing an additive regularization term $\Omega(f_t)$ to penalize model complexity and prevent overfitting:
    $$\mathcal{L}^{(t)} = \sum_{i=1}^{n} l\left(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)\right) + \Omega(f_t)$$
    This outputs robust, highly accurate success probabilities.

### E. Script Virality Forecasting: `Random Forest Regressor`
*   **Why:** Virality is multi-variable (simultaneously predicting views, likes, and shares). It is dependent on low-cardinality script traits (intro hooks, CTA endings).
*   **Math:** `Random Forest Regressor` uses bootstrap aggregation (bagging) of numerous decorrelated decision trees, reducing forecasting variance and yielding robust expected metrics.

---

## 🔌 4. API Schema Reference

All JSON payloads standardise under the `BaseResponse` format:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

### Endpoints Catalog & Payload Schemas:

#### 1. `GET /`
*   **Purpose:** Backend API health status check.
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": {
        "status": "Online",
        "service": "Ratefluencer Core API Engine",
        "version": "1.0.0",
        "environment": "sqlite"
      },
      "error": null
    }
    ```

#### 2. `GET /api/influencer/{username}`
*   **Purpose:** Evaluates and audits a creator handle.
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": {
        "profile": {
          "id": 1,
          "username": "tech_creator_0",
          "category": "tech",
          "followers": 152000,
          "engagement_rate": 4.82,
          "growth_rate_30d": 12.4
        },
        "scores": {
          "authenticity_score": 95.5,
          "growth_score": 85.0,
          "ratefluencer_score": 88.2
        },
        "forecast": {
          "historical": [140000, 145000, 152000],
          "predicted": [155000, 158000, 162000]
        }
      },
      "error": null
    }
    ```

#### 3. `POST /api/influencer/analyze`
*   **Purpose:** Accepts manual creator JSON payloads to audit.
*   **Request Schema:**
    ```json
    {
      "username": "@tester",
      "followers": 25000,
      "avg_likes": 2000,
      "posting_frequency": 3.5,
      "follower_history_30d": [24000, 24500, 25000]
    }
    ```
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": {
        "authenticity_score": 91.2,
        "growth_score": 78.4,
        "ratefluencer_score": 84.1,
        "anomalies_detected": false
      },
      "error": null
    }
    ```

#### 4. `GET /api/influencer/{id}/brand-matches`
*   **Purpose:** Gets top 5 matching product campaigns for a creator.
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": [
        {
          "brand_id": 1,
          "name": "FitTrack Pro",
          "industry": "fitness",
          "match_percentage": 95.8,
          "aesthetic": "minimalist, data-driven"
        },
        {
          "brand_id": 4,
          "name": "CodeLab IDE",
          "industry": "tech",
          "match_percentage": 82.3,
          "aesthetic": "developer-focused"
        }
      ],
      "error": null
    }
    ```

#### 5. `POST /api/influencer/search-by-brief`
*   **Purpose:** Matches all DB creators against a written campaign brief.
*   **Request Schema:**
    ```json
    {
      "brief": "Seeking fitness professionals to advertise wearable smart bands."
    }
    ```
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": [
        {
          "username": "@fit_coach",
          "category": "fitness",
          "match_score": 94.2,
          "bio": "Certified strength trainer sharing evidence-based fitness programs."
        },
        {
          "username": "@health_bytes",
          "category": "fitness",
          "match_score": 88.5,
          "bio": "High-intensity training workouts and macro tracking templates."
        }
      ],
      "error": null
    }
    ```

#### 6. `GET /api/trends`
*   **Purpose:** Live crawls and ranks top trending topics.
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": [
        {
          "topic": "GPT-5 reasoning capabilities",
          "category": "tech",
          "trend_score": 98.2,
          "growth_velocity": 4.5
        },
        {
          "topic": "DeFi yield structures in 2026",
          "category": "finance",
          "trend_score": 91.5,
          "growth_velocity": 3.2
        }
      ],
      "error": null
    }
    ```

#### 7. `POST /api/trends/score`
*   **Purpose:** Scores a custom topic string.
*   **Request Schema:**
    ```json
    {
      "topic": "Autonomous AI developer agents"
    }
    ```
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": {
        "topic": "Autonomous AI developer agents",
        "trend_score": 84.60,
        "is_viral_candidate": true
      },
      "error": null
    }
    ```

#### 8. `POST /api/content/agent-pipeline`
*   **Purpose:** Triggers the multi-node LangGraph sequential agent.
*   **Request Schema:**
    ```json
    {
      "topic": "GPT-5 reasoning",
      "category": "tech"
    }
    ```
*   **Response Payload:**
    ```json
    {
      "success": true,
      "data": {
        "topic": "GPT-5 reasoning",
        "category": "tech",
        "script": "[HOOK] The standard coding assistant is officially obsolete... [STORY] With the release of GPT-5 reasoning engines, the AI can now plan entire directories... [INSIGHTS] Developers are transitioning from typing out syntax to orchestrating system architectures... [CTA] Subscribe for more deep dives into the AI agent coding stack!",
        "linkedin_post": "GPT-5 is rewriting the rules of software development. It's not just about code suggestions anymore; it's about reasoning chains...",
        "instagram_caption": "GPT-5 reasoning is here. Are you ready? 🤖💡 #AI #SoftwareEngineer #GPT5 #FutureOfWork",
        "virality_score": 79.50,
        "expected_performance": {
          "views": 84000,
          "likes": 5600,
          "shares": 920
        }
      },
      "error": null
    }
    ```
