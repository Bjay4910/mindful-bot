Great questions! Let me address the animations point first:

---

**Animations don't require Next.js.** The YouTube video used Next.js probably because it's popular for modern web apps. But animations can be done beautifully with:

```
Plain HTML/CSS → CSS animations, transitions
JavaScript     → Vanilla JS animations
GSAP library   → Professional animations (free)
AOS library    → Animate On Scroll (free)
```

**We'll use AOS + CSS animations** — gives us everything we need without the complexity of Next.js.

---

**Now here's your complete CLAUDE.md file:**

---

```markdown
# mindful-bot — CLAUDE.md

## Project Overview
mindful-bot is a cognitive offload resistance 
chatbot. It challenges users to think and recall 
before revealing answers. Built as a full-stack 
web application for an Intelligent Systems course.

---

## Core Philosophy
- Never show answers immediately
- Always prompt user to think first
- Reward active recall with points
- Track progress honestly

---

## Tech Stack
- Frontend: Plain HTML, CSS, JavaScript
- Animations: AOS (Animate On Scroll) + CSS
- Backend: Python Flask
- Database: Supabase (PostgreSQL)
- AI: Claude API (claude-sonnet-4-6)
- Auth: Supabase Auth

---

## Project Structure
```
mindful-bot/
├── frontend/
│   ├── index.html          # Landing/Home page
│   ├── chat.html           # Main chat page
│   ├── dashboard.html      # User dashboard
│   ├── leaderboard.html    # Leaderboard page
│   ├── features.html       # Features page
│   ├── about.html          # About page
│   ├── privacy.html        # Privacy policy
│   ├── terms.html          # Terms of service
│   ├── contact.html        # Contact page
│   ├── css/
│   │   ├── notion.css      # Notion design system
│   │   ├── animations.css  # AOS + custom animations
│   │   └── main.css        # Global styles
│   └── js/
│       ├── main.js         # Global JS
│       ├── chat.js         # Chat functionality
│       ├── dashboard.js    # Dashboard data
│       └── leaderboard.js  # Leaderboard data
├── backend/
│   ├── app.py              # Flask entry point
│   ├── agents/
│   │   ├── chatbot.py      # Main chatbot agent
│   │   ├── challenger.py   # Recall challenge agent
│   │   └── evaluator.py    # Answer evaluator agent
│   ├── routes/
│   │   ├── chat.py         # Chat API routes
│   │   ├── scores.py       # Score API routes
│   │   └── users.py        # User API routes
│   └── database/
│       └── supabase.py     # Supabase connection
├── .env                    # Secret keys (never share)
├── .gitignore              # Hides .env from GitHub
├── requirements.txt        # Python dependencies
└── CLAUDE.md               # This file
```

---

## The Three AI Agents

### Agent 1 — Main Chatbot
- Handles normal conversation
- Uses Socratic method
- Never gives direct answers immediately
- Always prompts recall first
- System prompt: warm, intellectual, challenging

### Agent 2 — Recall Challenge Generator
- Triggers after every 2-3 exchanges
- Generates a specific recall question
- Based on the current conversation topic
- Returns structured JSON with question + answer

### Agent 3 — Evaluator Agent
- Scores user's recall answers
- Scale: 0-10 points
- Neither too strict nor too generous
- Gives constructive feedback
- Returns JSON: score, feedback, correct_answer

---

## Supabase Tables

### users
```
id          uuid primary key
username    text
email       text
created_at  timestamp
```

### sessions
```
id          uuid primary key
user_id     uuid references users
topic       text
started_at  timestamp
```

### messages
```
id          uuid primary key
session_id  uuid references sessions
role        text (user/assistant)
content     text
created_at  timestamp
```

### challenges
```
id            uuid primary key
session_id    uuid references sessions
question      text
user_answer   text
correct       boolean
score         integer
created_at    timestamp
```

### scores
```
id            uuid primary key
user_id       uuid references users
total_points  integer
streak        integer
updated_at    timestamp
```

---

## API Routes

### Chat
- POST /api/chat → send message, get response
- GET /api/chat/history → get chat history

### Challenges
- POST /api/challenge → generate recall challenge
- POST /api/challenge/evaluate → evaluate answer

### Scores
- GET /api/scores/:user_id → get user score
- POST /api/scores/update → update score

### Users
- POST /api/users/register → create account
- POST /api/users/login → login
- GET /api/users/:id → get user profile

---

## Design System
- Based on Notion design system
- Primary color: #0075de (Notion Blue)
- Background: #ffffff and #f6f5f4
- Text: rgba(0,0,0,0.95)
- Secondary text: #615d59
- Borders: 1px solid rgba(0,0,0,0.1)
- Font: Inter
- Radius: 4px buttons, 12px cards

## Animations (AOS Library)
- Page load: fade-up on hero sections
- Cards: fade-up with stagger delay
- Sidebar items: fade-right
- Chat bubbles: fade-in on appearance
- Score updates: pulse animation
- Challenge card: slide-up

---

## Development Rules

### Rule 1: Always read first
Before taking any action always read:
- CLAUDE.md
- project_specs.md

### Rule 2: Never use dummy data
- All data comes from Supabase
- All AI responses come from Claude API
- No hardcoded fake responses

### Rule 3: One file, one job
- Each file does one specific thing
- Keep files under 200 lines where possible
- Split logic into separate modules

### Rule 4: Environment variables
- Never hardcode API keys
- Always use .env file
- Always check .gitignore includes .env

### Rule 5: Error handling
- Every API call must have try/catch
- Always return proper error messages
- Never expose API keys in error messages

---

## Environment Variables needed
```
CLAUDE_API_KEY=sk-ant-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
FLASK_SECRET_KEY=your-random-secret-key
FLASK_ENV=development
```

---

## Running the project
```
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend
Open index.html in browser
Or use Live Server in VSCode
```

---

## Important Notes
- Contact: gyampoh.b.james@gmail.com
- The hardest part is prompt engineering 
  the three agents correctly
```

---

