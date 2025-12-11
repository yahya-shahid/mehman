import streamlit as st
import re
import time
from whisperer import get_mehman_response

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Mehman Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (To mimic the screenshot's clean look) ---
st.markdown("""
<style>
    /* 1. HIDE RADIO BUTTON CIRCLES to make them look like a menu */
    .stRadio [role=radiogroup] {
        padding-top: 10px;
    }
    .stRadio label {
        background-color: transparent;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stRadio label:hover {
        background-color: #808495;
    }
    /* Hide the actual circle */
    .stRadio div[role='radiogroup'] > label > div:first-child {
        display: none; 
    }
    
    /* 2. HEADER STYLING */
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0;
        color:#f5f5f7; /* Streamlit Dark Grey */
    }
    .header-subtitle {
        font-size: 1.2rem;
        color: #808495;
        margin-bottom: 2rem;
    }
    
    /* 3. CHAT BUBBLE TWEAKS */
    .stChatMessage {
        background-color: transparent;
    }
        
    
    /* Make headers pop */
    .stMarkdown h3 {
        color: #2E7D32; /* Pakistan Green */
        margin-top: 20px;
        font-size: 1.2rem;
    }
    
    /* Add spacing to lists */
    .stMarkdown ul {
        margin-bottom: 20px;
    }
    
    /* Make bold text stand out */
    .stMarkdown strong {
        color: #f5f5f7;
        font-weight: 700;
            
    /* 4. TRANSLATOR CARD STYLING */
    .urdu-text {
        font-family: 'Noto Nastaliq Urdu', serif; /* Tries to use a nice Urdu font */
        font-size: 32px;
        text-align: right;
        color: #2E7D32;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-top: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .roman-text {
        font-size: 18px;
        text-align: center;
        color: #555;
        font-style: italic;
        margin-top: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION (Matches the screenshot left panel) ---
with st.sidebar:
    
    
    # Navigation Menu (Hidden Radio Button)
    selected_page = st.radio(
        "Navigation", 
        ["Chatbot", "Translator", "About & Safety"],
        label_visibility="collapsed"
    )

    st.markdown("---")


    st.markdown("---")
    
    # Bottom Links
    st.markdown("[Get a Gemini API key](https://aistudio.google.com/)")
    st.markdown("[View the source code](#)")
    
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# --- PAGE 1: CHATBOT (Main Interface) ---
if selected_page == "Chatbot":
    
    # 1. The Header (Matches the "Chatbot" title in image)
    col1, col2 = st.columns([1, 15])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2040/2040946.png", width=50) # Generic Chat Icon
    with col2:
        st.markdown('<h1 style="margin-top: -10px;">Mehman</h1>', unsafe_allow_html=True)
    
    st.caption("🚀 A Chatbot powered by **Mehman Logic**")

    # 2. Chat Logic
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧙‍♂️" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # Initial Bot Greeting (if empty)
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🧙‍♂️"):
            st.markdown("How can I help you navigate Pakistan today?")

    # Input Area
    if prompt := st.chat_input("Your message"):
        
        # User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Assistant Response
        with st.chat_message("assistant", avatar="🧙‍♂️"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("Thinking..."):
                try:
                    # --- NEW CONTEXT LOGIC ---
                    # 1. Grab the last 4 messages so the bot remembers the conversation
                    history_context = []
                    for msg in st.session_state.messages[-4:]:
                        role = "User" if msg["role"] == "user" else "Mehman"
                        history_context.append(f"{role}: {msg['content']}")

                    # 2. Send the prompt AND the history to the backend
                    assistant_response = get_mehman_response(prompt, chat_history_context=history_context)
                    # -------------------------
                except Exception as e:
                    assistant_response = f"⚠️ Error: {str(e)}"
            
          # Typewriter effect (Format-Safe Version)
            if not isinstance(assistant_response, str):
                assistant_response = str(assistant_response)

            # 1. Use Regex to split by tokens BUT keep the whitespace/newlines
            import re
            tokens = re.split(r'(\s+)', assistant_response)
            
            for token in tokens:
                full_response += token
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.02) # Slightly faster typing feels smoother
            
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- PAGE 2: TRANSLATOR (Active) ---
elif selected_page == "Translator":
    
    # Header
    col1, col2 = st.columns([1, 15])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3898/3898150.png", width=50) 
    with col2:
        st.markdown('<h1 style="margin-top: -10px;">Cultural Bridge</h1>', unsafe_allow_html=True)
    
    st.caption("🗣️ Translate English to **Polite Urdu** (Native Script & Roman)")

    # Input Area
    st.markdown("### What do you want to say?")
    to_translate = st.text_area("", placeholder="Ex: How much is this? / I need water / Where is the bathroom?", height=100)
    
    # Translate Action
    if st.button("Translate to Urdu", use_container_width=True, type="primary"):
        if to_translate:
            # Inline import to keep it simple
            from whisperer import get_mehman_translation
            
            with st.spinner("Consulting the linguist..."):
                translation = get_mehman_translation(to_translate)
            
            if translation and "urdu_script" in translation:
                # 1. The Visual Card (For the Local)
                st.markdown("#### 📱 Show this to the local:")
                st.markdown(f'<div class="urdu-text">{translation["urdu_script"]}</div>', unsafe_allow_html=True)
                
                # 2. The Pronunciation (For You)
                st.markdown("#### 🗣️ You say:")
                st.markdown(f'<p class="roman-text">"{translation["roman_urdu"]}"</p>', unsafe_allow_html=True)
                
                # 3. Cultural Tip
                st.info("💡 **Mehman Tip:** We automatically made this polite ('Aap' instead of 'Tu'). Placing your hand on your heart while asking shows extra respect!")
                
            else:
                st.error("⚠️ Translation failed. Please try again.")

# --- PAGE 3: ABOUT (Placeholder) ---
elif selected_page == "About & Safety":
    st.title("ℹ️ About Mehman")
    st.warning("Always check official government travel advisories.")
    st.markdown("""
    **Mehman** is an AI powered by:
    - Real Reddit Conversations
    - Google Gemini AI
    """)