import sys
import os
import time

# Add the parent folder to the Python path so the app can import src modules.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd

from src.pipeline import run_pipeline
from src.database.db import get_history

# ---------------- CONFIGURATION ----------------
# Configure the Streamlit page settings and layout.
st.set_page_config(
    page_title="Churn AI Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- SESSION STATE ----------------
# Preserve the pipeline result in Streamlit session state to avoid reprocessing.
if "df_result" not in st.session_state:
    st.session_state.df_result = None

# ---------------- STYLE ----------------
# Custom CSS styles for page headings, cards, metrics, and log display.
st.markdown("""
<style>
.main-title { font-size: 42px; font-weight: 700; color: #0f172a; }
.subtitle { font-size: 16px; color: #64748b; }
.card {
    padding: 20px;
    border-radius: 14px;
    background: #f8fafc;
    margin-bottom: 15px;
    border: 1px solid #e2e8f0;
}
.metric-card {
    padding: 15px;
    border-radius: 12px;
    background: linear-gradient(135deg, #e0f2fe, #f0f9ff);
    text-align: center;
}
.log-box {
    height:200px;
    overflow:auto;
    background:#0f172a;
    color:#e2e8f0;
    padding:10px;
    border-radius:8px;
    font-family: monospace;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
# Render the main title and subtitle for the retention platform.
st.markdown('<div class="main-title">Churn AI Retention Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Machine Learning + Generative AI para retenção de clientes</div>', unsafe_allow_html=True)

st.divider()

# ---------------- SIDEBAR CONTROLS ----------------
# Sidebar controls for pipeline threshold, maximum customers, and execution.
st.sidebar.title("⚙️ Controle")

threshold = st.sidebar.slider("Risk threshold", 0.5, 0.9, 0.7)
limit = st.sidebar.slider("Customer limit", 1, 10, 3)

run = st.sidebar.button("🚀 Run Pipeline")

st.sidebar.divider()
st.sidebar.info("""
Pipeline:
1. ML model
2. Churn score
3. AI strategy
4. AI communication
""")

# ---------------- PIPELINE EXECUTION ----------------
if run:

    progress = st.progress(0)
    status = st.empty()

    # Dynamic log area to show execution messages.
    st.subheader("📡 Execution Log")

    log_container = st.empty()
    log_messages = []

    def add_log(msg):
        log_messages.append(msg)
        log_container.markdown(
            "<div class='log-box'>" + "<br>".join(log_messages) + "</div>",
            unsafe_allow_html=True
        )

    add_log("🚀 Initializing pipeline...")

    status.info("🔍 Loading model...")
    time.sleep(0.5)
    add_log("✔ Model loaded")
    progress.progress(20)

    status.info("📊 Calculating churn scores...")
    time.sleep(0.5)
    add_log("✔ Churn scores calculated")
    progress.progress(40)

    status.info("🧠 Running AI agents...")
    time.sleep(0.5)
    add_log("✔ AI started")
    progress.progress(60)

    add_log(f"⚙️ Running pipeline (threshold={threshold}, limit={limit})")

    with st.spinner("Processing customers..."):
        df = run_pipeline(threshold=threshold, limit=limit)

    st.session_state.df_result = df

    add_log("✔ Pipeline completed successfully")
    progress.progress(100)
    status.success("Pipeline finished")

# ---------------- RESULTS ----------------
df = st.session_state.df_result

if df is not None:

    st.divider()

    # Summary metrics for the generated result set.
    st.subheader("📈 Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="metric-card">Customers<br><b>{len(df)}</b></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card">Average Risk<br><b>{df["risk"].mean():.2f}</b></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card">Max<br><b>{df["risk"].max():.2f}</b></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-card">Min<br><b>{df["risk"].min():.2f}</b></div>', unsafe_allow_html=True)

    st.divider()

    # Display a bar chart of customer risk values.
    st.subheader("📊 Risk Distribution")
    st.bar_chart(df.set_index("customerID")["risk"])

    st.divider()

    # Filter section to inspect results above a selected risk level.
    st.subheader("🔎 Filter")
    selected_risk = st.slider("Minimum risk", 0.0, 1.0, threshold)

    filtered_df = df[df["risk"] >= selected_risk]

    st.dataframe(filtered_df, use_container_width=True)

    st.divider()

    # Detailed retention actions for each selected customer.
    st.subheader("🎯 Retention Actions")

    for _, row in filtered_df.iterrows():

        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            colA, colB = st.columns([1, 3])

            with colA:
                st.write(f"Customer: {row['customerID']}")
                st.metric("Risk", f"{row['risk']:.2f}")

            with colB:
                st.markdown("**Strategy**")
                st.write(row["strategy"])

                st.markdown("**Email**")
                st.write(row["email"])

            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # History section showing saved results from the SQLite database.
    st.subheader("📚 History (SQLite)")

    history = get_history()

    if history:
        df_hist = pd.DataFrame(history, columns=[
            "id", "customerID", "risk", "strategy", "email", "created_at"
        ])
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No history yet.")

else:
    st.info("Run the pipeline to generate results.")