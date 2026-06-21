# AI Chatbot Upgrade — Setup & What Changed

This replaces the old chatbot (a single Hugging Face `flan-t5-base` call with
no real knowledge of the site) with a context-aware LangChain agent that
looks up real activities, prices, availability, weather, your bookings, and
FAQ answers before replying.

## 1. Get a free LLM API key (2 minutes, no credit card)

1. Go to **https://openrouter.ai/keys** and sign up.
2. Create a new API key.
3. Open `.env` in the project root and paste it in:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
   ```
4. (Optional) Pin a specific free model instead of the auto-router:
   ```
   OPENROUTER_MODEL=deepseek/deepseek-chat-v3.1:free
   ```
   Check **openrouter.ai/models** filtered by `Price: Free` for whatever's
   currently live — free model availability rotates over time. Leaving it as
   `openrouter/free` (the default) auto-picks a live free model for you, so
   you don't have to babysit this.

## 2. Install the new dependencies

```bash
pip install -r app/requirement.txt
```

This pulls in `langchain`, `langchain-openai`, `langchain-community`,
`langchain-huggingface`, `faiss-cpu`, and `sentence-transformers`. The last
one downloads a small (~90MB) local embedding model on first run — this is
what powers FAQ semantic search, and it's free/local, no API key needed for
it. It also pulls in PyTorch as a dependency, so the install is a few
hundred MB larger than before; that's expected.

## 3. Run it

```bash
python run.py
```

Open the site, click **"Chat with us"** in the bottom-right corner on any
page, and ask something like:
- "Is paragliding available next Saturday?"
- "How much does bungee jumping cost?"
- "What's the weather like in Pokhara?"
- "What's the status of my booking?" (only works if you're logged in)
- "How do I cancel a booking?"

## What actually changed

**Backend (new):**
- `app/chatbot/tools.py` — 6 tools: activity search, price lookup,
  availability lookup, weather lookup (free, no key, via Open-Meteo), your
  own booking lookup (session-scoped — the AI can never look up another
  user's bookings), and FAQ semantic search.
- `app/chatbot/faiss_store.py` — builds/caches a FAISS vector index over the
  FAQ content using free local embeddings.
- `app/chatbot/faq_data.py` — the FAQ knowledge base (edit this file to add
  more Q&A — no code changes needed elsewhere, the index rebuilds itself).
- `app/chatbot/agent.py` — wires the LLM (via OpenRouter) + tools into a
  LangChain agent.
- `app/routes/chatbot.py` — the `/chat` endpoint now calls the agent instead
  of the old Hugging Face call. Same request/response shape as before, so
  nothing else needed to change. The old file is kept as
  `app/routes/chatbot_OLD_huggingface.py.bak` for reference/comparison —
  safe to delete once you're happy with the new one.

**Frontend (bug fix + upgrade):**
- The chat widget was actually **broken before this change** — its
  `toggleChatbot()`/`sendChatbotMessage()` functions were referenced in
  `home.html` but never defined anywhere, and a stray `return` statement
  outside any function was silently breaking the *entire* script block on
  the homepage (including the wishlist heart-icon toggle). Both are fixed.
- The widget now lives in `base.html` instead of only `home.html`, so
  **"Chat with us" appears on every page**, not just the homepage.
- New `app/static/css/chatbot.css` and `app/static/js/chatbot.js` — a real,
  working implementation with a typing indicator and proper message bubbles
  that match your existing theme colors (light/dark mode both supported).

## Notes / honest limitations

- The free OpenRouter tier has a rate limit (~20 requests/minute as of
  writing) — fine for a class project demo, not for high-traffic production.
- `search_faq` quality depends entirely on what's in `faq_data.py`. Add more
  entries there as you think of real questions users will ask.
- This piece is self-contained and doesn't touch the dashboard, admin panel,
  or payment system — those need the `ThrillDash_AdminFix` reference
  codebase, which wasn't provided yet.
