FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

EXPOSE 8000
CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8000"]
