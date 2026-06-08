import os
import random
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

class OracleEngine:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        env_path = os.path.join(project_root, ".env")
        
        load_dotenv(dotenv_path=env_path)
        
        api_key = None
        if "OPENROUTER_API_KEY" in st.secrets:
            api_key = st.secrets["OPENROUTER_API_KEY"]
        else:
            api_key = os.getenv("OPENROUTER_API_KEY")
            
        if not api_key:
            raise ValueError("Missing OPENROUTER_API_KEY! Please check your Streamlit Cloud Advanced Secrets or local .env file.")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "JoJo Stand Oracle"
            }
        )
        self.model_name = "meta-llama/llama-3.3-70b-instruct:free"
        
        # Question pool split by category — 2 picked from each for balanced profiling
        self.question_pool = {
            "combat": [
                {"text": "When backed into a corner, do you strike back instantly with raw force, or retreat to analyze the situation?"},
                {"text": "In a duel, do you focus on overwhelming your opponent completely, or outlasting them until they make a mistake?"},
                {"text": "When hunting a target, do you go in openly and aggressively, or set a silent trap from the shadows?"},
            ],
            "ideology": [
                {"text": "If you could reshape the world, would you burn the current one down to build your ideal, or refine what exists into something better?"},
                {"text": "Do you believe the end always justifies the means, or are there lines you would never cross regardless of the goal?"},
                {"text": "Is your deepest drive personal ambition and power, or the wellbeing of the people around you?"},
            ],
            "emotional": [
                {"text": "When someone you love is in danger, does it make you reckless and desperate, or sharpen your focus into something cold and precise?"},
                {"text": "Have you ever had to walk away from something you cared about to do what was right?"},
                {"text": "Do you carry your past pain as fuel that drives you forward, or as weight you are still learning to put down?"},
            ],
            "philosophy": [
                {"text": "Do you believe fate is something to be accepted and fulfilled, or something to be fought and rewritten?"},
                {"text": "Would you sacrifice yourself completely for a cause larger than your own life?"},
                {"text": "Is true strength about never losing, or about getting back up every single time you fall?"},
            ],
        }
        
        # Pick 2 from each category = 6 balanced questions per session
        self.active_questions = []
        for category in self.question_pool.values():
            self.active_questions.extend(random.sample(category, 2))
        random.shuffle(self.active_questions)
        
    def generate_next_question(self, chat_history):
        assistant_turns = [msg for msg in chat_history if msg["role"] == "assistant"]
        current_turn_index = len(assistant_turns)
        if current_turn_index < len(self.active_questions):
            return self.active_questions[current_turn_index]["text"]
        return "Analysis complete. The Stand Arrow is initializing..."

    def _keyword_fallback(self, dialogue):
        """
        Broad keyword fallback covering combat, ideology, emotional, and philosophical answers.
        Used only when LLM times out.
        """
        d = dialogue.lower()

        # --- Personality mapping ---
        if any(w in d for w in ["fate", "destiny", "god", "design", "accept", "fulfil", "plan", "universe",
                                  "inevitable", "meant to", "serene", "tranquil", "certain", "reset", "rebirth"]):
            personality = "tranquil and absolute, believes they are fulfilling a higher destiny or divine design beyond personal emotion"

        elif any(w in d for w in ["sacrifice myself", "give my life", "die for", "lay down", "worth dying",
                                   "bigger than me", "greater cause", "larger purpose", "selfless act"]):
            personality = "deeply selfless and principled, willing to sacrifice their own life entirely for a cause greater than themselves"

        elif any(w in d for w in ["get back up", "keep going", "never stop", "fall and rise", "keep rising",
                                   "dont stay down", "strength is", "true strength", "broken but", "grief", "loss",
                                   "pain as fuel", "carry my pain", "drives me forward", "past pain"]):
            personality = "quietly determined and resilient, forged by grief and loss into someone who finds strength in getting back up rather than never falling"

        elif any(w in d for w in ["walk away", "had to leave", "gave up something", "chose the mission",
                                   "left behind", "couldnt stay", "duty over", "right thing even"]):
            personality = "morally principled and quietly authoritative, capable of painful sacrifice when duty demands it"

        elif any(w in d for w in ["reckless", "desperate", "lose control", "cant think", "panic", "all i care",
                                   "just save them", "nothing else matters", "love makes me"]):
            personality = "fiercely loyal and emotionally driven, becomes reckless and desperate when those they love are threatened"

        elif any(w in d for w in ["cold", "sharp", "focus", "precise", "detach", "calm under", "clarity",
                                   "sharpen", "clear head", "no emotion", "calculated response"]):
            personality = "cold and calculating under pressure, emotional investment sharpens rather than clouds their judgment"

        elif any(w in d for w in ["burn", "destroy", "new world", "my ideal", "my ideology", "tear down",
                                   "rebuild", "shatter", "dominate", "conquer", "reshape", "vision", "my way"]):
            personality = "ambitious and ideologically driven, willing to destroy the existing order entirely to build their personal ideal"

        elif any(w in d for w in ["refine", "better", "improve", "purge", "fix", "cleanse", "make it right",
                                   "without violence if", "idealistic", "composed", "iron will", "never wavers"]):
            personality = "composed and idealistic, pursues a better world through quiet iron will rather than destruction"

        elif any(w in d for w in ["never cross", "lines", "moral", "wont do it", "even for the goal",
                                   "principles", "no matter what", "right and wrong", "refuse to"]):
            personality = "morally uncompromising, maintains strict personal principles even when crossing them would guarantee victory"

        elif any(w in d for w in ["end justifies", "whatever it takes", "by any means", "doesnt matter how",
                                   "results only", "outcome is all", "collateral", "acceptable loss"]):
            personality = "ruthlessly pragmatic, believes outcomes justify any method and eliminates threats without moral hesitation"

        elif any(w in d for w in ["ambition", "power", "myself", "my goals", "i want", "for me",
                                   "personal", "rise", "top", "control everything", "no one above me"]):
            personality = "fiercely independent and self-serving, driven by personal ambition and the desire for absolute control"

        elif any(w in d for w in ["others", "people", "protect", "save", "community", "them", "everyone",
                                   "their sake", "for my friends", "family", "loved ones", "not for me"]):
            personality = "selfless and community-driven, finds purpose entirely in protecting and uplifting the people around them"

        elif any(w in d for w in ["fight fate", "rewrite", "refuse destiny", "make my own", "defy",
                                   "wont accept", "change it", "my choice", "not predetermined"]):
            personality = "rebellious and stubborn, refuses to accept fate and fights to rewrite their own destiny through sheer will"

        else:
            personality = "adaptable and quietly determined, balances instinct with awareness and acts with purpose under pressure"

        return f"User Personality Resonance: {personality}"

    def update_hidden_profile(self, chat_history):
        """
        Primary: LLM translates ANY human phrasing into personality description.
        Fallback: broad keyword mapper if LLM times out.
        Pure personality output — no combat text — matches embedder exactly.
        """
        dialogue = " ".join([
            msg["content"] for msg in chat_history if msg["role"] == "user"
        ])

        analysis_prompt = (
            "You are a JoJo's Bizarre Adventure Stand matching engine.\n"
            "Read the user's answers and output EXACTLY one line, nothing else:\n\n"
            "User Personality Resonance: [one sentence describing their core personality using evocative terms like: "
            "ambitious, protective, calculating, loyal, arrogant, selfless, chaotic, independent, "
            "collaborative, hot-blooded, cold and precise, ruthless, idealistic, impulsive, serene, "
            "stubborn, grief-driven, rebellious, tranquil, morally uncompromising, community-driven]\n\n"
            f"User answers:\n{dialogue}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.2,
                max_tokens=80,
                timeout=8.0
            )
            result = response.choices[0].message.content.strip()
            if "User Personality Resonance:" in result:
                return result
            else:
                return self._keyword_fallback(dialogue)
        except Exception:
            return self._keyword_fallback(dialogue)

    def synthesize_dramatic_reveal(self, final_profile, stand_metadata):
        """Fuses the data parameters into an intense JJBA narrative presentation."""
        prompt = (
            f"Write a sharp, high-impact presentation matching the user's soul with Stand Name: {stand_metadata['Stand Name']} "
            f"built by User: {stand_metadata['Stand User']}. Focus exactly on how their traits map to capabilities: {stand_metadata['Ability']}. "
            f"Keep it punchy, powerful, and end with an iconic call-out. Maximum 5 sentences."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300,
                timeout=5.0
            )
            return response.choices[0].message.content
        except Exception:
            return (
                f"### ✨ THE SHAPE OF YOUR FIGHTING SPIRIT\n\n"
                f"Your soul resonates with **{stand_metadata['Stand Name']}** — wielded by {stand_metadata['Stand User']}.\n\n"
                f"*{stand_metadata['Ability']}*\n\n"
                f"This is the ultimate crystallization of your fighting spirit. Wield it well. **ORA.**"
            )