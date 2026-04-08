import pandas as pd
import time
from datetime import datetime

from src.predict import predict_churn
from src.llm_agents import strategist_agent, writer_agent
from src.database.db import insert_result, create_table


def build_context(df, customer_id):
    """Build a text context for the given customer using their profile data."""
    cliente = df[df["customerID"] == customer_id].iloc[0]

    context = f"""
    Customer profile:
    - Tenure: {cliente['tenure']} months
    - Contract type: {cliente['Contract']}
    - Internet service: {cliente['InternetService']}
    - Monthly charge: {cliente['MonthlyCharges']}
    """

    return context


def run_pipeline(threshold=0.7, limit=3):
    """Run the full churn pipeline and return the generated retention recommendations."""
    print("Starting pipeline...")

    # Ensure the database table exists before inserting results.
    create_table()

    # Run churn prediction and load the raw customer data.
    scores = predict_churn()
    base = pd.read_csv("data/telco.csv")

    # Keep only the top customers above the risk threshold.
    high_risk = scores[scores["risk_score"] > threshold].head(limit)

    results = []

    for _, row in high_risk.iterrows():
        print(f"Processing customer {row['customerID']}...")

        # Build a profile context for the LLM agents.
        context = build_context(base, row["customerID"])

        # Generate a retention strategy using the strategist LLM.
        strategy = strategist_agent(context)
        time.sleep(2)

        # Generate a personalized email using the writer LLM.
        email = writer_agent(strategy)
        time.sleep(2)

        # Save each result into the SQLite database.
        insert_result(
            customerID=row["customerID"],
            risk=row["risk_score"],
            strategy=strategy,
            email=email
        )

        results.append({
            "customerID": row["customerID"],
            "risk": row["risk_score"],
            "strategy": strategy,
            "email": email
        })

    df = pd.DataFrame(results)

    # Save the result CSV with a timestamp for version tracking.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/output/result_{timestamp}.csv"

    import os
    os.makedirs("data/output", exist_ok=True)

    df.to_csv(output_path, index=False)

    print(f"Pipeline completed. Output saved to {output_path}")

    return df


if __name__ == "__main__":
    run_pipeline()