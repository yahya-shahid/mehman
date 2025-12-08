import streamlit as st
import time
from whisperer import get_mehman_response

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Mehman: The Cultural Whisperer",
    page_icon="🕌",
    layout="wide",  # 'wide' layout uses more screen space
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* Give the main title a nice look */
    .main-title {
        font-size: 3rem;
        color: #2E7D32; /* Pakistan Green */
        text-align: center;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .subtitle {
        text-align: center;
        color: #555;
        margin-bottom: 30px;
        font-style: italic;
    }
    /* Style the chat bubbles slightly */
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://www.flaticon.com/free-icon/pakistan_3973547", width=80)
    st.title("About Mehman")
    st.markdown("""
    **Mehman** is your AI companion for traveling in Pakistan. 
    
    它 It is powered by:
    - 🧠 **Real Reddit Conversations** (RAG)
    - 🤖 **Google Gemini AI**
    """)
    
    st.divider()
    
    st.warning("⚠️ **Safety Disclaimer:**\nMehman provides advice based on public forums. Always check official government travel advisories for critical safety updates.")
    
    st.divider()
    
    # Reset Button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- MAIN HEADER ---
st.markdown('<p class="main-title">🕌 Mehman</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI Guide to Pakistani Etiquette, Safety, and Logistics</p>', unsafe_allow_html=True)

# --- TABS LAYOUT (Pre-work for Part 6) ---
tab1, tab2 = st.tabs(["💬 Ask Advice", "🗣️ Translator (Coming Soon)"])

# --- TAB 1: THE CHATBOT ---
with tab1:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🕌"):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ex: Is it safe to wear shorts in Lahore?"):
        
        # 1. Show User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 2. Generate Assistant Response
        with st.chat_message("assistant", avatar="🕌"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("Consulting local advice..."):
                try:
                    assistant_response = get_mehman_response(prompt)
                except Exception as e:
                    assistant_response = f"⚠️ Error: {str(e)}"

            # Typing effect
            # (Safety check: ensure response is a string)
            if not isinstance(assistant_response, str):
                assistant_response = str(assistant_response)

            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # 3. Save Assistant Message
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- TAB 2: TRANSLATOR (Placeholders) ---
with tab2:
    st.header("🇵🇰 Urdu Translator")
    st.caption("Type a phrase in English to see it in Urdu script and Roman Urdu.")
    st.info("🛠️ This feature is under construction. (Part 6)")