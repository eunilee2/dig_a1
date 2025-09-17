import pandas as pd
import json

df_overdose = pd.read_csv('data/fatal_overdoses_2007_2025.csv')

# Data overview
# print(df_overdose.head()) # View the first few rows
# print(df_overdose.info()) # Get a summary of the DataFrame, including data types and non-null counts
# print(df_overdose.describe()) # Get descriptive statistics for numerical columns

# Check for missing values
# print(df_overdose.isnull().sum())

# Drop rows where 'incident_zip' or 'race' is missing (NaN or blank)
# df = df_overdose.dropna(subset=['incident_zip', 'race'])
# df = df[(df['incident_zip'].astype(str).str.strip() != '') & (df['race'].astype(str).str.strip() != '')]

# Save the cleaned data
# df.to_csv('fatal_overdoses_2007_2025_cleaned.csv', index=False)

# Load data
overdose_data = pd.read_csv("./data/fatal_overdoses_2007_2025_cleaned.csv")
with open("./data/allegheny-county-zip-code-boundaries.geojson") as f:
    geojson_data = json.load(f)

# Valid Allegheny zips
allegheny_zips = {feature["properties"]["ZIP"].zfill(5) for feature in geojson_data["features"]}
print(f"Valid Allegheny Zips: {allegheny_zips}")

# Normalize and classify zips
overdose_data["incident_zip"] = overdose_data["incident_zip"].astype(str).str.zfill(5)
overdose_data["zip_status"] = overdose_data["incident_zip"].apply(
    lambda z: "Allegheny" if z in allegheny_zips else "Extraneous"
)

# Filter for Datawrapper
allegheny_only = overdose_data[overdose_data["zip_status"] == "Allegheny"]

# Save outputs
allegheny_only.to_csv("./data/fatal_overdoses_allegheny_only.csv", index=False)  # Datawrapper use