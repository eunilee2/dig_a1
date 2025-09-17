import pandas as pd

# Load your data
df = pd.read_csv("fatal_overdoses_allegheny_only.csv")

# List of drug columns to unpivot
drug_cols = [f"combined_od{i}" for i in range(1, 11)]

# Melt the dataframe to long format
df_long = df.melt(
    id_vars=[col for col in df.columns if col not in drug_cols],
    value_vars=drug_cols,
    var_name="drug_col",
    value_name="drug"
)

# Drop rows where drug is missing or empty
df_long = df_long[df_long["drug"].notna() & (df_long["drug"] != "")]

# Optionally, drop the 'drug_col' column if you don't need to know which slot it came from
df_long = df_long.drop(columns=["drug_col"])

# Save to a new CSV
df_long.to_csv("fatal_overdoses_allegheny_only_long.csv", index=False)