# Churn AI Retention Platform 🚀

This project is a customer churn retention platform that combines machine learning, data engineering, and generative AI to identify high-risk customers, generate retention strategies, and produce personalized email content.

## 📁 Project Structure

| Component | Path | Purpose |
|---|---|---|
| Streamlit UI | `app/streamlit_app.py` | Web dashboard to run the pipeline, configure parameters, view results, and read historical records. |
| Churn prediction | `src/predict.py` | Load the trained model and encoders, preprocess raw customer data, and calculate churn risk probabilities. |
| Pipeline orchestration | `src/pipeline.py` | Control the full flow: prediction, selection, LLM calls, persistence, and output export. |
| LLM agents | `src/llm_agents.py` | Generate retention strategies and customer emails through the Groq API. |
| Local DB | `src/database/db.py` | Save pipeline output to SQLite and retrieve result history. |
| Raw data | `data/telco.csv` | Original customer dataset used for scoring and profile extraction. |
| Model artifacts | `models/` | Saved `XGBClassifier` model and label encoders required for prediction. |

## 🧠 Technical Stack

| Layer | Technology | Description |
|---|---|---|
| Frontend | Streamlit | Simple Python dashboard for user input, progress feedback, charts, and data tables. |
| Data processing | pandas | Read CSV, preprocess records, select top customers, and structure predictions. |
| Machine Learning | XGBoost, scikit-learn | Trained churn model with categorical encoding and probability-based scoring. |
| Generative AI | Groq API | Two prompt-based agents produce retention strategy text and a persuasive email. |
| Storage | SQLite | Local embedded database for history and auditability. |
| Containerization | Docker | Packaging the app for repeatable deployment with a lightweight Python image. |

## 🔄 Pipeline Flow

1. Read customer data from `data/telco.csv`.
2. Preprocess the raw dataset:
   - remove missing values
   - encode categorical features
   - map churn labels to numeric values
3. Load the trained churn model from `models/churn_model.pkl`.
4. Predict the churn probability for each customer and save to `data/churn_scores.csv`.
5. Filter customers whose risk score exceeds the user-selected threshold.
6. For each high-risk customer:
   - build a profile context from their contract, service, and billing data
   - call `strategist_agent()` to generate a retention recommendation
   - call `writer_agent()` to generate a short email message
7. Save each customer result into SQLite via `src/database/db.py`.
8. Export the pipeline output to a timestamped CSV file under `data/output/`.

## 🛠️ Docker and Deployment

This project includes a Docker setup for consistent runtime environments.

### Dockerfile overview

- Uses `python:3.11-slim-bookworm` as the base image.
- Installs dependencies from `requirements.txt`.
- Copies the full project into `/app`.
- Runs Streamlit as a non-root user.
- Exposes port `8501` for the web interface.

### docker-compose.yml

The compose file defines a single service:

- `churn-app`: builds the application image, mounts the repository into the container, and maps host port `8501` to the container.

### Run with Docker

```bash
docker compose up --build
```

Then open:

```bash
http://localhost:8501
```

## ⚙️ How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add `.env` with your Groq API key:
   ```text
   GROQ_API_KEY=your_api_key_here
   ```
3. Start the Streamlit app:
   ```bash
   streamlit run app/streamlit_app.py
   ```
4. Use the sidebar to set the risk threshold and customer limit, then click **Run Pipeline**.

## ✅ Notes and Improvements

- The Streamlit app preserves result state in `st.session_state` so data remains available during a session.
- The pipeline stores results in `db/churn.db` and presents history in the UI.
- LLM calls include retry logic for temporary API failures.
- Output files are saved with timestamps to support versioned exports.
- Comments were added throughout the source code to clearly explain each step in English.
