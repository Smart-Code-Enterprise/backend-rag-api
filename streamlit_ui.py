import streamlit as st
import requests

# URL of the backend API
API_URL = "http://localhost:8000/query"  # Change this to your actual endpoint

# Streamlit App Title
st.set_page_config(page_title="Building Code Q&A", layout="wide")
st.title("🏛️ Building Code Q&A Interface")

# Sidebar settings
st.sidebar.header("🔧 Settings")
rerank = st.sidebar.checkbox("Enable Re-Ranking", value=False)
hybrid = st.sidebar.slider("Hybrid Search Weight", 0.0, 1.0, 0.4, 0.1)
llm = st.sidebar.selectbox("Select LLM Model", ["o4-mini", "gpt-3.5-turbo", "gpt-4"], index=0)

# Main input
st.subheader("Ask a question about the building code:")
question = st.text_input("Your question:")

# Submit button
if st.button("Submit"):
    if not question:
        st.error("Please enter a question to proceed.")
    else:
        payload = {
            "User_question": question,
            "Rerank": rerank,
            "Hybrid_search": hybrid,
            "LLM": llm
        }
        with st.spinner("Querying backend API..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=300)
                response.raise_for_status()
                data = response.json()

                # Display Answer
                answer = data.get("content") or data.get("resp")
                if answer:
                    st.markdown("### ✅ Answer")
                    st.markdown(answer)
                else:
                    st.warning("No answer returned from the API.")

                # Display References
                refs = data.get("refs", [])
                if refs:
                    st.markdown("### 📚 References")
                    for ref in refs:
                        ref_num = ref.get("ref_num", "N/A")
                        page = ref.get("page", "?")
                        st.write(f"- Section **{ref_num}** (Page {page})")

                # Display Book Name
                book = data.get("book_name")
                if book:
                    st.caption(f"Source document: **{book}**")

            except requests.exceptions.RequestException as e:
                st.error(f"Error contacting API: {e}")
