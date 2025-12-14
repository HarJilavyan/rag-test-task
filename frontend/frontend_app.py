import os
import requests
import streamlit as st

st.set_page_config(page_title="Tabular Text2SQL Chat", layout="wide")
st.title("Chat over Tabular Data (Text-to-SQL)")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.write(
    "This UI calls a backend API that performs Text-to-SQL over an in-memory SQLite DB "
    "built from the Excel files, then generates a grounded answer."
)

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("Controls")
    st.write(f"Backend: `{BACKEND_URL}`")
    if st.button("Clear chat"):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.subheader("Examples")
    examples = [
        "Which clients are based in the UK?",
        "List all invoices issued in March 2024 with their statuses.",
        "Which invoices are currently marked as \"Overdue\"?",
        "For each service_name in InvoiceLineItems, how many line items are there?",
        "For invoice I1001, list all line items with totals including tax.",
        "Which client has the highest total billed amount in 2024, and what is that total?",
    ]
    for ex in examples:
        if st.button(ex):
            st.session_state.pending_question = ex
            st.rerun()

question = st.text_input(
    "Your question",
    value=st.session_state.pop("pending_question", "") if "pending_question" in st.session_state else "",
    placeholder="e.g., Which clients are based in the UK?",
)

colA, colB, colC = st.columns([1, 1, 1])
return_sql = colA.checkbox("Show SQL", value=True)
return_rows = colB.checkbox("Show rows", value=True)
max_rows = colC.number_input("Max rows", min_value=1, max_value=200, value=50)

ask = st.button("Ask")

if ask and question.strip():
    with st.spinner("Calling backend..."):
        resp = requests.post(
            f"{BACKEND_URL}/ask",
            json={
                "question": question,
                "return_sql": return_sql,
                "return_rows": return_rows,
                "max_rows": int(max_rows),
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        st.session_state.history.append(data)

for item in reversed(st.session_state.history):
    st.markdown("### Question")
    st.write(item["question"])

    cols = st.columns([1, 1])
    if item.get("sql"):
        with cols[0]:
            st.markdown("### Generated SQL")
            st.code(item["sql"], language="sql")

    with cols[1]:
        st.markdown("### Answer")
        st.write(item["answer"])

    if item.get("rows") is not None:
        st.markdown(f"### Retrieved rows (showing up to {max_rows}, total rows: {item.get('num_rows', 0)})")
        st.dataframe(item["rows"])

    st.markdown("---")
