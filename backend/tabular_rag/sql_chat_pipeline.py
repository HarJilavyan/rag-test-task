from __future__ import annotations

from dataclasses import dataclass
import json
import pandas as pd

from .llm_client import LLMClient
from .sql_engine import SqlEngine
from .text2sql_planner import Text2SQLPlanner

ANSWER_SYSTEM_PROMPT_SQL = """
You answer questions about a small business's clients, invoices, and invoice line items.

You are given:
- the user's original question
- the SQL query that was executed
- the tabular result of that query (as Markdown)

CRITICAL RULES:
- Do NOT hallucinate any numeric values. All numbers you mention MUST appear in the result table.
- If needed, you may do simple mental aggregation (e.g. sum a column across rows) but it must be consistent with the result.
- If something is not present in the result table, explicitly say it is not available.
- Be concise and business-friendly.
"""

@dataclass
class SqlChatPipeline:
    sql_engine: SqlEngine
    llm: LLMClient

    def __post_init__(self):
        self.planner = Text2SQLPlanner(llm=self.llm)

    def answer(self, question: str) -> str:
        # 1) Plan SQL
        sql = self.planner.plan_sql(question)

        # 2) Execute SQL
        df = self.sql_engine.query(sql)

        # 3) Format context
        if df.empty:
            table_md = "(EMPTY RESULT)"
        else:
            display_df = df.head(50).copy()
            try:
                table_md = display_df.to_markdown(index=False)
            except Exception:
                table_md = display_df.to_string(index=False)

        user_payload = {
            "question": question,
            "sql": sql,
            "result_table_markdown": table_md,
            "num_rows": len(df),
        }

        answer = self.llm.generate(
            system_prompt=ANSWER_SYSTEM_PROMPT_SQL,
            user_prompt=json.dumps(user_payload, indent=2),
            temperature=0.1,
        )

        return answer
