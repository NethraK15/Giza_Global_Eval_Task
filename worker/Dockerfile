FROM python:3.10-slim

WORKDIR /worker

COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "worker.py"]
