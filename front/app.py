import time
import streamlit as st
st.set_page_config(
    page_title="Recr-itic", 
    page_icon=" ",           
    layout="centered"           
)

from xai_sdk import Client
from xai_sdk.chat import user, system


# --- Custom CSS for avatars ---
st.markdown("""
    <style>
        /* Assistant avatar (AI): purple */
        div[data-testid="stChatMessageAvatarAssistant"] {
            display: flex;
            width: 2rem;
            height: 2rem;
            flex-shrink: 0;
            border-radius: 0.5rem;
            align-items: center;
            justify-content: center;
            background-color: rgb(144, 124, 255) !important;  /* purple */
            color: rgb(1, 17, 23) !important;
        }

        /* User avatar (Human): blue */
        div[data-testid="stChatMessageAvatarUser"] {
            display: flex;
            width: 2rem;
            height: 2rem;
            flex-shrink: 0;
            border-radius: 0.5rem;
            align-items: center;
            justify-content: center;
            background-color: rgb(76, 135, 240) !important;   /* blue */
            color: white !important;
        }

        /* Space below title */
        .main-header {
            margin-bottom: 1rem;
        }

        /* Hide Streamlit default top padding */
        .block-container {
            padding-top: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)


# --- Title and Restart Button ---
st.markdown('<div class="main-header"><h1>Are You Industry Ready?</h1></div>', unsafe_allow_html=True)

# Add small spacing, then restart button
if st.button("Start Again", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


if "messages" not in st.session_state and "prompt" in st.session_state:
    st.session_state.prompt = st.session_state.prompt + '\n\n Remember to keep it to internship roles and be clear that they are not qualified for specific reasons, you should be very critical but not mean. Also address them in the 2nd person. Stay formal and keep it numbered to 3 clear specific jobs. ie. 1. [Role Title]: [Reason]. Do NOT exceed 150 words and do NOT use the word Oh. The last line should explain why youre choosing other candidates.'
    if not st.session_state.loaded:
        FAKE_THOUGHTS = [
        "💼 Searching for relevant job categories...",
        "🔍 Cross-referencing experience with market data...",
        "📉 Comparing candidate skills to industry expectations...",
        "📊 Calculating probability of success in interviews...",
        "🚫 Filtering out roles far above current qualification level...",
        ]

        placeholder = st.empty()
        with st.spinner("Processing candidate data..."):
            st.session_state.chat.append(user(st.session_state.prompt))
            st.session_state.response = st.session_state.chat.sample()
            total_steps = len(FAKE_THOUGHTS)
            delay_per_step = 12 / total_steps
            for thought in FAKE_THOUGHTS:
                placeholder.markdown(f"**{thought}**")
                time.sleep(delay_per_step)
        placeholder.empty()
        st.session_state.loaded = True
        st.session_state.stated = False

    # --- Final Output ---
    if not st.session_state.stated:
        st.chat_message("assistant").markdown("✅ Review complete. Here’s the final consensus:")
        st.write(st.session_state.response.content)
        st.session_state.stated = True
        st.stop()
        
    st.rerun()

# --- Constants ---
QUESTIONS = [
    "What kind of industry or roles are you interested in?",
    "Do you prefer field work, development, research, sales, or design?",
    "Is your ideal position in a large or small organization?",
    "Please copy/paste your resume or a summary of your experience."
]


# --- State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.current_q = 0
    st.session_state.prompt = (
        "You are a very pretentious, passive aggressive, and critical recruiter. "
        "Use the data assets provided and the following question/answers to find roles the candidate would be interested in but not qualified for, then explain why you wouldnt accept them for each role:\n"
    )
    st.session_state.complete = False
    st.session_state.messages.append({"role": "assistant", "content": QUESTIONS[0]})
    GROK_API_KEY = st.secrets["GROK"]["API_KEY"]
    st.session_state.client = Client(api_key=GROK_API_KEY)
    st.session_state.chat = st.session_state.client.chat.create(model="grok-4")


# --- Display Chat Messages ---
chat_container = st.container()
if not st.session_state.complete:
    with chat_container:
        for message in st.session_state.messages:
            st.chat_message(message["role"]).markdown(message["content"])


# --- User Input ---
if not st.session_state.complete:
    response = st.chat_input("Respond here...")
else:
    response = None  # disable input once complete


# --- Handle Responses ---
if response:
    st.chat_message("user").markdown(response)
    st.session_state.messages.append({"role": "user", "content": response})

    current_question = QUESTIONS[st.session_state.current_q]
    st.session_state.prompt += f"\n{current_question} {response}"
    st.session_state.current_q += 1

    if st.session_state.current_q < len(QUESTIONS):
        next_q = QUESTIONS[st.session_state.current_q]
        st.chat_message("assistant").markdown(next_q)
        st.session_state.messages.append({"role": "assistant", "content": next_q})
    else:
        # --- Clear all messages before loading ---
        for key in list(st.session_state.keys()):
            if key not in ['prompt', 'client', 'chat']:
                del st.session_state[key]
        st.session_state.loaded = False
        st.rerun()
    
