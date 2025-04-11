import pandas as pd # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore
from sklearn.preprocessing import OneHotEncoder # type: ignore
import pickle

print("Starting script...")

# Load and preprocess data
try:
    df = pd.read_csv("imdb_top_1000.csv")
    print("CSV loaded successfully. Shape:", df.shape)
except FileNotFoundError:
    print("Error: imdb_top_1000.csv not found in Implementation folder!")
    exit(1)

# Clean data
df["Gross"] = df["Gross"].str.replace(",", "").fillna(0).astype(float) / 1e6
df["Runtime"] = df["Runtime"].str.extract(r"(\d+)").astype(float)
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
df = df.dropna(subset=["Released_Year"])
df["Released_Year"] = df["Released_Year"].astype(int)
df["Meta_score"] = df["Meta_score"].fillna(df["Meta_score"].mode()[0])
df["Genre"] = df["Genre"].str.split(",").str[0].str.strip()
print("Data cleaned. Shape after cleaning:", df.shape)

# Define success categories
def classify_success(row):
    if row["Gross"] > 100 and row["IMDB_Rating"] >= 8.0:
        return "Hit"
    elif row["Gross"] < 20 and row["IMDB_Rating"] < 7.0:
        return "Flop"
    else:
        return "Average"

df["Success_Category"] = df.apply(classify_success, axis=1)
print("Success categories assigned.")

# Features and target
features = ["Runtime", "Meta_score", "Released_Year", "Genre"]
X = df[features]
y = df["Success_Category"]

# Encode categorical data (Genre)
encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
genre_encoded = encoder.fit_transform(X[["Genre"]])
genre_df = pd.DataFrame(genre_encoded, columns=encoder.get_feature_names_out(["Genre"]))
X_encoded = pd.concat([X[["Runtime", "Meta_score", "Released_Year"]].reset_index(drop=True), genre_df], axis=1)
print("Features encoded. Shape of X_encoded:", X_encoded.shape)

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("Model trained.")

# Save model and encoder
with open("success_predictor_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("genre_encoder.pkl", "wb") as f:
    pickle.dump(encoder, f)
print("Model and encoder saved as success_predictor_model.pkl and genre_encoder.pkl")

# Evaluate model
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.2f}")
print("Category Distribution in Training Data:")
print(df["Success_Category"].value_counts())
print("Script completed successfully!")