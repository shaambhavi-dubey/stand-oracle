# 🔮 JJBA Stand Oracle

A RAG-powered personality matching app that figures out which JoJo's Bizarre Adventure Stand reflects your soul — built with FAISS, SentenceTransformers, and a touch of the Stand Arrow's energy.

---

## What It Does

The Oracle asks you 6 questions across four dimensions — combat instinct, ideology, emotional response, and philosophy. Your answers get translated into a personality profile, which is then matched against 20 Stands from Parts 3–7 using vector similarity search. No gimmicks, actual semantic matching.

The result: your Stand, your user, your stats, and a dramatic reveal worthy of a Part finale.

---

## How It Actually Works (The RAG Pipeline)

This isn't a quiz with hardcoded outcomes. Here's the real pipeline:

```
Your 6 answers
      ↓
LLM translates freeform human text → structured personality description
      ↓
SentenceTransformer (all-MiniLM-L6-v2) converts it → 384-dimensional vector
      ↓
FAISS cosine similarity search → finds closest Stand personality vector
      ↓
Stand metadata returned → dramatic reveal generated
```

The LLM's only job is translation — it converts whatever you say into personality language that FAISS can work with. The actual matching is done entirely by the vector search. That's what makes it RAG: **R**etrieval (FAISS) **A**ugmented **G**eneration (reveal text).

---

## Tech Stack

- **Streamlit** — frontend and session management
- **FAISS** — vector similarity search for Stand matching
- **SentenceTransformers** — `all-MiniLM-L6-v2` for generating 384-dim embeddings
- **OpenRouter API** — LLM access (Llama 3.3 70B) for profile translation and reveal generation
- **pandas + openpyxl** — Stand database ingestion from Excel
- **matplotlib** — radar chart for Stand stats

---

## Project Structure

```
stand-oracle/
├── core/
│   ├── embedder.py       # Builds FAISS index from stands.xlsx
│   ├── engine.py         # Questions, profile generation, reveal synthesis
│   ├── retriever.py      # FAISS query logic
│   └── visualizer.py     # Radar chart generator
├── data/
│   ├── stands.xlsx       # Stand database (Name, User, Ability, Personality, Stats)
│   └── user_images/      # Stand user images (optional, named first_last.jpeg)
├── main.py               # Streamlit app entrypoint
├── requirements.txt
└── .env                  # Local only — never commit this
```

---

## Local Setup

```bash
# Clone and enter
git clone https://github.com/yourusername/stand-oracle.git
cd stand-oracle

# Create and activate virtual environment
python -m venv jjenv
jjenv\Scripts\activate        # Windows
source jjenv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your OpenRouter API key
echo OPENROUTER_API_KEY=your-key-here > .env

# Build the FAISS index
python core/embedder.py

# Run the app
streamlit run main.py
```

---

## Deployment (Streamlit Community Cloud)

1. Push your repo to GitHub — make sure `.env`, `jjenv/`, `*.index`, and `*.pkl` are in `.gitignore`
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set main file to `main.py`
4. Go to **Settings → Secrets** and add:
```toml
OPENROUTER_API_KEY = "your-key-here"
```
5. Deploy — the FAISS index builds automatically on first run

The `all-MiniLM-L6-v2` model downloads on first deploy (~1-2 min). Subsequent loads are cached.

---

## A Note on the Matching Algorithm

Getting this right took some work. The first version of the pipeline was returning the same Stand regardless of what anyone answered — here's why and how it was fixed.

**The problem:** The LLM profile call was hitting OpenRouter's free tier rate limit on almost every request and silently falling back to a hardcoded generic description. Every user got the same fallback text → same FAISS vector → same Stand. The error was invisible because the `except` block just returned the fallback without any indication it had failed.

**The second problem:** Even when the profile varied, the FAISS index was built with both `Ability` and `User Personality` columns embedded together. Since many Stands share similar combat descriptions (close-range powerhouse, high speed, physical strength), the combat text was dominating the vector and pulling unrelated Stands together.

**The fix:** Two changes — the index was rebuilt using **only** the `User Personality` column, since each Stand's user has a genuinely distinct personality that maps much better to how people answer open-ended questions. The LLM call was also made minimal (80 tokens, single line output) to survive rate limits, with a broad keyword fallback covering natural language patterns that people actually use rather than the expected quiz-style answers.

The questions were also redesigned from 4 combat-focused prompts to 6 questions across combat, ideology, emotional response, and philosophy — because Stands like Gold Experience, Tusk, and Made in Heaven are defined by their users' grief, conviction, and worldview, not their fighting style.

---

## Stand Database

20 Stands across Parts 3–7:

| Stand | User | Part |
|---|---|---|
| Star Platinum | Jotaro Kujo | 3 |
| The World | DIO | 3 |
| Crazy Diamond | Josuke Higashikata | 4 |
| The Hand | Okuyasu Nijimura | 4 |
| Killer Queen | Yoshikage Kira | 4 |
| Gold Experience | Giorno Giovanna | 5 |
| King Crimson | Diavolo | 5 |
| Purple Haze | Pannacotta Fugo | 5 |
| Sticky Fingers | Bruno Bucciarati | 5 |
| Sex Pistols | Guido Mista | 5 |
| Notorious B.I.G | Carne | 5 |
| Whitesnake | Enrico Pucci | 6 |
| C-Moon | Enrico Pucci | 6 |
| Made in Heaven | Enrico Pucci | 6 |
| Stone Free | Jolyne Cujoh | 6 |
| Weather Report | Weather Report | 6 |
| Tusk | Johnny Joestar | 7 |
| Tusk ACT4 | Johnny Joestar | 7 |
| Ball Breaker | Gyro Zeppeli | 7 |
| Scary Monsters | Diego Brando | 7 |

---

## Known Limitations

- OpenRouter free tier rate limits can cause the LLM profile call to fall back to keyword matching. The keyword fallback is broad but won't catch every possible phrasing.
- The `synthesize_dramatic_reveal` LLM call can also time out — the fallback text is used in that case, which is less dramatic but still accurate.
- User images are not included in the repo. Place `first_last.jpeg` files in `data/user_images/` to enable them.

---

## Credits

Built as a personal ML project exploring RAG pipelines, vector search, and what it means to match a human soul to a fictional fighting spirit.

Stand data sourced from the JoJo's Bizarre Adventure wiki.

*The Arrow does not choose the worthy. It chooses the inevitable.*
