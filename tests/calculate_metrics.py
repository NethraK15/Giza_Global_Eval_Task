import numpy as np
import os
import sys

def calculate_percentiles(file_path):
    if not os.path.exists(file_path):
        print("Error: File not found")
        return

    latencies = []
    with open(file_path, 'rb') as f:
        data = f.read()
        # Clean data: keep only numbers, dots, and newlines
        cleaned = "".join(chr(b) for b in data if (48 <= b <= 57) or b == 46 or b == 10 or b == 13)
        for line in cleaned.splitlines():
            if line.strip():
                try:
                    latencies.append(float(line.strip()))
                except:
                    continue
    
    if not latencies:
        print("No latencies")
        return

    print(f"Count: {len(latencies)}")
    print(f"p50: {np.percentile(latencies, 50):.2f}")
    print(f"p95: {np.percentile(latencies, 95):.2f}")

if __name__ == "__main__":
    calculate_percentiles("latencies.txt")