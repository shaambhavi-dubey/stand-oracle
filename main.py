import os
import traceback
import streamlit as st
from dotenv import load_dotenv

current_directory = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_directory, ".env")
load_dotenv(dotenv_path=env_path)

# Auto-build FAISS index if missing (e.g. on Streamlit Cloud first deploy)
from core.embedder import run_ingestion
if not os.path.exists(os.path.join(current_directory, "data", "stands_index.index")):
    try:
        run_ingestion()
    except Exception as e:
        st.error(f"⚠️ Automated ingestion failed: {str(e)}")

from core.retriever import StandRetriever
from core.engine import OracleEngine
from core.visualizer import StandVisualizer

# Page config
st.set_page_config(page_title="JJBA Stand Oracle", page_icon="🔮", layout="centered")
st.title("JJBA Stand Oracle ★")
st.caption("Discover your stand ><")

# Initialize session state
if "engine" not in st.session_state:
    try:
        st.session_state.engine = OracleEngine()
        st.session_state.retriever = StandRetriever()
        st.session_state.visualizer = StandVisualizer()
        st.session_state.chat_history = []
        st.session_state.turn_count = 0
        st.session_state.stage = "chat"
    except Exception as e:
        st.error(f"💥 Initialization Error: {str(e)}")
        st.code(traceback.format_exc())
        st.session_state.chat_history = []
        st.session_state.stage = "error"

# Show error state clearly instead of blank screen
if st.session_state.get("stage") == "error":
    st.warning("The Oracle failed to initialize. Check the error above, then click below to retry.")
    if st.button("🔄 Retry"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# Generate first question if chat is empty
if len(st.session_state.chat_history) == 0:
    with st.spinner("Connecting to the spirit realm..."):
        try:
            initial_question = st.session_state.engine.generate_next_question([])
            st.session_state.chat_history.append({"role": "assistant", "content": initial_question})
        except Exception as e:
            st.error(f"💥 Initial Question Error: {str(e)}")

# --- CHAT STAGE ---
if st.session_state.stage == "chat":
    for message in st.session_state.chat_history:
        if message["content"] is not None:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_input := st.chat_input("Speak your mind, traveler..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.turn_count += 1
        
        if st.session_state.turn_count >= 6:
            st.session_state.stage = "matching"
        else:
            with st.spinner("The Oracle ponders your words..."):
                try:
                    next_question = st.session_state.engine.generate_next_question(st.session_state.chat_history)
                    st.session_state.chat_history.append({"role": "assistant", "content": next_question})
                except Exception as e:
                    st.error(f"💥 Question Error: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": "The cosmic link flickered. Speak again..."})
        
        st.rerun()

# --- MATCHING STAGE ---
if st.session_state.stage == "matching":
    with st.spinner("The Stand Arrow is deciphering your soul..."):
        try:
            profile = st.session_state.engine.update_hidden_profile(st.session_state.chat_history)
            top_matches = st.session_state.retriever.query(profile, k=1)
            winning_stand = top_matches[0]
            dramatic_reveal = st.session_state.engine.synthesize_dramatic_reveal(profile, winning_stand)
            
            st.session_state.reveal_prose = dramatic_reveal
            st.session_state.matched_data = winning_stand
            st.session_state.stage = "revealed"
            st.rerun()
        except Exception as e:
            st.error(f"💥 Matching Algorithm Error: {str(e)}")
            st.code(traceback.format_exc())

# --- REVEAL STAGE ---
if st.session_state.stage == "revealed":
    stand = st.session_state.matched_data
    
    st.subheader("✨ THE STAND ARROW REVEALS YOUR SOUL")
    st.header(f"{stand['Stand Name']}")
    st.subheader(f"👤 User: {stand['Stand User']} | Part {stand.get('Part', 'Unknown')}")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        base_name = stand.get('Stand User', 'unknown').lower().replace(' ', '_')
        path_jpg = os.path.join(current_directory, "data", "user_images", f"{base_name}.jpg")
        path_jpeg = os.path.join(current_directory, "data", "user_images", f"{base_name}.jpeg")
        
        if os.path.exists(path_jpeg):
            st.image(path_jpeg, use_container_width=True)
        elif os.path.exists(path_jpg):
            st.image(path_jpg, use_container_width=True)
        else:
            st.info(f"📸 Place '{base_name}.jpeg' in data/user_images/")
            
    with col2:
        chart_figure = st.session_state.visualizer.generate_radar_chart(stand)
        st.pyplot(chart_figure)
        
    st.divider()
    st.markdown(st.session_state.reveal_prose)
    
    if st.button("Re-enter the Chambers"):
        st.session_state.clear()
        st.rerun()