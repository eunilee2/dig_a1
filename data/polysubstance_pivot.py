import pandas as pd

df = pd.read_csv("fatal_overdoses_allegheny_only.csv")
drug_cols = [f"combined_od{i}" for i in range(1, 11)]

# Count non-empty drugs per case
df["drug_count"] = df[drug_cols].notna().sum(axis=1) - (df[drug_cols] == '').sum(axis=1)
df["drug_case_type"] = df["drug_count"].apply(lambda x: "Single" if x == 1 else "Poly" if x > 1 else "None")

# Save for visualization
df.to_csv("fatal_overdoses_allegheny_only_drugtype.csv", index=False)