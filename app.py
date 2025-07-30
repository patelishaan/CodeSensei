import os
import streamlit as st
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv() 

python_agent_id = "ag:27f5718d:20250726:python-agent:6e6c8fa5"
explaining_agent_id = "ag:27f5718d:20250730:professor:72086301"

# --- Agent 1: Code Generation ---
# function only generates code nothing else
#@st.cache_data # Cache the function to avoid re-running on every interaction
def make_code_python(client, planning_agent_id , query):
    
    try:
        response = client.agents.complete(
            agent_id=planning_agent_id,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        result = response.choices[0].message.content
        if result.startswith("```python"):
            result = result[9:]
        if result.endswith("```"):
            result = result[:-3]
        return result.strip()
    except Exception as e:
        return f"❌ [Agent 1: Coder] Request failed: {e}"

# --- Agent 2: Code Analysis ---
# this agent explains the code w examples and a dry run
#@st.cache_data # Cache the function
def analyze_code_python(client, explaining_agent_id, code_to_analyze):
    """Analyzes Python code using the Analyzer Agent."""
    analyzer_system_prompt = """
    You are `Code-Insight`, an expert AI programming analyst. Your mission is to deliver a comprehensive and educational analysis of any given code snippet. Your response must be structured, clear, and technically precise.

    Given a piece of code from the user, you must follow these steps in order:

    1. **High-Level Summary:** In a single paragraph, concisely describe the code's overall purpose and functionality.
    2. **Logic & Algorithm Breakdown:** Explain the core algorithm and logical blocks.
    3. **Execution Analysis:** Provide a sample input, a step-by-step dry run in a Markdown table, and the final output.
    4. **Deeper Insights:** State the Time and Space Complexity and suggest potential improvements.

    Structure your entire response using clear Markdown headings for each section.
    """
    
    try:
        response = client.agents.complete(
            agent_id=explaining_agent_id,
            messages=[
                {"role": "system", "content": analyzer_system_prompt},
                {"role": "user", "content": code_to_analyze}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ [Agent 2: Analyzer] Request failed: {e}"

# --- Main App Logic ---
st.set_page_config(layout="wide")
st.title("🤖 Code Sensei - Multi-Agent DSA Assistant")

# Get Mistral API key from environment variables/secrets
api_key = os.environ.get("MISTRAL_API_KEY")

coder_agent_id = python_agent_id 
analyzer_agent_id = explaining_agent_id

if not api_key:
    st.error("Error: Environment variable 'MISTRAL_API_KEY' not found. Please set it in your repository's secrets.")
else:
    client = Mistral(api_key=api_key)

    # User input form
    with st.form("code_generator_form"):
        user_query = st.text_area("▶️ What coding task would you like to perform?", height=100)
        submitted = st.form_submit_button("Generate & Analyze")

    if submitted and user_query:
        with st.spinner("🤖 Agent 1 is generating code..."):
            generated_code = make_code_python(client, coder_agent_id, user_query)
        
        st.subheader("✅ Generated Code")
        st.code(generated_code, language='python')

        with st.spinner("🧐 Agent 2 is analyzing the code..."):
            code_analysis = analyze_code_python(client, analyzer_agent_id, generated_code)

        st.subheader("📝 Code Analysis")
        st.markdown(code_analysis)

    elif submitted and not user_query:
        st.warning("Please enter a coding task.")
