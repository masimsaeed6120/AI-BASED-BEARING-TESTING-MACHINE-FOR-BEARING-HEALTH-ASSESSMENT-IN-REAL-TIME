import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier

# Load features
df = pd.read_csv("features.csv")





# Separate features and labels
X = df.drop(columns=["file", "label"])
y = df["label"]

# Train Random Forest
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)
model.fit(X, y)
# Save model
joblib.dump(model, "models/random_forest_model.pkl")

print("Model trained successfully.")
print("Model saved to:")
print("models/random_forest_model.pkl")