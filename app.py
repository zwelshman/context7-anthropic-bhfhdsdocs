"""
BHF Data Science Centre - Documentation Search
AI-powered search using Context7 and Claude
"""

import streamlit as st
import requests
from anthropic import Anthropic

# ============================================================================
# PAGE SETUP
# ============================================================================

st.set_page_config(
    page_title="BHF Documentation Search",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');
        
        :root {
            --bhf-red: #C8102E;
            --bhf-red-dark: #A00D24;
            --bhf-red-light: #E8394F;
            --color-bg: #FAFAFA;
            --color-bg-warm: #FFF9F9;
            --color-bg-card: #FFFFFF;
            --color-bg-dark: #1A1A2E;
            --color-text: #2D3436;
            --color-text-muted: #636E72;
            --color-border: #E8E8E8;
            --font-display: 'Source Serif 4', Georgia, serif;
            --font-body: 'Source Sans 3', -apple-system, sans-serif;
            --shadow-sm: 0 1px 3px rgba(200, 16, 46, 0.06);
            --shadow-md: 0 4px 12px rgba(200, 16, 46, 0.08);
            --shadow-red: 0 4px 20px rgba(200, 16, 46, 0.15);
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
        }
        
        * { font-family: var(--font-body); }
        h1, h2, h3, h4 { font-family: var(--font-display); color: var(--color-text); }
        
        .stApp { background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-bg-warm) 100%); }
        .main .block-container { max-width: 1200px; padding: 2rem 3rem 4rem; }
        
        /* Hero Section */
        .hero-section {
            background: linear-gradient(135deg, var(--color-bg-dark) 0%, #2D1F2F 30%, var(--bhf-red-dark) 70%, var(--bhf-red) 100%);
            border-radius: var(--radius-lg);
            padding: 3.5rem;
            margin: -1rem -1rem 2.5rem;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 80%, rgba(255, 107, 107, 0.2) 0%, transparent 40%),
                        radial-gradient(circle at 80% 20%, rgba(242, 84, 91, 0.15) 0%, transparent 40%);
            pointer-events: none;
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
        }
        
        .hero-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #ffffff;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.5rem 1.25rem;
            border-radius: 50px;
            margin-bottom: 1.5rem;
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.1;
            margin-bottom: 1rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.85);
            line-height: 1.7;
            max-width: 600px;
            margin-bottom: 0;
        }
        
        /* Section Header */
        .section-header {
            text-align: left;
            margin-bottom: 2rem;
            margin-top: 2.5rem;
        }
        
        .section-header h2 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--color-text);
            margin-bottom: 0.5rem;
        }
        
        .section-header p {
            font-size: 1rem;
            color: var(--color-text-muted);
            margin: 0;
        }
        
        /* Status Badge */
        .status-alert {
            background: linear-gradient(135deg, #fff9e6 0%, #fffbf0 100%);
            border-left: 5px solid #ff9800;
            padding: 1.25rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1);
        }
        
        .status-alert strong {
            color: #e65100;
            display: block;
            margin-bottom: 0.25rem;
        }
        
        .status-alert p {
            margin: 0;
            color: #bf360c;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        /* Repo Buttons */
        .repo-button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .repo-btn-wrapper {
            cursor: pointer;
        }
        
        .repo-card {
            background: var(--color-bg-card);
            border: 2px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: 2rem;
            text-align: left;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
            height: 100%;
        }
        
        .repo-card:hover {
            border-color: var(--bhf-red);
            box-shadow: var(--shadow-red);
            transform: translateY(-4px);
        }
        
        .repo-card.active {
            background: linear-gradient(135deg, rgba(200, 16, 46, 0.05) 0%, rgba(242, 84, 91, 0.05) 100%);
            border-color: var(--bhf-red);
        }
        
        .repo-card h3 {
            margin: 0 0 0.75rem 0;
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--color-text);
        }
        
        .repo-card p {
            margin: 0;
            font-size: 0.95rem;
            color: var(--color-text-muted);
            line-height: 1.5;
        }
        
        /* Selection Indicator */
        .selection-indicator {
            background: linear-gradient(135deg, var(--bhf-red) 0%, var(--bhf-red-dark) 100%);
            color: white;
            padding: 1.25rem;
            border-radius: var(--radius-md);
            margin: 1.5rem 0 2rem 0;
            font-weight: 600;
            text-align: center;
            box-shadow: var(--shadow-red);
            font-size: 1.05rem;
        }
        
        /* Search Box */
        .search-section {
            background: var(--color-bg-card);
            padding: 2rem;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            margin-bottom: 2rem;
            border: 1px solid var(--color-border);
        }
        
        .search-section h3 {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--color-text);
            margin-top: 0;
            margin-bottom: 1rem;
        }
        
        /* Results */
        .result-box {
            background: linear-gradient(135deg, #F5F8FF 0%, #EDF2FF 100%);
            padding: 2rem;
            border-radius: var(--radius-md);
            border-left: 5px solid var(--bhf-red);
            margin: 2rem 0;
            box-shadow: var(--shadow-md);
        }
        
        .result-box h2 {
            color: var(--color-text);
            margin-top: 0;
            font-weight: 700;
            margin-bottom: 1rem;
            font-size: 1.4rem;
        }
        
        /* History */
        .history-section {
            margin-top: 2.5rem;
        }
        
        .history-item {
            background: var(--color-bg-card);
            padding: 1.5rem;
            border-radius: var(--radius-md);
            border-left: 4px solid var(--bhf-red);
            margin: 1rem 0;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .history-item:hover {
            box-shadow: var(--shadow-md);
            transform: translateX(2px);
        }
        
        .history-item h4 {
            color: var(--color-text);
            margin: 0 0 0.5rem 0;
            font-weight: 600;
            font-size: 1rem;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: var(--radius-md);
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--bhf-red) 0%, var(--bhf-red-dark) 100%);
            color: white;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, var(--bhf-red-dark) 0%, #7A0B1B 100%);
            box-shadow: var(--shadow-red);
        }
        
        /* Divider */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, var(--color-border) 20%, var(--color-border) 80%, transparent 100%);
            margin: 2.5rem 0;
        }
        
        /* Footer */
        .footer {
            background: var(--color-bg-dark);
            border-radius: var(--radius-lg);
            padding: 3rem;
            margin: 3rem -1rem -1rem;
            color: #ffffff;
            text-align: center;
        }
        
        .footer p {
            margin: 0.25rem 0;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .footer strong {
            color: #ffffff;
            font-weight: 600;
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: var(--radius-md);
            border: 2px solid var(--color-border);
            font-size: 1rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--bhf-red);
            box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.1);
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            font-weight: 500;
            font-size: 0.95rem;
            color: var(--color-text);
            background: rgba(200, 16, 46, 0.03);
            border-radius: var(--radius-sm);
        }
        
        .streamlit-expanderContent {
            border: 1px solid var(--color-border);
            border-top: none;
        }
        
        @media (max-width: 768px) {
            .hero-section { padding: 2.5rem 1.5rem; }
            .hero-title { font-size: 2rem; }
            .repo-button-group { grid-template-columns: 1fr; }
            .main .block-container { padding: 1rem 1.5rem 2rem; }
        }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZE
# ============================================================================

if "client" not in st.session_state:
    st.session_state.client = Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY", ""))

if "messages" not in st.session_state:
    st.session_state.messages = []

if "repo" not in st.session_state:
    st.session_state.repo = "documentation"

context7_key = st.secrets.get("CONTEXT7_API_KEY", "")
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")

if not context7_key or not anthropic_key:
    st.error("⚠️ Missing API keys")
    st.stop()


# ============================================================================
# FUNCTIONS
# ============================================================================

def fetch_documentation(search_topic, repo_name):
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
# HERO SECTION
# ============================================================================

st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-badge">BHF Data Science Centre</div>
            <h1 class="hero-title">Documentation Search</h1>
            <p class="hero-subtitle">Intelligent Q&A powered by Claude AI and Context7. 
            Search across BHF repositories for phenotypes, curation processes, and technical documentation.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="status-alert">
        <strong>⚠️ EXPERIMENTAL</strong>
        <p>This is a prototype tool. For feedback or issues: <strong>bhfdsc_hds@hdruk.ac.uk</strong></p>
    </div>
""", unsafe_allow_html=True)


# ============================================================================
# REPO SELECTION
# ============================================================================

st.markdown("""
    <div class="section-header">
        <h2>Select Repository</h2>
        <p>Choose which documentation repository you want to search</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📖 Documentation\n\nGeneral guides, data models, standards, best practices", 
                 use_container_width=True, key="doc_btn"):
        st.session_state.repo = "documentation"

with col2:
    if st.button("💻 Standard Pipeline\n\nCode examples, technical implementation, configuration", 
                 use_container_width=True, key="code_btn"):
        st.session_state.repo = "standard-pipeline"

repo_choice = st.session_state.repo
repo_display = repo_choice.replace('-', ' ').title()

st.markdown(f"""
    <div class="selection-indicator">
        ✓ Currently searching: <strong>🏥 BHF {repo_display}</strong>
    </div>
""", unsafe_allow_html=True)


# ============================================================================
# SEARCH SECTION
# ============================================================================

st.markdown("""
    <div class="section-header">
        <h2>Search Documentation</h2>
        <p>Ask a question to find relevant information</p>
    </div>
""", unsafe_allow_html=True)

search_query = st.text_input(
    "Your question",
    placeholder="e.g., 'What is the standard pipeline?' or 'How do I define phenotypes?'",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 1, 1])

with col2:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

with col3:
    clear_button = st.button("Clear", use_container_width=True)


# ============================================================================
# RESULTS
# ============================================================================

if clear_button:
    st.rerun()

if search_button and search_query:
    with st.spinner("Searching documentation..."):
        docs_context = fetch_documentation(search_query, repo_choice)
    
    if not docs_context or len(docs_context.strip()) < 20:
        st.warning(f"No documentation found for '{search_query}'")
        st.info("Try different search terms or switch repositories")
    else:
        with st.spinner("Generating answer with Claude..."):
            answer = generate_answer(search_query, docs_context)
        
        st.markdown("""<div class="result-box">""", unsafe_allow_html=True)
        st.markdown("## Answer")
        st.markdown(answer)
        st.markdown("""</div>""", unsafe_allow_html=True)
        
        with st.expander("📚 View Source Documentation", expanded=False):
            st.code(docs_context, language="text")
        
        st.session_state.messages.append({
            "query": search_query,
            "answer": answer,
            "repo": repo_choice
        })


# ============================================================================
# HISTORY
# ============================================================================

if st.session_state.messages:
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="section-header">
            <h2>Recent Searches</h2>
            <p>Your previous questions and answers</p>
        </div>
    """, unsafe_allow_html=True)
    
    for msg in reversed(st.session_state.messages[-5:]):
        with st.expander(f"❓ {msg['query'][:60]}"):
            st.markdown(msg['answer'])
            st.caption(f"From: **{msg['repo'].title()}**")


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
    <div class="footer">
        <strong>❤️ BHF Documentation Search</strong><br>
        <p>Powered by Anthropic Claude | Context7 API</p>
        <p>British Heart Foundation Data Science Centre</p>
    </div>
""", unsafe_allow_html=True)
