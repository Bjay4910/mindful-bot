# mindful-bot

A cognitive offload resistance chatbot that challenges users to think and recall before receiving answers. Built as a full-stack web application for an Intelligent Systems course.

---

## Overview

mindful-bot uses the Socratic method to resist cognitive offloading — the tendency to outsource thinking to AI. Instead of giving direct answers, it prompts users to reason first, then tests retention with recall challenges, and rewards active engagement with points.

---

## Features

- **Socratic chatbot** — never gives direct answers; guides users to think through problems
- **Recall challenges** — automatically generated every 3 exchanges, based on the conversation
- **AI-powered evaluation** — answers are scored 0–10 with constructive feedback
- **Points and streaks** — gamified progress tracking stored per user
- **Leaderboard** — ranked by total points across all users
- **Authentication** — secure login and registration via Supabase Auth
- **Session history** — conversations are persisted and retrievable

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Animations | AOS (Animate On Scroll) + CSS transitions |
| Backend | Python, Flask |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth |
| AI | Claude API (`claude-sonnet-4-6`) |

---

## Project Structure

```
mindful-bot/
├── frontend/
│   ├── index.html           # Landing page
│   ├── chat.html            # Main chat interface
│   ├── dashboard.html       # User dashboard
│   ├── leaderboard.html     # Global leaderboard
│   ├── features.html
│   ├── about.html
│   ├── privacy.html
│   ├── terms.html
│   ├── contact.html
│   ├── css/
│   │   ├── main.css         # Global styles + Notion design system
│   │   └── animations.css   # AOS + custom animations
│   └── js/
│       ├── config.js        # API base URL + Supabase public keys
│       ├── main.js          # Auth, apiFetch helper, toast notifications
│       ├── chat.js          # Chat flow + recall challenge UI
│       ├── dashboard.js     # Dashboard data loading
│       └── leaderboard.js   # Leaderboard rendering
├── backend/
│   ├── app.py               # Flask entry point (port 5001)
│   ├── agents/
│   │   ├── chatbot.py       # Socratic chatbot agent
│   │   ├── challenger.py    # Recall challenge generator
│   │   └── evaluator.py     # Answer evaluator (scores 0–10)
│   ├── routes/
│   │   ├── chat.py          # /chat, /challenge, /challenge/evaluate
│   │   ├── scores.py        # /scores/<user_id>, /leaderboard
│   │   └── users.py         # /users/register, /users/login
│   └── database/
│       └── supabase.py      # Supabase client + auth token verification
├── supabase_schema.sql      # Full database schema + RLS policies
├── requirements.txt
├── .env                     # Secret keys (never commit)
├── .gitignore
└── README.md
```

---

## The Three AI Agents

### Agent 1 — Socratic Chatbot
Handles conversation using the Socratic method. Never gives direct answers immediately — always prompts the user to reason first. Uses the last 20 messages as context.

### Agent 2 — Recall Challenge Generator
Triggers after every 3 user exchanges. Generates a targeted recall question based on the conversation, with a hint and a model answer. Returns structured JSON.

### Agent 3 — Evaluator
Scores the user's answer on a 0–10 scale. Provides specific feedback and the correct answer. A score of 7 or above counts as correct and extends the user's streak.

---

## Database Schema

| Table | Key Columns |
|---|---|
| `users` | `id`, `username`, `email`, `created_at` |
| `sessions` | `id`, `user_id`, `topic`, `started_at` |
| `messages` | `id`, `session_id`, `role`, `content`, `created_at` |
| `challenges` | `id`, `session_id`, `question`, `user_answer`, `correct_answer`, `correct`, `score` |
| `scores` | `id`, `user_id`, `total_points`, `streak`, `challenges_completed`, `updated_at` |
| `leaderboard` | View: `username`, `total_points`, `streak`, `rank` |

Row Level Security (RLS) is enabled on all tables. Users can only read and write their own data.

---

## API Routes

| Method | Route | Description |
|---|---|---|
| POST | `/api/chat` | Send a message, get a Socratic response |
| GET | `/api/chat/history` | Fetch session message history |
| POST | `/api/challenge` | Generate a recall challenge |
| POST | `/api/challenge/evaluate` | Evaluate a user's answer |
| GET | `/api/scores/<user_id>` | Get a user's points, streak, and rank |
| GET | `/api/leaderboard` | Get top 20 users |
| POST | `/api/users/register` | Create a new account |
| POST | `/api/users/login` | Log in |

All routes except register and login require a `Authorization: Bearer <token>` header.

---

## Setup

### Prerequisites

- Python 3.10+
- A [Supabase](https://supabase.com) project with the schema applied
- An [Anthropic](https://console.anthropic.com) API key

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mindful-bot.git
cd mindful-bot
```

### 2. Configure environment variables

Create a `.env` file in the root directory:

```env
CLAUDE_API_KEY=sk-ant-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
FLASK_SECRET_KEY=a-random-secret-string
FLASK_ENV=development
```

### 3. Set up the database

Open the Supabase SQL editor and run the full contents of `supabase_schema.sql`.

### 4. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the backend

```bash
python -m backend.app
```

The API will be available at `http://localhost:5001`.

### 6. Open the frontend

Open `frontend/index.html` in a browser, or use the **Live Server** extension in VS Code (serves on port 5500).

---

## Design System

Inspired by Notion's UI. Key tokens:

| Token | Value |
|---|---|
| Primary | `#0075de` |
| Background | `#ffffff` / `#f6f5f4` |
| Text | `rgba(0,0,0,0.95)` |
| Secondary text | `#615d59` |
| Border | `1px solid rgba(0,0,0,0.1)` |
| Font | Inter |
| Button radius | `4px` |
| Card radius | `12px` |

---

## Environment Variables

| Variable | Description |
|---|---|
| `CLAUDE_API_KEY` | Anthropic API key |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public key |
| `FLASK_SECRET_KEY` | Flask session secret |
| `FLASK_ENV` | `development` or `production` |

---

## License

MIT

---

Built for the Intelligent Systems course — JRSEM2.
