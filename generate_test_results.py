from tabular_rag import load_data
from tabular_rag.llm_client import LLMClient
from tabular_rag.sql_engine import SqlEngine
from tabular_rag.sql_chat_pipeline import SqlChatPipeline

import csv
from pathlib import Path


QUESTIONS = [
    "List all clients with their industries.",
    "Which clients are based in the UK?",
    "List all invoices issued in March 2024 with their statuses.",
    "Which invoices are currently marked as \"Overdue\"?",
    "For each service_name in InvoiceLineItems, how many line items are there?",
    "List all invoices for Acme Corp with their invoice IDs, invoice dates, due dates, and statuses.",
    "Show all invoices issued to Bright Legal in February 2024, including their status and currency.",
    "For invoice I1001, list all line items with service name, quantity, unit price, tax rate, and compute the line total (including tax) for each.",
    "For each client, compute the total amount billed in 2024 (including tax) across all their invoices.",
    "Which client has the highest total billed amount in 2024, and what is that total?",
]


def main():
    # Load data and build pipeline
    ctx = load_data()
    sql_engine = SqlEngine.from_datacontext(ctx)
    llm = LLMClient()
    pipeline = SqlChatPipeline(sql_engine=sql_engine, llm=llm)

    out_path = Path("test_results.csv")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Answer"])

        for q in QUESTIONS:
            print(f"Running question: {q}")
            try:
                answer = pipeline.answer(q)
            except Exception as e:
                answer = f"ERROR: {e}"

            writer.writerow([q, answer])

    print(f"Saved results to {out_path.resolve()}")


if __name__ == "__main__":
    main()
