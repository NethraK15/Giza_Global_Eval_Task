
# Capacity Planning and Performance Analysis Report

## 1. Input Assumptions
| Parameter | Value | Unit |
| :--- | :--- | :--- |
| **Total Users** | 1,000 | Users |
| **Daily Active Users (DAU)** | 100 (10%) | Users |
| **Uploads per DAU per Day** | 10 | Uploads |
| **Retention Period** | 30 | Days |
| **Active Window** | 8 | Hours/Day |
| **Peak Factor** | 10 | x |
| **Target Worker Utilization** | 70 | % |
| **User Storage Quota** | 5 | GB |

## 2. Observed Metrics (from Current Test Set)
| Metric | Value | Unit | Rationale |
| :--- | :--- | :--- | :--- |
| **p95 Inference Time** | 1,296.61 | ms | Worker log analysis (p95) |
| **Avg. Input Size** | 1.83 | MB | Observed `size_test.png` |
| **Avg. Overlay Size** | 1.83 | MB | Observed artifact |
| **Avg. CSV Size** | 0.03 | KB | Observed artifact |

## 3. Detailed Calculations

### A. Traffic & Throughput
- **Daily Jobs** = 100 DAU × 10 uploads = **1,000 Jobs/Day**
- **Active Window (Seconds)** = 8 hours × 3600 = **28,800 Seconds**
- **Avg. Jobs per Second** = 1,000 / 28,800 = **0.0347 Jobs/sec**
- **Peak Jobs per Second** = 0.0347 × 10 = **0.347 Jobs/sec**

### B. Worker Scaling
- **p95 Inference (Seconds)** = 1.30 Seconds
- **Required Workers** = (Peak 0.3472 Jobs/sec × 1.30s) / 0.70 = **0.64 Workers**
- **Conclusion**: A single worker instance can handle the peak load at ~45% utilization.

### C. Data Volume
- **Bytes per Job** = 1.83 (Input) + 1.83 (Overlay) + 0.00003 (CSV) = **3.66 MB/Job**
- **Daily Ingress** = 1,000 Jobs × 1.83 MB = **1.83 GB/Day**
- **Daily Egress** = 1,000 Jobs × (1.83 + 0.00003) MB = **1.83 GB/Day**
- **Total Storage (30d Retention)** = 1,000 Jobs × 3.66 MB × 30 Days = **110.1 GB**
- **Maximum Possible Quota Storage** = 1,000 Users × 5 GB = **5,000 GB (5 TB)**

## 4. Final Capacity Summary
- **Daily Combined Data Flow**: 3.66 GB
- **Monthly Storage Consumption**: 110.1 GB
- **Recommended Minimum Workers**: 1 (Single instance)
- **Scale-out Threshold**: Add second worker if DAU exceeds 1,500 or Peak Factor exceeds 15x.
