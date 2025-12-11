"""
BHF Data Science Centre - Documentation Search
Simple, clean interface for searching repositories
"""

import streamlit as st
import requests
from anthropic import Anthropic


# PAGE SETUP
st.set_page_config(
    page_title="BHF Health Data Science Team Documentation and Standard Pipeline Knowledge Base",
    page_icon="❤️",
    layout="wide"
)

# Minimal styling - avoid conflicts
st.markdown("""
    <style>
        .main { background: linear-gradient(180deg, #fafafa 0%, #fff9f9 100%); }
        .header-box { 
            background: linear-gradient(135deg, #1a1a2e 0%, #c8102e 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .header-box h1 { color: white; margin: 0; font-size: 2.5rem; }
        .header-box p { color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; }
        .repo-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0; }
    </style>
""", unsafe_allow_html=True)

# INITIALIZE SESSION STATE
if "client" not in st.session_state:
    st.session_state.client = Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY", ""))

if "messages" not in st.session_state:
    st.session_state.messages = []

if "repo" not in st.session_state:
    st.session_state.repo = "documentation"

# GET API KEYS
context7_key = st.secrets.get("CONTEXT7_API_KEY", "")
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")

if not context7_key or not anthropic_key:
    st.error("Missing API keys in secrets")
    st.stop()


# FUNCTIONS
def fetch_documentation(search_topic, repo_name):
    """Fetch from Context7 API"""
    repo_full = f"bhfdsc/{repo_name}"
    endpoints = [
        f"https://context7.com/api/v2/docs/info/{repo_full}",
        f"https://context7.com/api/v2/docs/code/{repo_full}"
    ]
    headers = {"Authorization": f"Bearer {context7_key}"}
    params = {"topic": search_topic, "type": "txt"}
    
    for url in endpoints:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception:
            continue
    return ""


def generate_answer(search_query, docs_context):
    """Generate answer using Claude"""
    prompt = f"""Answer this question based on the documentation:

Question: {search_query}

Documentation:
{docs_context}

Provide a clear, helpful answer."""

    message = st.session_state.client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text


# HEADER
st.markdown("""
    <div class="header-box">
        <h1>❤️ BHF Documentation Search</h1>
        <p>Intelligent Q&A powered by Claude AI</p>
    </div>
""", unsafe_allow_html=True)

st.warning("⚠️ EXPERIMENTAL - For feedback: bhfdsc_hds@hdruk.ac.uk")

st.markdown("---")

# REPO SELECTION
st.subheader("1️⃣ Select Repository")

col1, col2 = st.columns(2)

with col1:
    if st.button("📖 Documentation", use_container_width=True, key="doc_btn"):
        st.session_state.repo = "documentation"
        st.rerun()

with col2:
    if st.button("💻 Standard Pipeline", use_container_width=True, key="code_btn"):
        st.session_state.repo = "standard-pipeline"
        st.rerun()

repo_choice = st.session_state.repo
repo_display = repo_choice.replace('-', ' ').title()

st.info(f"✓ Currently searching: **🏥 BHF {repo_display}**")

st.markdown("---")

# SEARCH
st.subheader("2️⃣ Search Documentation")

search_query = st.text_input(
    "Ask your question:",
    placeholder="e.g., 'What is the standard pipeline?'",
)

col1, col2 = st.columns([3, 1])
with col1:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")
with col2:
    clear_button = st.button("Clear", use_container_width=True)

if clear_button:
    st.session_state.messages = []
    st.rerun()

# RESULTS
if search_button and search_query:
    st.markdown("---")
    st.subheader("3️⃣ Results")
    
    # Show progress
    status = st.status("Searching and generating...", expanded=True)
    
    with status:
        st.write("🔄 Fetching documentation from Context7...")
        docs_context = fetch_documentation(search_query, repo_choice)
        st.write("✓ Documentation fetched")
        
        if not docs_context or len(docs_context.strip()) < 20:
            st.error(f"No documentation found for '{search_query}'")
            st.write("Try different search terms or switch repositories")
        else:
            st.write("✨ Generating answer with Claude...")
            answer = generate_answer(search_query, docs_context)
            st.write("✓ Answer generated")
    
    # Display answer
    st.success("Done!")
    
    st.subheader("📖 Answer")
    st.write(answer)
    
    # Show source docs
    with st.expander("📚 View Source Documentation"):
        st.text(docs_context)
    
    # Store in history
    st.session_state.messages.append({
        "query": search_query,
        "answer": answer,
        "repo": repo_choice
    })

# HISTORY
if st.session_state.messages:
    st.markdown("---")
    st.subheader("📋 Recent Searches")
    
    for i, msg in enumerate(reversed(st.session_state.messages[-5:]), 1):
        with st.expander(f"{i}. {msg['query'][:60]}"):
            st.write(msg['answer'])
            st.caption(f"From: {msg['repo'].title()}")

# FOOTER
st.markdown("---")
st.caption("❤️ BHF Documentation Search | Powered by Claude AI & Context7 API | British Heart Foundation Data Science Centre")
