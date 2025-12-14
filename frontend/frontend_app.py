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

if st.button("Clear chat"):
    st.session_state.history = []
    st.rerun()

question = st.text_input(
    "Your question",
    value=st.session_state.pop("pending_question", "") if "pending_question" in st.session_state else "",
    placeholder="e.g., Which clients are based in the UK?",
)

colA, colB = st.columns([1, 1])
return_sql = colA.checkbox("Show SQL", value=True)
return_rows = colB.checkbox("Show rows", value=True)

ask = st.button("Ask") or st.session_state.pop("trigger_ask", False)  # Check the flag

if ask and question.strip():
    with st.spinner("Calling backend..."):
        resp = requests.post(
            f"{BACKEND_URL}/ask",
            json={
                "question": question,
                "return_sql": return_sql,
                "return_rows": return_rows,
                "max_rows": 50,  # Default max rows
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
        st.markdown("### Retrieved rows")
        st.dataframe(item["rows"])

    st.markdown("---")
