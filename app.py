import streamlit as st
import time
from whisperer import get_mehman_response

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Mehman: The Cultural Whisperer",
    page_icon="🕌",
    layout="centered"
)

# --- CUSTOM STYLING (Optional) ---
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
    }
    .stChatInput {
        padding-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🕌 Mehman: Your Pakistan Guide")
st.caption("Ask me about safety, etiquette, or travel logistics in Pakistan.")

# --- SESSION STATE (Chat History) ---
# Streamlit uses st.session_state to hold persistent variables like chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ex: Is it safe to wear shorts in Lahore?"):
    # 1. Display User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Get AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Show a little "thinking" spinner
        with st.spinner("Consulting local advice..."):
            try:
                # Call our backend function from Part 4
                assistant_response = get_mehman_response(prompt)
            except Exception as e:
                assistant_response = f"⚠️ Sorry, I encountered an error: {e}"

        # Simulate typing effect (optional, looks cool)
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # 3. Save AI Message to History
    st.session_state.messages.append({"role": "assistant", "content": full_response})