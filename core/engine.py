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
        """Compiles user vocabulary into descriptive prose that matches the Excel column concepts."""
        user_responses = " ".join([msg["content"] for msg in chat_history if msg["role"] == "user"]).lower()
        
        # Accumulate traits using descriptive language matching your Excel database columns
        combat_style = []
        personality_traits = []
        
        # Combat Metrics Scanning
        if any(w in user_responses for w in ["strike", "force", "instantly", "now", "fist", "attack", "rage", "burning", "overwhelming", "retribution"]):
            combat_style.append("Close-range powerhouse focused on high destructive power, explosive speed, and direct physical combat execution.")
            personality_traits.append("Fearless, impulsive, driven by fierce emotional intensity, and prone to open confrontations.")
        if any(w in user_responses for w in ["retreat", "analyze", "wait", "back", "think", "shadow", "cold", "calculated", "trap", "plan", "flaw", "precision", "patiently"]):
            combat_style.append("Long-range tactical combatant utilizing meticulous planning, surgical precision, environment manipulation, and defensive traps.")
            personality_traits.append("Cold, highly calculated, patient under pressure, prioritizing structural observation over impulsive engagements.")
            
        # Development / Resolve Scanning
        if any(w in user_responses for w in ["shatter", "new", "change", "destroy", "break", "complex", "specific", "feared", "nature"]):
            combat_style.append("Highly dynamic utility capabilities with high development potential, altering environmental parameters or breaking established rules.")
            personality_traits.append("Ambitious, disruptive, looking to challenge the status quo, obsessed with evolution or total control.")
        if any(w in user_responses for w in ["protect", "order", "keep", "save", "defend", "outlast", "limit", "save everything", "peace", "revered"]):
            combat_style.append("Defensive utility designed for immense stamina, resilience, protection, and outlasting opponents in high-stakes duels.")
            personality_traits.append("Deeply protective core, intensely loyal to allies, selfless, and driven by a strong moral desire to preserve order.")

        # Default fallbacks if user inputs are short or neutral
        if not combat_style:
            combat_style.append("Balanced adaptable fighter using direct physical capabilities mixed with swift utility maneuvers.")
        if not personality_traits:
            personality_traits.append("Resourceful, observant traveler showing deep versatility when adapting to situational shifts.")

        # Cleanly stitch the profile text into the exact contextual framework used by your excel file
        profile_summary = (
            f"User Personality: {' '.join(personality_traits)}\n"
            f"Combat Capabilities: {' '.join(combat_style)}\n"
            f"Raw Signature Intent: {user_responses}"
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