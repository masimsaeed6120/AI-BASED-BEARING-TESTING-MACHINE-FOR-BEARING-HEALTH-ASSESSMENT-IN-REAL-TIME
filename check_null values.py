import pandas as pd

df = pd.read_csv("features.csv")

print("NaN check")
print("=" * 40)

nan_counts = df.isna().sum()

print("\nFeatures containing NaN:")
print(nan_counts[nan_counts > 0])

print("\nRows containing NaN:")

nan_rows = df[df.isna().any(axis=1)]

print(nan_rows[["file", "label"]].to_string(index=False))

print("\nTotal rows with NaN:", len(nan_rows))