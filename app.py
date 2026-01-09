import streamlit as st
import time
import re
from whisperer import get_mehman_response, get_mehman_translation

# --- 1. CONFIGURATION & STATE ---
st.set_page_config(
    page_title="Mehman",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Welcome to Mehman. I'm here to help you navigate Pakistan. Ask me about places to visit, local customs, food, or safety!"}
    ]

# --- 2. THE DESIGN ENGINE (CSS) ---
# This translates your React/Tailwind styles into Streamlit CSS
st.markdown("""
<style>
    /* GLOBAL THEME */
    .stApp {
        background-color: #1a1d29;
        color: #ffffff;
    }
    
    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        background-color: #232730;
        border-right: 1px solid #2d3139;
    }
    
    /* HIDE DEFAULT RADIO BUTTONS */
    .stRadio [role=radiogroup] {
        padding-top: 10px;
        background-color: transparent;
    }
    .stRadio label {
        background-color: transparent;
        color: #9ca3af;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 4px;
        transition: all 0.2s;
        border: 1px solid transparent;
        display: flex;
        align-items: center;
        font-size: 16px;
    }
    /* Active State for Sidebar Menu */
    .stRadio label[data-checked="true"] {
        background-color: #2d3139;
        color: #ffffff;
        border-left: 4px solid #14a44d !important;
    }
    .stRadio label:hover {
        background-color: #2d3139;
        color: #ffffff;
    }
    /* Hide the actual radio circle */
    .stRadio div[role='radiogroup'] > label > div:first-child {
        display: none;
    }

    /* CHAT MESSAGES */
    /* User Bubble */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #14a44d !important;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: transparent;
    }
    /* We use some CSS hacks to target the text bubbles specifically if possible, 
       but Streamlit controls this tightly. We stick to global theme alignment. */

    /* INPUT FIELDS */
    .stTextInput input, .stChatInput textarea {
        background-color: #232730 !important;
        color: white !important;
        border: 1px solid #2d3139 !important;
        border-radius: 12px !important;
    }
    .stTextInput input:focus, .stChatInput textarea:focus {
        border-color: #14a44d !important;
        box-shadow: none !important;
    }

    /* BUTTONS */
    .stButton button {
        background-color: #14a44d;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #12923e;
    }
    /* Secondary Button (Clear Chat) */
    .secondary-btn button {
        background-color: transparent;
        border: 1px solid #2d3139;
        color: #9ca3af;
    }
    .secondary-btn button:hover {
        border-color: #14a44d;
        color: #14a44d;
        background-color: transparent;
    }

    /* CARDS (For Translator/About) */
    .custom-card {
        background-color: #232730;
        border: 1px solid #2d3139;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    /* TYPOGRAPHY */
    h1, h2, h3 {
        color: white !important;
    }
    p, li {
        color: #d1d5db;
        line-height: 1.6;
    }
    .accent-text {
        color: #14a44d;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    # Logo Area
    st.markdown("""
        <div style="padding: 10px 0px 20px 0px; border-bottom: 1px solid #2d3139; margin-bottom: 20px;">
            <h1 style="color: #14a44d; font-size: 28px; margin:0; font-weight: 700; letter-spacing: -0.5px;">Mehman</h1>
            <p style="color: #9ca3af; font-size: 14px; margin: 4px 0 0 0;">Navigate Pakistan with AI</p>
        </div>
    """, unsafe_allow_html=True)

    # Navigation Menu
    selected_screen = st.radio(
        "Menu",
        ["Chatbot", "Translator", "About & Safety"],
        label_visibility="collapsed"
    )

    # Spacer
    st.markdown("<div style='height: 50vh'></div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style="border-top: 1px solid #2d3139; padding-top: 20px;">
            <a href="https://ai.google.dev/" target="_blank" style="text-decoration: none; color: #9ca3af; font-size: 13px; display: block; margin-bottom: 8px;">✨ Powered by Gemini</a>
            <a href="#" style="text-decoration: none; color: #9ca3af; font-size: 13px; display: block; margin-bottom: 15px;">💻 View Source Code</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# --- 4. MAIN CONTENT ROUTER ---
main_container = st.container()

with main_container:
    
    # === SCREEN 1: CHATBOT ===
    if selected_screen == "Chatbot":
        # Header
        col1, col2 = st.columns([0.8, 10])
        with col1:
            st.markdown("""
                <div style="width: 48px; height: 48px; background-color: #14a44d; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 24px;">🕌</span>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <h1 style="margin: 0; font-size: 32px;">Mehman Chat</h1>
                <p style="color: #9ca3af; margin: 0;">Your AI companion for travel, safety, and culture</p>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)

        # Chat Area
        for message in st.session_state.messages:
            avatar = "👤" if message["role"] == "user" else "🕌"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Input Area
        if prompt := st.chat_input("Ask about Lahore, food, or safety..."):
            # User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            # Bot Response
            with st.chat_message("assistant", avatar="🕌"):
                message_placeholder = st.empty()
                full_response = ""
                
                with st.spinner("Thinking..."):
                    try:
                        # Context Logic
                        history_context = []
                        for msg in st.session_state.messages[-4:]:
                            role = "User" if msg["role"] == "user" else "Mehman"
                            history_context.append(f"{role}: {msg['content']}")
                        
                        assistant_response = get_mehman_response(prompt, chat_history_context=history_context)
                    except Exception as e:
                        assistant_response = f"⚠️ Error: {str(e)}"
                
                # Format-Safe Typing Effect
                if not isinstance(assistant_response, str):
                    assistant_response = str(assistant_response)
                
                tokens = re.split(r'(\s+)', assistant_response)
                for token in tokens:
                    full_response += token
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.02)
                
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    # === SCREEN 2: TRANSLATOR ===
    elif selected_screen == "Translator":
        # Header
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 30px;">
                <div style="width: 48px; height: 48px; background-color: #14a44d; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 24px; color: white;">🗣️</span>
                </div>
                <div>
                    <h1 style="margin: 0; font-size: 32px; color: white;">Translator</h1>
                    <p style="color: #9ca3af; margin: 0;">English to Polite Urdu (Script & Roman)</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Input Section (Styled Card)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<label style="color: white; margin-bottom: 10px; display: block;">What would you like to say?</label>', unsafe_allow_html=True)
        translate_input = st.text_input("Input", placeholder="e.g. Where is the bathroom?", label_visibility="collapsed")
        
        if st.button("Translate to Urdu", use_container_width=True):
            if translate_input:
                with st.spinner("Translating..."):
                    translation = get_mehman_translation(translate_input)
                
                if translation and "urdu_script" in translation:
                    # Result Cards
                    st.markdown(f"""
                        <div style="margin-top: 30px;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <span style="color: #14a44d; font-weight: bold;">SHOW THIS TO LOCAL</span>
                                <div style="height: 1px; background: #2d3139; flex: 1;"></div>
                            </div>
                            <div style="background: white; border: 2px solid #14a44d; border-radius: 12px; padding: 30px; text-align: right; margin-bottom: 30px;">
                                <p style="color: #1a1d29; font-family: 'Noto Nastaliq Urdu', serif; font-size: 42px; margin: 0; line-height: 1.5;" dir="rtl">
                                    {translation['urdu_script']}
                                </p>
                            </div>
                            
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <span style="color: #f5e6d3; font-weight: bold;">YOU SAY</span>
                                <div style="height: 1px; background: #2d3139; flex: 1;"></div>
                            </div>
                            <div style="background: #232730; border: 1px solid #2d3139; border-radius: 12px; padding: 20px;">
                                <p style="color: #f5e6d3; font-size: 20px; font-style: italic; margin: 0; text-align: center;">
                                    "{translation['roman_urdu']}"
                                </p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Translation failed. Try again.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Quick Phrases
        if not translate_input:
            st.markdown("""
                <div class="custom-card">
                    <h3 style="margin-bottom: 15px;">💡 Common Phrases</h3>
                    <p>Try: <i>"How much is this?"</i>, <i>"Thank you"</i>, or <i>"I am lost"</i>.</p>
                </div>
            """, unsafe_allow_html=True)

    # === SCREEN 3: ABOUT ===
    elif selected_screen == "About & Safety":
        # Header
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 30px;">
                <div style="width: 48px; height: 48px; background-color: #14a44d; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 24px; color: white;">ℹ️</span>
                </div>
                <div>
                    <h1 style="margin: 0; font-size: 32px; color: white;">About Mehman</h1>
                    <p style="color: #9ca3af; margin: 0;">Safety, Features & Tech</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Intro Card
        st.markdown("""
            <div class="custom-card">
                <p style="margin-bottom: 15px;"><b>Mehman</b> ("guest" in Urdu) is an AI-powered assistant designed to help international visitors navigate Pakistan with confidence.</p>
                <p>Built on Google Gemini AI and trained on 19,000+ real travel conversations, it bridges the gap between digital maps and street-level reality.</p>
            </div>
        """, unsafe_allow_html=True)

        # Safety Warning
        st.warning("⚠️ **Important: Verify Official Travel Advisories**\n\nMehman provides general guidance based on public forums. It cannot replace official government safety alerts. Always check with your embassy.")

        # Features Grid
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div class="custom-card" style="border-color: #14a44d;">
                    <h3 style="color: #14a44d;">✅ Capabilities</h3>
                    <ul style="list-style-type: none; padding: 0;">
                        <li>• Polite Urdu Translations</li>
                        <li>• Cultural Etiquette Tips</li>
                        <li>• Authentic Food Recs</li>
                        <li>• Safety Context</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="custom-card" style="border-color: #fbbf24;">
                    <h3 style="color: #fbbf24;">🛡️ Use Responsibly</h3>
                    <ul style="list-style-type: none; padding: 0;">
                        <li>• Verify critical info</li>
                        <li>• Respect local customs</li>
                        <li>• Keep emergency numbers</li>
                        <li>• Use common sense</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)