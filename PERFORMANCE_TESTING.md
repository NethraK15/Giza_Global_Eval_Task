# Performance Measurement Guide

This guide describes how to measure the inference performance and resource usage of the PID Parser worker.

## 1. Enqueue 100 Jobs
Run the provided load test script to saturate the worker queue:
```powershell
python tests/load_test_enqueue.py
```

## 2. Extraction of Latency Values
Extract the `latency_ms` values from the worker's JSON logs. This command looks for logs containing "Inference complete" and parses out the latency:

```powershell
# Using PowerShell to extract latency_ms from Docker logs
docker compose logs worker | Select-String "inference_complete" | ForEach-Object { $obj = $_.ToString() | ConvertFrom-Json; $obj.latency_ms } > latencies.txt
```

## 3. Python Snippet for p50 and p95
Create a file named `tests/calculate_metrics.py`:

```python
import numpy as np

def calculate_percentiles(file_path):
    with open(file_path, 'r') as f:
        latencies = [float(line.strip()) for line in f if line.strip()]
    
    if not latencies:
        print("No latencies found.")
        return

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    
    print(f"p50 (Median): {p50:.2f} ms")
    print(f"p95:          {p95:.2f} ms")
    print(f"Count:        {len(latencies)} samples")

if __name__ == "__main__":
    calculate_percentiles("latencies.txt")
```

## 4. Measure Peak Memory Usage
While the 100 jobs are processing, run this command in a separate terminal to monitor the worker's memory:

```powershell
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
```
*Note: To capture the peak, you should run `docker stats` without the `--no-stream` flag and observe it during the run.*

## 5. Calculate Throughput
Throughput (Jobs Per Second) should be calculated based on the total processing time of the batch:

**Formula:** `Throughput = Total Jobs / (T_end - T_start)`

To get `T_start` and `T_end` from logs:
```powershell
# Get start time of first job in batch
docker compose logs worker | Select-String "Processing job" | Select-Object -First 1

# Get end time of last job in batch
docker compose logs worker | Select-String "Job .* succeeded" | Select-Object -Last 1
```
Subtract the timestamps and divide the number of jobs (100) by that duration.
