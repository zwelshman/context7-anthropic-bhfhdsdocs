import streamlit as st
import requests
from anthropic import Anthropic

# Set page config
st.set_page_config(
    page_title="BHF Documentation Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling - BHF Color Scheme
st.markdown("""
    <style>
        /* BHF Color Scheme */
        :root {
            --bhf-navy: #003d7a;
            --bhf-red: #c41e3a;
            --bhf-light-blue: #e8f0ff;
            --bhf-dark-blue: #001f4d;
        }
        
        /* Main background and text */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
        }
        
        /* Header styling */
        h1 {
            color: #003d7a;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            color: #003d7a;
            font-weight: 600;
            margin-top: 1.5rem;
        }
        
        /* Source sections */
        .source-section {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #c41e3a;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0, 61, 122, 0.08);
        }
        
        /* Answer section */
        .answer-section {
            background: linear-gradient(135deg, #f0f7ff 0%, #e8eef5 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border: 2px solid #003d7a;
            margin: 1rem 0;
            box-shadow: 0 4px 8px rgba(0, 61, 122, 0.12);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #003d7a 0%, #002147 100%);
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] label {
            color: white;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            background: #f0f4f8;
            border-radius: 6px;
            color: #003d7a;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] [data-baseweb="tab"] {
            background: #003d7a;
            color: white;
            border-bottom: 3px solid #c41e3a;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #003d7a 0%, #002147 100%);
            color: white;
            border: none;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #c41e3a 0%, #8b0000 100%);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY"))

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

# Check API keys
context7_key = st.secrets.get("CONTEXT7_API_KEY", "")
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "")

col1, col2 = st.sidebar.columns([3, 1])
with col1:
    st.sidebar.markdown("**API Status**")
with col2:
    pass

status_cols = st.sidebar.columns([2, 2])
with status_cols[0]:
    st.markdown(f"{'✅ Context7' if context7_key else '❌ Context7'}")
with status_cols[1]:
    st.markdown(f"{'✅ Anthropic' if anthropic_key else '❌ Anthropic'}")

if not context7_key or not anthropic_key:
    st.sidebar.error("⚠️ Missing API keys in secrets")
    st.stop()

api_key = context7_key

st.sidebar.divider()

repo_choice = st.sidebar.radio(
    "Select Repository:",
    options=["documentation", "standard-template"],
    format_func=lambda x: f"🏥 BHF {x.replace('-', ' ').title()}",
    help="Choose which BHF repository to search"
)

st.sidebar.divider()
st.sidebar.info(
    "📚 This app searches BHF repository documentation and generates answers using Claude AI."
)

# Main header
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🔍 BHF Documentation Search")
with col2:
    repo_display = repo_choice.replace('-', ' ').title()
    st.markdown(f"<div style='padding-top: 1rem; text-align: right; color: #003d7a; font-weight: 600;'>📦 {repo_display}</div>", unsafe_allow_html=True)

st.markdown(f"Search **BHF {repo_choice.replace('-', ' ').title()}** with AI-powered answers", unsafe_allow_html=True)

# Functions
def fetch_documentation(topic, repo, page=1):
    """Fetch documentation context from Context7 API"""
    repo_full = f"bhfdsc/{repo}"
    url = f"https://context7.com/api/v2/docs/info/{repo_full}"
    params = {
        "type": "txt",
        "topic": topic,
        "page": page
    }
    headers = {"Authorization": api_key}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching documentation: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)}"

def fetch_code_context(topic, repo, page=1):
    """Fetch code context from Context7 API"""
    repo_full = f"bhfdsc/{repo}"
    url = f"https://context7.com/api/v2/docs/code/{repo_full}"
    params = {
        "type": "txt",
        "topic": topic,
        "page": page
    }
    headers = {"Authorization": api_key}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return ""
    except requests.exceptions.RequestException:
        return ""

def get_best_answer(topic, docs_context, code_context):
    """Use Claude to generate the best answer based on documentation and code context"""
    prompt = f"""Based on the following documentation and code examples, provide a clear and concise answer to the question.

Question: {topic}

Documentation Context:
{docs_context}"""

    if code_context.strip():
        prompt += f"""

Code Examples and Context:
{code_context}"""

    prompt += "\n\nPlease provide a comprehensive answer based on the provided documentation and code examples. Be specific and actionable."

    message = st.session_state.client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return message.content[0].text

# Main search interface
st.markdown("### 🔎 Search Documentation")

col1, col2 = st.columns([4, 1])
with col1:
    search_query = st.text_input(
        "What would you like to know?",
        placeholder="e.g., 'what is the standard pipeline?' or 'how to configure the deployment'",
        label_visibility="collapsed"
    )
with col2:
    search_button = st.button("Search", use_container_width=True, type="primary")

# Process search
if search_button and search_query:
    with st.spinner("🔄 Searching documentation..."):
        # Fetch contexts
        docs_context = fetch_documentation(search_query, repo_choice)
        code_context = fetch_code_context(search_query, repo_choice)
        
        # Generate answer
        with st.spinner("✨ Generating answer with Claude..."):
            answer = get_best_answer(search_query, docs_context, code_context)
    
    # Display results in tabs
    tab1, tab2, tab3 = st.tabs(["📖 Answer", "📚 Documentation", "💻 Code Context"])
    
    with tab1:
        st.markdown('<div class="answer-section">', unsafe_allow_html=True)
        st.markdown("### Answer")
        st.markdown(answer)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="source-section">', unsafe_allow_html=True)
        if docs_context.startswith("Error") or docs_context.startswith("Request"):
            st.warning(docs_context)
        else:
            st.markdown("### Documentation Context")
            st.text(docs_context)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        if code_context.strip():
            st.markdown('<div class="source-section">', unsafe_allow_html=True)
            st.markdown("### Code Examples")
            st.code(code_context, language="python")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No code context available for this query.")
    
    # Store in session for reference
    st.session_state.messages.append({
        "query": search_query,
        "answer": answer,
        "repo": repo_choice
    })

# Show previous searches
if st.session_state.messages:
    st.divider()
    st.markdown("### 📋 Previous Searches")
    
    for i, msg in enumerate(reversed(st.session_state.messages[-5:])):  # Show last 5
        with st.expander(f"❓ {msg['query'][:60]}...", expanded=False):
            st.markdown(msg['answer'])
            st.caption(f"From: {msg['repo']}")

# Footer
st.divider()
st.caption("🤖 Powered by Anthropic Claude | Context7 Documentation API")
