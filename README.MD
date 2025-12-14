# Chat Over Tabular Data (Text-to-SQL RAG)

This repository contains a complete solution to the task “Build a Chat Over Tabular Data (RAG-style)”.

The system answers natural-language questions over structured Excel data using a Text-to-SQL RAG architecture:

1. A user asks a question in natural language
2. An LLM translates the question into SQL
3. The SQL is executed on an in-memory SQLite database
4. The retrieved rows and aggregates are passed back to the LLM
5. The final answer is generated strictly grounded in the retrieved data

## The Project

The project is implemented as a multi-service application with:
- A FastAPI backend
- A Streamlit frontend
- An optional CLI client
- Full Docker + Docker Compose setup

## Data

The system operates on the following Excel files (included in the repository):
- `Clients.xlsx` – client information (name, industry, country)
- `Invoices.xlsx` – invoice headers (dates, status, currency, FX rates)
- `InvoiceLineItems.xlsx` – invoice line items (service name, quantity, unit price, tax rate)

All data fits in memory, as assumed by the task.

## What the System Can Answer

The chat can answer questions such as:
- List all clients with their industries.
- Which clients are based in the UK?
- List all invoices issued in March 2024 with their statuses.
- Which invoices are currently marked as "Overdue"?
- For each `service_name`, how many line items are there?
- List all invoices for Acme Corp with invoice IDs, dates, due dates, and statuses.
- Show all invoices issued to Bright Legal in February 2024.
- For invoice I1001, list all line items and compute totals including tax.
- For each client, compute the total amount billed in 2024 (including tax).
- Which client has the highest total billed amount in 2024?

These questions are not hard-coded and are handled via Text-to-SQL.

## Architecture Overview

### High-level flow
```
User (UI / CLI)
      ↓
FastAPI Backend
      ↓
Text-to-SQL (LLM)
      ↓
SQLite (SELECT execution)
      ↓
Result Table
      ↓
Answer Generation (LLM, grounded)
```

### Key design choice: Text-to-SQL

Instead of manually routing questions to predefined pandas functions, the system uses an LLM to generate SQL based on:
- The database schema
- Explicit business rules (tax, FX conversion, revenue calculation)

This makes the solution flexible, extensible, and closer to real production systems.

## Project Structure
```
.
├── data/
│   ├── Clients.xlsx
│   ├── Invoices.xlsx
│   └── InvoiceLineItems.xlsx
│
├── backend/
│   ├── backend_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tabular_rag/
│       ├── data_loader.py
│       ├── llm_client.py
│       ├── sql_engine.py
│       ├── text2sql_planner.py
│       └── sql_chat_pipeline.py
│
├── frontend/
│   ├── frontend_app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── cli/
│   └── cli_client.py
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Environment Configuration

### `.env.example`

An example environment file is provided:
```
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4.1-mini
BACKEND_URL=http://backend:8000
```

Create your own `.env` file:
```
cp .env.example .env
```

Edit `.env` and set your real OpenAI API key.

## Running the Full Application (Recommended)

### Prerequisites
- Docker
- Docker Compose

### Start everything
From the repository root:
```
docker compose up --build
```

Expected behavior:
- First run: ~2–3 minutes (dependency installation)
- Backend API available at: `http://localhost:8000`
- Frontend UI available at: `http://localhost:8501`

### Health check
```
curl http://localhost:8000/health
```
Expected response:
```
{"status":"ok"}
```

## Frontend (Streamlit UI)

Open in browser:
```
http://localhost:8501
```

The UI shows:
- User question
- Generated SQL
- Retrieved rows (table)
- Final grounded answer
- A "Clear chat history" button to reset the conversation

This transparency helps verify correctness and grounding.

## Backend API

### Endpoint: `/ask`

#### POST `/ask`

Request example:
```json
{
  "question": "Which clients are based in the UK?",
  "return_sql": true,
  "return_rows": true,
  "max_rows": 50
}
```

Response example:
```json
{
  "question": "...",
  "sql": "SELECT ...",
  "answer": "...",
  "rows": [...],
  "num_rows": 2
}
```

## CLI Client (Optional)

You can also interact via a CLI client that calls the backend API:
```
export BACKEND_URL=http://localhost:8000
python cli/cli_client.py
```

## Business Logic

### Line total (including tax)
```
quantity * unit_price * (1 + tax_rate)
```

### Line total in USD
```
line_total * fx_rate_to_usd
```

Revenue and aggregations are computed in SQL, not by the LLM.

## Hallucination Mitigation

The system is designed to avoid numeric hallucinations:
- The LLM generates SQL, not numeric values.
- All computations are performed by SQLite.
- The LLM only sees retrieved rows and aggregates.
- If data is missing, the model is instructed to state that explicitly.

## Assumptions & Limitations
- All data fits in memory.
- Read-only analytical queries only (SELECT).
- No authentication or authorization layer.
- Text-to-SQL quality depends on the LLM.
- Optimized for clarity and correctness rather than large-scale deployment.

## Switching LLM Providers

All LLM calls are centralized in `llm_client.py`.

To switch providers (e.g. OpenAI → Groq):
- Replace the client implementation
- Update environment variables
- No other code changes required

## Summary

This project demonstrates:
- A clean Text-to-SQL RAG architecture
- Strong grounding and hallucination mitigation
- Clear separation between backend and frontend
- Production-style execution using Docker Compose
- Transparent, inspectable outputs (SQL + rows)

The solution prioritizes correctness, clarity, and maintainability.
