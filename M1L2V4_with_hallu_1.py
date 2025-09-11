# import packages
from langchain_ollama import ChatOllama  # Chat model for Ollama
from langchain_core.messages import SystemMessage, HumanMessage
import streamlit as st

@st.cache_data
def get_response(user_prompt, temperature1, response_type="standard"):
    # Initialize chat model with explicit temperature setting
    chat_model = ChatOllama(
        model="llama3.2",
        temperature=float(temperature1)  # Ensure temperature is float
    )
    
    # Return None if no user input is provided
    if not user_prompt:
        return None

    # Adjust system message based on response type
    if response_type == "creative":
        system_content = "You are an imaginative AI assistant. Be creative and think outside the box while responding."
    elif response_type == "factual":
        system_content = "You are a precise AI assistant. Stick to verified facts only. If unsure, explicitly state that."
    else:
        system_content = "You are a helpful AI assistant."
    
    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_prompt)
    ]

    response = chat_model.invoke(messages)
    return response

st.set_page_config(page_title="Generative AI Chatbot", layout="wide")

st.title("Hello, GenAI!")
st.write("This is your first Streamlit app.")

# Add a text input box for the user prompt
user_prompt = st.chat_input(placeholder="Ask anything...")


# Initialize session state for temperature changes if not exists
if 'temp_changed' not in st.session_state:
    st.session_state.temp_changed = False

if 'previous_responses' not in st.session_state:
    st.session_state.previous_responses = {}

def on_temp_change():
    st.session_state.temp_changed = True
    
# Add a slider for temperature
temperature_param = st.slider(
    "Model temperature:",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.01,
    help="Controls randomness: 0 = deterministic, 1 = very creative",
    on_change=on_temp_change,
    key="temperature"  # Add a key to access in session state
)

# Analysis section
st.subheader("Temperature Analysis")


# Generate responses when temperature changes or on first load
if st.session_state.temp_changed or not st.session_state.get('previous_responses'):
    with st.spinner("Generating responses for analysis..."):
         # Get standard response
        standard_response = get_response(user_prompt, temperature_param, "standard")
        
        # Get factual response
        factual_response = get_response(user_prompt, temperature_param, "factual")

        # Get creative response
        creative_response = get_response(user_prompt, temperature_param, "creative")
        
        # Store responses in session state
        if standard_response != None and factual_response != None and creative_response != None:
            st.session_state.previous_responses = {
                'standard': standard_response.content,
                'factual': factual_response.content,
                'creative': creative_response.content
            }
        
        # Reset the temperature change flag
        st.session_state.temp_changed = False

# Display results
col1, col2, col3 = st.columns(3)

if standard_response != None and factual_response != None and creative_response != None:
    with col1:
        st.write("### Standard Output")
        st.write(st.session_state.previous_responses['standard'])

    with col2:
        st.write("### Factual Output")
        st.write(st.session_state.previous_responses['factual'])

    with col3:
        st.write("### Creative Output")
        st.write(st.session_state.previous_responses['creative'])
        

# Analysis metrics
st.write("### Analysis Metrics")
col4, col5, col6 = st.columns(3)

if standard_response != None and factual_response != None and creative_response != None:
    with col4:
        standard_score = st.slider(
            "Standard Accuracy Score (1-10)",
            min_value=1,
            max_value=10,
            value=5,
            key="standard_score"
        )
        
    with col5:
        factual_score = st.slider(
            "Factual Accuracy Score (1-10)",
            min_value=1,
            max_value=10,
            value=5,
            key="factual_score"
        )

    with col6:
        creativity_score = st.slider(
            "Creativity Accuracy Score (1-10)",
            min_value=1,
            max_value=10,
            value=5,
            key="creativity_score"
        )

# Hallucination analysis
hallucination_analysis = st.text_area(
    "Hallucination Analysis",
    placeholder="Describe any potential hallucinations or inaccuracies you notice in the responses..."
)

# Add a divider for clarity
st.divider()
