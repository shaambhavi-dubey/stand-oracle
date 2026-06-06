# core/engine.py

import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

class OracleEngine:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        env_path = os.path.join(project_root, ".env")
        
        load_dotenv(dotenv_path=env_path)
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(f"Missing OPENROUTER_API_KEY inside the configuration file at: {env_path}")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501", 
                "X-Title": "JoJo Stand Oracle"          
            }
        )
        self.model_name = "meta-llama/llama-3.3-70b-instruct:free"
        
        # Streamlined 9 direct behavioral profiling questions
        self.question_pool = [
            {"text": "When backed into a corner, do you strike back instantly with raw force, or do you retreat to analyze?", "type": "combat"},
            {"text": "If you acquired a tool of absolute power, would you use it to protect order, or shatter it to create something new?", "type": "resolve"},
            {"text": "In a high-stakes conflict, do you prefer acting alone with absolute control, or organizing a team strategy?", "type": "tactics"},
            {"text": "Does an enemy's betrayal spark an immediate, burning rage inside you, or a cold, calculated plan to neutralize them?", "type": "combat"},
            {"text": "Would you rather have a simple ability pushed to its absolute physical limit, or a complex, highly specific utility?", "type": "resolve"},
            {"text": "When tracking a target, do you hunt them down aggressively out in the open, or set a silent trap in the shadows?", "type": "tactics"},
            {"text": "If a mission demands it, are you willing to sacrifice a critical asset to win, or will you risk failure to save everything?", "type": "moral"},
            {"text": "Do you perform at your best when under intense, immediate pressure, or when given ample time to plan?", "type": "moral"},
            {"text": "In a duel, do you focus on completely overwhelming your opponent's guard, or outlasting them until they trip up?", "type": "combat"}
        ]
        
        # Select exactly 4 random questions for this session
        self.active_questions = random.sample(self.question_pool, 4)
        
    def generate_next_question(self, chat_history):
        """Serves direct, short prompts instantly from the active session pool."""
        assistant_turns = [msg for msg in chat_history if msg["role"] == "assistant"]
        current_turn_index = len(assistant_turns)
        
        if current_turn_index < len(self.active_questions):
            return self.active_questions[current_turn_index]["text"]
            
        return "Analysis complete. The Stand Arrow is initializing..."

    def update_hidden_profile(self, chat_history):
        """Locally scores text responses against tactical dimensions to prepare the FAISS query text."""
        user_responses = " ".join([msg["content"] for msg in chat_history if msg["role"] == "user"]).lower()
        
        # Internal Profile Matrix tracking: [Destructive, Speed, Range, Stamina, Precision, Dev]
        base_scores = {"Destructive": 3, "Speed": 3, "Range": 3, "Stamina": 3, "Precision": 3, "Dev": 3}
        
        # Keyword scanners mapping semantic weights across profile parameters
        if any(w in user_responses for w in ["strike", "force", "instantly", "now", "fist", "attack", "rage", "burning", "overwhelming"]):
            base_scores["Destructive"] += 2
            base_scores["Speed"] += 1
        if any(w in user_responses for w in ["retreat", "analyze", "wait", "back", "think", "shadow", "cold", "calculated", "trap", "plan"]):
            base_scores["Precision"] += 2
            base_scores["Range"] += 1
        if any(w in user_responses for w in ["shatter", "new", "change", "destroy", "break", "complex", "specific"]):
            base_scores["Dev"] += 2
            base_scores["Destructive"] += 1
        if any(w in user_responses for w in ["protect", "order", "keep", "save", "defend", "outlast", "limit", "save everything"]):
            base_scores["Stamina"] += 2
            base_scores["Precision"] += 1
        if any(w in user_responses for w in ["alone", "myself", "control", "solo", "own", "sacrifice"]):
            base_scores["Speed"] += 1
            base_scores["Precision"] += 1
        if any(w in user_responses for w in ["team", "coordinate", "strategy", "group", "share", "risk"]):
            base_scores["Range"] += 1
            base_scores["Dev"] += 1

        # Capture raw user vocabulary to preserve distinct semantic profiles
        raw_signature = " ".join([msg["content"] for msg in chat_history if msg["role"] == "user"])

        profile_summary = (
            f"Subject displays a structural configuration emphasizing a Destructive capacity of {base_scores['Destructive']}/5 "
            f"and tactical Speed of {base_scores['Speed']}/5. Tactical movement profile exhibits Range: {base_scores['Range']}/5, "
            f"Stamina: {base_scores['Stamina']}/5, Precision: {base_scores['Precision']}/5, and Development Potential: {base_scores['Dev']}/5. "
            f"\n\nPsychological Vocabulary Signature: {raw_signature}"
        )
        return profile_summary

    def synthesize_dramatic_reveal(self, final_profile, stand_metadata):
        """Fuses the data parameters into an intense JJBA narrative presentation."""
        prompt = (
            f"Write a sharp, high-impact presentation matching the user's soul with Stand Name: {stand_metadata['Stand Name']} "
            f"built by User: {stand_metadata['Stand User']}. Focus exactly on how their traits map to capabilities: {stand_metadata['Ability']}. "
            f"Keep it punchy, powerful, and end with an iconic call-out."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8, 
                max_tokens=500,
                timeout=4.0
            )
            return response.choices[0].message.content
        except:
            return (
                f"### ✨ THE SHAPE OF YOUR FIGHTING SPIRIT\n\n"
                f"Your analytical patterns and tactical decisions perfectly align with **{stand_metadata['Stand Name']}** (User: {stand_metadata['Stand User']}).\n\n"
                f"**Soul Profile Evaluation:** Your vocabulary vectors directly map to its parameter stats. "
                f"Its capability—*{stand_metadata['Ability']}*—is the ultimate crystallization of your focus. Wield it well."
            )