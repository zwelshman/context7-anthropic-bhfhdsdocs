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

# Apply custom styling
st.markdown("""
    <style>
        /* Main background and text */
        .main {
            background: linear-gradient(135deg, #f8f9fa 0%, #e8eef5 100%);
        }
        
        /* Header styling */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            color: #3b82f6;
            font-weight: 600;
            margin-top: 1.5rem;
        }
        
        /* Source sections */
        .source-section {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Answer section */
        .answer-section {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border: 2px solid #3b82f6;
            margin: 1rem 0;
            box-shadow: 0 4px 8px rgba(59, 130, 246, 0.15);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            background: #f0f4f8;
            border-radius: 6px;
            color: #1e3a8a;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] [data-baseweb="tab"] {
            background: #3b82f6;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = Anthropic()

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

repo_choice = st.sidebar.radio(
    "Select Repository:",
    options=["bhfdsc/documentation", "bhfdsc/standard-template"],
    help="Choose which BHF repository to search"
)

api_key = st.sidebar.text_input(
    "Context7 API Key:",
    type="password",
    value="ctx7sk-6625dd2b-6b13-4ca8-b0ae-4d974713053f",
    help="Your Context7 API key for documentation access"
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
    st.metric("Repo", repo_choice.split("/")[1])

st.markdown(f"Search and query documentation from **{repo_choice}** with AI-powered answers")

# Functions
def fetch_documentation(topic, repo, page=1):
    """Fetch documentation context from Context7 API"""
    url = f"https://context7.com/api/v2/docs/info/{repo}"
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
    url = f"https://context7.com/api/v2/docs/code/{repo}"
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
        model="claude-opus-4.5",
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
