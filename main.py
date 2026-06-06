# main.py

import os
import streamlit as st
from dotenv import load_dotenv

# Force directory calculations to bind environment memory instantly
current_directory = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_directory, ".env")
load_dotenv(dotenv_path=env_path)

from core.retriever import StandRetriever
from core.engine import OracleEngine
from core.visualizer import StandVisualizer

# Page Setup Configurations
st.set_page_config(page_title="JJBA Stand Oracle", page_icon="🔮", layout="centered")
st.title("🔮 The Stand Arrow Chambers")
st.caption("Discover your fighting spirit through RAG-driven vector profiling calculations.")

# Initialize core states inside server memory trackers
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

# Generate initialization question from backend if timeline log is empty
if len(st.session_state.chat_history) == 0:
    with st.spinner("Connecting to the spirit realm..."):
        try:
            initial_question = st.session_state.engine.generate_next_question([])
            if initial_question is None:
                initial_question = "When backed into a corner, do you strike back instantly with raw force, or do you retreat to analyze the environment?"
            st.session_state.chat_history.append({"role": "assistant", "content": initial_question})
        except Exception as e:
            st.error(f"💥 Initial Question Error: {str(e)}")

# Presentation Layer: Chat interaction sequence
if st.session_state.stage == "chat":
    # Display conversation logs cleanly
    for message in st.session_state.chat_history:
        if message["content"] is not None:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Wait for User input
    if user_input := st.chat_input("Speak your mind, traveler..."):
        # Append user response to log
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.turn_count += 1
        
        # Process matching after exactly 6 conversational turns have completed
        if st.session_state.turn_count >= 6:
            st.session_state.stage = "matching"
        else:
            with st.spinner("The Oracle ponders your words..."):
                try:
                    next_question = st.session_state.engine.generate_next_question(st.session_state.chat_history)
                    if next_question is None:
                        next_question = "The shadows shift as you speak. Tell me more, traveler..."
                    st.session_state.chat_history.append({"role": "assistant", "content": next_question})
                except Exception as e:
                    st.error(f"💥 Next Question Generation Error: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": "The cosmic link flickered. Speak again..."})
        
        st.rerun()

# RAG Integration Strategy State Execution Block
if st.session_state.stage == "matching":
    with st.spinner("The Stand Arrow is reacting violently to your fighting spirit..."):
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

# Presentation Layer: Structural Display Grid Screen Card
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
            st.info(f"📸 Asset Missing! Place '{base_name}.jpeg' in your data/user_images/ folder.")
            
    with col2:
        chart_figure = st.session_state.visualizer.generate_radar_chart(stand)
        st.pyplot(chart_figure)
        
    st.divider()
    st.markdown(st.session_state.reveal_prose)
    
    if st.button("Re-enter the Chambers"):
        st.session_state.clear()
        st.rerun()