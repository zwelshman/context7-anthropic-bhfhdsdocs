import streamlit as st
import requests
from anthropic import Anthropic


# ============================================================================
# PAGE SETUP
# ============================================================================

st.set_page_config(
    page_title="BHF Documentation Search",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
    <style>
        h1 { color: #003d7a; font-weight: 700; }
        .answer-section {
            background: linear-gradient(135deg, #f0f7ff 0%, #e8eef5 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border: 2px solid #003d7a;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if "client" not in st.session_state:
    anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    st.session_state.client = Anthropic(api_key=anthropic_key)

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================================
# GET API KEYS
# ============================================================================

context7_key = st.secrets.get("CONTEXT7_API_KEY", "")
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")

if not context7_key or not anthropic_key:
    st.error("⚠️ Missing API keys in secrets")
    st.stop()


# ============================================================================
# FETCH DOCUMENTATION FROM CONTEXT7
# ============================================================================

def fetch_documentation(search_topic, repo_name):
    """
    Fetch documentation from Context7 API
    """
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


# ============================================================================
# GENERATE ANSWER WITH CLAUDE
# ============================================================================

def generate_answer(search_query, docs_context):
    """
    Use Claude to answer the question
    """
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


# ============================================================================
# HEADER
# ============================================================================

st.title("🔍 BHF Documentation Search")

st.warning(
    "⚠️ **EXPERIMENTAL** - For issues or feedback: "
    "[bhfdsc_hds@hdruk.ac.uk](mailto:bhfdsc_hds@hdruk.ac.uk)"
)

st.divider()


# ============================================================================
# REPOSITORY SELECTION
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    if st.button("📖 Documentation", use_container_width=True, key="doc_btn"):
        st.session_state.repo = "documentation"

with col2:
    if st.button("💻 Standard Pipeline", use_container_width=True, key="code_btn"):
        st.session_state.repo = "standard-pipeline"

# Set default repo if not selected
if "repo" not in st.session_state:
    st.session_state.repo = "documentation"

# Show selected repo
repo_choice = st.session_state.repo
repo_display = repo_choice.replace('-', ' ').title()

st.markdown(f"**Selected:** 🏥 BHF {repo_display}")

st.divider()


# ============================================================================
# SEARCH
# ============================================================================

search_query = st.text_input(
    "What would you like to know?",
    placeholder="Type your question...",
)

search_button = st.button("🔍 Search", use_container_width=True, type="primary")


# ============================================================================
# RESULTS
# ============================================================================

if search_button and search_query:
    with st.spinner("🔄 Fetching documentation..."):
        docs_context = fetch_documentation(search_query, repo_choice)
    
    if not docs_context or len(docs_context.strip()) < 20:
        st.warning(f"No documentation found for '{search_query}'")
    else:
        with st.spinner("✨ Generating answer..."):
            answer = generate_answer(search_query, docs_context)
        
        st.markdown('<div class="answer-section">', unsafe_allow_html=True)
        st.markdown("## Answer")
        st.markdown(answer)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("📚 View Source Documentation"):
            st.text(docs_context)
        
        st.session_state.messages.append({
            "query": search_query,
            "answer": answer,
            "repo": repo_choice
        })


# ============================================================================
# HISTORY
# ============================================================================

if st.session_state.messages:
    st.divider()
    st.markdown("### Recent Searches")
    
    for msg in reversed(st.session_state.messages[-5:]):
        with st.expander(f"❓ {msg['query'][:60]}"):
            st.markdown(msg['answer'])
