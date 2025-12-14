from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Any

from .llm_client import LLMClient

SCHEMA_DESCRIPTION = """
You are given a SQLite database with the following tables and columns:

Table: Clients
- client_id (TEXT)
- client_name (TEXT)
- industry (TEXT)
- country (TEXT)

Table: Invoices
- invoice_id (TEXT)
- client_id (TEXT)  -- foreign key to Clients.client_id
- invoice_date (DATE)
- due_date (DATE)
- status (TEXT)     -- e.g. 'Paid', 'Overdue'
- currency (TEXT)
- fx_rate_to_usd (REAL)  -- conversion rate to USD

Table: InvoiceLineItems
- line_id (TEXT)
- invoice_id (TEXT)      -- foreign key to Invoices.invoice_id
- service_name (TEXT)
- quantity (INTEGER)
- unit_price (REAL)
- tax_rate (REAL)        -- e.g. 0.2 for 20% VAT

Business rules:
- Line total in invoice currency INCLUDING tax:
    line_total = quantity * unit_price * (1 + tax_rate)
- Line total converted to USD:
    line_total_usd = line_total * fx_rate_to_usd
- When a question asks for "total billed in 2024 (including tax)" or "revenue in 2024":
    * Filter invoices by invoice_date in 2024.
    * Join Invoices with InvoiceLineItems on invoice_id.
    * Compute SUM(quantity * unit_price * (1 + tax_rate) * fx_rate_to_usd).
- When grouping by client:
    * Join Clients on client_id and group by Clients.client_id or client_name.
- When grouping by service_name:
    * Group by InvoiceLineItems.service_name.
- When counting line items per service_name:
    * Use COUNT(DISTINCT line_id) or COUNT(*) grouped by service_name.

Rules:
- Use ONLY these tables and columns.
- Use SQL compatible with SQLite.
- Do NOT modify data (no INSERT/UPDATE/DELETE); ONLY SELECT queries.
- Prefer explicit JOINs when combining tables.
"""


TEXT2SQL_SYSTEM_PROMPT = SCHEMA_DESCRIPTION + """
You are a Text-to-SQL model that translates a user's question into a single SQL SELECT query.

Return STRICT JSON with this shape (no extra text):

{
  "sql": "<sql_query_here>"
}

Do NOT include comments or explanations, only valid JSON.
"""

@dataclass
class Text2SQLPlanner:
    llm: LLMClient

    def plan_sql(self, question: str) -> str:
        """
        Given a natural-language question, return a SQL query string.
        """
        user_prompt = json.dumps(
            {
                "question": question,
                "instructions": "Translate the question into a single SELECT SQL query."
            },
            indent=2,
        )

        raw = self.llm.generate(
            system_prompt=TEXT2SQL_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.0,
        )

        # Extract JSON even if wrapped in code fences
        json_str = raw.strip()
        if json_str.startswith("```"):
            json_str = json_str.strip("`")
            if "{" in json_str:
                json_str = json_str[json_str.find("{"):]
            if "}" in json_str:
                json_str = json_str[: json_str.rfind("}") + 1]
        else:
            if not (json_str.startswith("{") and json_str.endswith("}")):
                start = json_str.find("{")
                end = json_str.rfind("}")
                if start != -1 and end != -1:
                    json_str = json_str[start : end + 1]

        data = json.loads(json_str)
        sql = data.get("sql", "")
        if not sql:
            raise ValueError(f"Text2SQL model did not return a SQL query. Raw: {raw}")

        return sql.strip()
