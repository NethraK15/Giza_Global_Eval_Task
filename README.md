# PID Parser SaaS

A full-stack SaaS application for parsing PIDs using YOLO models, built with FastAPI, React, and Redis.

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

Ensure you have the following installed:
- [Docker](https://www.docker.com/products/docker-desktop/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (v18+ recommended)
- [Python](https://www.python.org/) (3.9+ recommended)

### 🛠️ Quick Start with Docker

The easiest way to start all services (Backend, Frontend, Worker, Database, Redis, MinIO) is using Docker Compose. The backend will automatically create the necessary database tables and storage buckets on startup.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd pid-parser-saas
    ```

2.  **Set up environment variables:**
    Copy the example environment file to `.env`:
    ```bash
    cp .env.example .env
    ```

3.  **Run with Docker Compose:**
    ```bash
    docker compose up --build
    ```

All services will be available at:
- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **MinIO Console:** [http://localhost:9001](http://localhost:9001)

### 🛑 Shutting Down Docker

To stop the services and clean up resources, use the following commands:

- **Stop all services:**
  ```bash
  docker compose stop
  ```
- **Stop and remove containers, networks, and images:**
  ```bash
  docker compose down
  ```
- **Complete cleanup (including data volumes/database):**
  ```bash
  docker compose down -v
  ```

---

### 🌐 Ngrok Tunnel Setup

The application is also accessible via ngrok for external access or testing:
- **Public URL:** [https://uncharmable-nonvexatiously-leonie.ngrok-free.dev](https://uncharmable-nonvexatiously-leonie.ngrok-free.dev)

To start the tunnel manually for the frontend:
```bash
ngrok http 5173 --host-header=rewrite
```

---

### 💻 Manual Setup (Local Development)

If you prefer to run services individually without Docker:

#### 1. Infrastructure (Required)
You still need Redis and PostgreSQL. You can run just them using:
```bash
docker compose up db redis minio -d
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 3. Worker Setup
```bash
cd worker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Sample Credentials

Use these credentials to log in to the application:

- **Email:** `abc@gmail.com`
- **Password:** `qwertyu`

---

## 🧪 Testing

The project includes a comprehensive suite of integration, end-to-end, and performance tests.

### 1. Backend Integration Tests
Validates API endpoints, authentication, and job processing flows.
```bash
pytest tests/test_backend.py
```

### 2. Frontend E2E Tests (Playwright)
Automated browser tests covering the full user journey from signup to image processing results.
```bash
# Ensure containers are running first
pytest tests/test_frontend.py
```

### 3. Performance & Load Testing
Measures system throughput, latency (p50/p95), and worker utilization.
```bash
# Enqueue 100 jobs for testing
python tests/load_test_enqueue.py

# Calculate metrics from logs
# (Refer to PERFORMANCE_TESTING.md for detailed steps)
python tests/calculate_metrics.py
```

For a detailed test execution report, see `TEST_REPORT.md`.

---

## 📊 Capacity & Scaling

The system is designed to handle high loads efficiently. Based on current benchmarks:

- **Peak Capacity:** ~0.35 Jobs/sec with a single worker.
- **Worker Utilization:** A single worker instance can handle 1,000 daily jobs at ~45% utilization.
- **Storage Consumption:** ~3.66 MB per job (including original image, overlay, and CSV).
- **Scale-out Threshold:** Recommended to add a second worker instance once DAU exceeds 1,500.

For detailed calculations and rationale, see `CAPACITY_REPORT.md`.

## 📁 Project Structure

- `backend/`: FastAPI application handling API requests and auth.
- `frontend/`: React + Vite application for the user interface.
- `worker/`: Background worker for processing images using YOLO.
- `models/`: Directory for storing YOLO model weights.
- `tests/`: Integration and performance testing suite.

## 🛡️ License

This project is licensed under the MIT License.
