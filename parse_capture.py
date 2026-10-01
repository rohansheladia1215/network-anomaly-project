import pyshark
from collections import defaultdict
import pandas as pd

window_counts = defaultdict(int)
window_bytes = defaultdict(int)

capture = pyshark.FileCapture('capture1.pcapng', keep_packets=False)

for packet in capture:
    timestamp = float(packet.sniff_timestamp)
    window = int(timestamp)
    window_counts[window] += 1
    window_bytes[window] += int(packet.length)

capture.close()

windows = sorted(window_counts.keys())
data = {
    "second": windows,
    "packet_count": [window_counts[w] for w in windows],
    "byte_count": [window_bytes[w] for w in windows],
}

df = pd.DataFrame(data)
df.to_csv("network_features.csv", index=False)
print(df.head(20))
print(f"\nTotal seconds captured: {len(df)}")

from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly"] = model.fit_predict(df[["packet_count", "byte_count"]])

anomalies = df[df["anomaly"] == -1]
print("\nDetected anomalies:")
print(anomalies)

import matplotlib.pyplot as plt

plt.figure(figsize=(14, 5))
plt.plot(df["second"], df["packet_count"], label="Packet count", color="steelblue")
plt.scatter(anomalies["second"], anomalies["packet_count"], color="red", label="Detected anomaly", zorder=5)
plt.xlabel("Time (seconds since capture start)")
plt.ylabel("Packets per second")
plt.title("Network Traffic with Detected Anomalies")
plt.legend()
plt.tight_layout()
plt.savefig("traffic_anomalies.png")
print("\nSaved chart to traffic_anomalies.png")