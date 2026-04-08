import pandas as pd
import joblib

# Load the trained churn model and label encoders from disk.
model = joblib.load("models/churn_model.pkl")
encoders = joblib.load("models/encoders.pkl")

def preprocess(df):
    """Prepare the raw customer data for model prediction."""
    df = df.dropna()

    # Keep the original IDs so we can attach them back to the score output.
    ids = df["customerID"]

    # Remove the ID column before model prediction.
    df = df.drop(columns=["customerID"])

    # Convert churn labels from text to numeric values.
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    # Apply the saved label encoders to all categorical columns.
    for col, le in encoders.items():
        df[col] = le.transform(df[col])

    return df, ids

def predict_churn():
    """Read the data, run the churn prediction model, and return risk scores."""
    df = pd.read_csv("data/telco.csv")

    df_processed, ids = preprocess(df)

    # Predict the probability of churn for each customer.
    probs = model.predict_proba(df_processed.drop("Churn", axis=1))[:, 1]

    result = pd.DataFrame({
        "customerID": ids,
        "risk_score": probs
    })

    # Save the churn scores to a CSV file for auditing and reuse.
    result.to_csv("data/churn_scores.csv", index=False)

    return result

if __name__ == "__main__":
    predict_churn()