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
        h2 { color: #003d7a; font-weight: 600; }
        .answer-section {
            background: linear-gradient(135deg, #f0f7ff 0%, #e8eef5 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border: 2px solid #003d7a;
            margin: 1rem 0;
        }
        .docs-section {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #c41e3a;
            margin: 1rem 0;
        }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #003d7a 0%, #002147 100%); }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] label { color: white; }
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
# SIDEBAR: CONFIGURATION & API STATUS
# ============================================================================

st.sidebar.title("⚙️ Configuration")

# Check API keys
context7_key = st.secrets.get("CONTEXT7_API_KEY", "")
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")

col1, col2 = st.sidebar.columns([2, 2])
with col1:
    st.markdown(f"{'✅ Context7' if context7_key else '❌ Context7'}")
with col2:
    st.markdown(f"{'✅ Anthropic' if anthropic_key else '❌ Anthropic'}")

if not context7_key or not anthropic_key:
    st.sidebar.error("⚠️ Missing API keys in secrets")
    st.stop()

st.sidebar.divider()

# Repository selection with clear descriptions
st.sidebar.markdown("### 📂 Choose Your Repository")

repo_choice = st.sidebar.radio(
    "Which repository do you want to search?",
    options=["documentation", "standard-pipeline"],
    label_visibility="collapsed"
)

# Show detailed info about selected repo
if repo_choice == "documentation":
    st.sidebar.info(
        "**📖 BHF Documentation**\n\n"
        "Use this for:\n"
        "• General information & guides\n"
        "• Data models & structures\n"
        "• Clinical coding systems\n"
        "• Best practices & standards\n\n"
        "❓ Example: 'What is the standard pipeline?'"
    )
else:
    st.sidebar.info(
        "**💻 BHF Standard Pipeline**\n\n"
        "Use this for:\n"
        "• Code examples & implementations\n"
        "• Technical details & configuration\n"
        "• Working code samples\n"
        "• Development workflows\n\n"
        "❓ Example: 'How do I implement the pipeline?'"
    )

st.sidebar.divider()


# ============================================================================
# FETCH DOCUMENTATION FROM CONTEXT7
# ============================================================================

def fetch_documentation(search_topic, repo_name):
    """
    Fetch documentation from Context7 API
    Tries both /info and /code endpoints
    """
    repo_full = f"bhfdsc/{repo_name}"
    
    # Try both endpoints
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
                # Return plain text when type=txt
                return response.text
                
        except Exception:
            continue
    
    return ""


# ============================================================================
# GENERATE ANSWER WITH CLAUDE
# ============================================================================

def generate_answer(search_query, docs_context):
    """
    Use Claude to answer the question based on documentation
    """
    prompt = f"""Answer this question based on the documentation provided:

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
# MAIN INTERFACE
# ============================================================================

st.title("🔍 BHF Documentation Search")

st.warning(
    "⚠️ **EXPERIMENTAL** - This is a prototype tool. For issues or feedback, "
    "please contact the Health Data Scientist Team: "
    "[bhfdsc_hds@hdruk.ac.uk](mailto:bhfdsc_hds@hdruk.ac.uk)"
)

st.divider()

# Show what repo is selected and what it contains
st.markdown("## 📂 Current Repository")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown("**📖 Documentation**" if repo_choice == "documentation" else "💻 Standard Pipeline")

with col2:
    if repo_choice == "documentation":
        st.caption("General info, guides, data models, best practices")
    else:
        st.caption("Code examples, implementations, technical details")

with col3:
    if st.button("📋 Change Repo", use_container_width=True):
        st.info("Use the sidebar to switch repositories")

st.divider()

repo_display = repo_choice.replace('-', ' ').title()
st.markdown(f"**Search** BHF {repo_display} with AI-powered answers")

st.divider()

# Search input
search_query = st.text_input(
    "What would you like to know?",
    placeholder="e.g., 'what is the standard pipeline?' or 'how to configure deployment'",
    label_visibility="collapsed"
)

search_button = st.button("🔍 Search", use_container_width=True, type="primary")


# ============================================================================
# HANDLE SEARCH
# ============================================================================

if search_button and search_query:
    with st.spinner("🔄 Fetching documentation..."):
        docs_context = fetch_documentation(search_query, repo_choice)
    
    # Check if we found anything
    if not docs_context or len(docs_context.strip()) < 20:
        st.warning(f"⚠️ No documentation found for '{search_query}'")
        st.info(
            f"The `bhfdsc/{repo_choice}` repository may not be indexed in Context7 yet, "
            "or documentation for this topic doesn't exist.\n\n"
            "Try different search terms, or check if the repo is available."
        )
    else:
        # Generate answer
        with st.spinner("✨ Generating answer..."):
            answer = generate_answer(search_query, docs_context)
        
        # Display results
        st.markdown('<div class="answer-section">', unsafe_allow_html=True)
        st.markdown("### 📖 Answer")
        st.markdown(answer)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show source documentation
        with st.expander("📚 Source Documentation", expanded=False):
            st.markdown('<div class="docs-section">', unsafe_allow_html=True)
            st.text(docs_context)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Store search history
        st.session_state.messages.append({
            "query": search_query,
            "answer": answer,
            "repo": repo_choice
        })


# ============================================================================
# SEARCH HISTORY
# ============================================================================

if st.session_state.messages:
    st.divider()
    st.markdown("### 📋 Recent Searches")
    
    for msg in reversed(st.session_state.messages[-5:]):
        with st.expander(f"❓ {msg['query'][:60]}"):
            st.markdown(msg['answer'])
            st.caption(f"From: {msg['repo']}")


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("🤖 Powered by Anthropic Claude | Context7 Documentation API")
