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

To run the backend tests:
```bash
pytest tests/
```

To run performance tests:
```bash
python tests/performance_test.py
```

## 📁 Project Structure

- `backend/`: FastAPI application handling API requests and auth.
- `frontend/`: React + Vite application for the user interface.
- `worker/`: Background worker for processing images using YOLO.
- `models/`: Directory for storing YOLO model weights.
- `tests/`: Integration and performance testing suite.

## 🛡️ License

This project is licensed under the MIT License.
