FROM python:3.11-slim

WORKDIR /app

# Copy frontend requirements only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "frontend_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
