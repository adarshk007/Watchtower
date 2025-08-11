import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===== CONFIG =====
INPUT_FILE = "cloudwatch_logs.csv"  # Can be .csv or .json
FILE_TYPE = "csv"  # "csv" or "json"

# ===== LOAD DATA =====
if FILE_TYPE == "csv":
    df = pd.read_csv(INPUT_FILE)
elif FILE_TYPE == "json":
    df = pd.read_json(INPUT_FILE, lines=True)
else:
    raise ValueError("FILE_TYPE must be 'csv' or 'json'")

# Ensure correct types
df["@timestamp"] = pd.to_datetime(df["@timestamp"], errors="coerce")
df["@duration"] = pd.to_numeric(df["@duration"], errors="coerce")

# Drop missing duration rows
df = df.dropna(subset=["@duration", "@timestamp"])

# ===== CALCULATE STATS =====
stats = {
    "count": len(df),
    "min": df["@duration"].min(),
    "max": df["@duration"].max(),
    "mean": df["@duration"].mean(),
    "median": df["@duration"].median(),
    "p95": np.percentile(df["@duration"], 95),
    "p99": np.percentile(df["@duration"], 99),
    "last_value": df.iloc[-1]["@duration"] if not df.empty else None
}

# Calculate percentage of requests above thresholds
stats["%>p95"] = (df["@duration"] > stats["p95"]).mean() * 100
stats["%>p99"] = (df["@duration"] > stats["p99"]).mean() * 100

print("===== PERFORMANCE SUMMARY =====")
for k, v in stats.items():
    if isinstance(v, float):
        print(f"{k}: {v:.2f}")
    else:
        print(f"{k}: {v}")

# ===== CREATE GRAPHS =====

# 1. Duration over time
plt.figure(figsize=(10,5))
plt.plot(df["@timestamp"], df["@duration"], marker="o", markersize=3, linestyle="-")
plt.title("Execution Duration Over Time")
plt.xlabel("Timestamp")
plt.ylabel("Duration (ms)")
plt.grid(True)
plt.tight_layout()
plt.savefig("duration_over_time.png")

# 2. Percentiles over time (rolling window)
df_sorted = df.sort_values("@timestamp")
df_sorted["p95_rolling"] = df_sorted["@duration"].rolling(window=50).apply(lambda x: np.percentile(x, 95))
df_sorted["p99_rolling"] = df_sorted["@duration"].rolling(window=50).apply(lambda x: np.percentile(x, 99))
plt.figure(figsize=(10,5))
plt.plot(df_sorted["@timestamp"], df_sorted["p95_rolling"], label="P95", color="orange")
plt.plot(df_sorted["@timestamp"], df_sorted["p99_rolling"], label="P99", color="red")
plt.title("Rolling Percentiles Over Time")
plt.xlabel("Timestamp")
plt.ylabel("Duration (ms)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("percentiles_over_time.png")

# 3. Histogram of durations
plt.figure(figsize=(8,5))
plt.hist(df["@duration"], bins=30, edgecolor="black")
plt.title("Duration Distribution")
plt.xlabel("Duration (ms)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("duration_distribution.png")

# 4. Requests per minute
df["minute"] = df["@timestamp"].dt.floor("T")
req_per_min = df.groupby("minute").size()
plt.figure(figsize=(10,5))
req_per_min.plot(kind="line")
plt.title("Requests per Minute")
plt.ylabel("Count")
plt.grid(True)
plt.tight_layout()
plt.savefig("requests_per_minute.png")

print("\nGraphs saved as:")
print("- duration_over_time.png")
print("- percentiles_over_time.png")
print("- duration_distribution.png")
print("- requests_per_minute.png")
