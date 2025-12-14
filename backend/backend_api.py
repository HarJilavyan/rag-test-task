from __future__ import annotations

import os
from fastapi import FastAPI
from pydantic import BaseModel

from tabular_rag import load_data
from tabular_rag.llm_client import LLMClient
from tabular_rag.sql_engine import SqlEngine
from tabular_rag.text2sql_planner import Text2SQLPlanner
from tabular_rag.sql_chat_pipeline import SqlChatPipeline

app = FastAPI(title="Tabular Text2SQL RAG API")

# Build once at startup (simple + fast for this dataset)
CTX = load_data()
SQL_ENGINE = SqlEngine.from_datacontext(CTX)
LLM = LLMClient()
PLANNER = Text2SQLPlanner(llm=LLM)
PIPELINE = SqlChatPipeline(sql_engine=SQL_ENGINE, llm=LLM)


class AskRequest(BaseModel):
    question: str
    return_sql: bool = True
    return_rows: bool = True
    max_rows: int = 50


class AskResponse(BaseModel):
    question: str
    sql: str | None
    answer: str
    rows: list[dict] | None
    num_rows: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    sql = PLANNER.plan_sql(req.question) if req.return_sql else None
    answer = PIPELINE.answer(req.question)

    rows = None
    num_rows = 0
    if req.return_rows and sql:
        df = SQL_ENGINE.query(sql)
        num_rows = len(df)
        df = df.head(req.max_rows)
        rows = df.to_dict(orient="records")

    return AskResponse(
        question=req.question,
        sql=sql,
        answer=answer,
        rows=rows,
        num_rows=num_rows,
    )
