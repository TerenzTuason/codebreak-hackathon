# SympAI — Codebreak Hackathon

AI-powered healthcare support system. A Next.js frontend for patients + a Flask API that handles healthcare queries with intent detection and tiered escalation.

---

## Quick Start

**1. Frontend (Next.js)**
```bash
cd frontend
npm install
npm run dev
```
→ Open http://localhost:3000

**2. Backend (Flask API)**
```bash
cd ai-training
pip install -r requirements.txt
python app.py
```
→ API runs at http://localhost:5000

---

## Project Structure

```
Codebreak Hackathon/
├── frontend/                 # Next.js web app
│   ├── src/
│   │   ├── app/              # Pages & routes
│   │   ├── components/       # Reusable UI
│   │   ├── context/          # React context (loading state)
│   │   └── data/             # Static data (users.json)
│   └── public/images/        # Logos, avatars
│
├── ai-training/              # Flask API + AI logic
│   ├── app.py                # Main API (local dev)
│   ├── api/                  # Vercel serverless entry
│   ├── datasets/             # Healthcare data (doctors, policies, etc.)
│   └── config/               # Model & healthcare config
│
└── README.md
```

---

## Directory Guide

### `frontend/` — Web App

| Path | Purpose |
|------|---------|
| `src/app/page.tsx` | Home → redirects to `/login` |
| `src/app/login/page.tsx` | Login (uses `users.json`) |
| `src/app/dashboard/page.tsx` | User dashboard + AI chat button |
| `src/app/chat/page.tsx` | Full-screen AI chat |
| `src/app/health-records/page.tsx` | User health records |
| `src/components/AiChat/` | AI chat button + chat window |
| `src/components/Navbar.tsx` | Navigation bar |
| `src/data/users.json` | Demo users (username/password + health data) |

**Flow:** Login → Dashboard → Chat with AI or view Health Records.

---

### `ai-training/` — Backend API

| Path | Purpose |
|------|---------|
| `app.py` | Flask app for local dev (port 5000) |
| `api/app.py` | Same logic, used by Vercel |
| `api/wsgi.py` | Vercel serverless entry point |
| `datasets/healthcare_support_data.json` | Intents, templates, doctors, policies |
| `.env` | `GOOGLE_GEMINI_API_KEY`, `GEMINI_MODEL` (create this file) |

**Main endpoint:** `POST /predict` with `{ "query": "your question" }`

---

## Setup Details

### Frontend
- **Node.js** 18+
- `cd frontend && npm install && npm run dev`
- Demo login: `john_doe` / `securePassword123` or `jane_smith` / `strongPass456`

### Backend
- **Python** 3.8+
- Create `ai-training/.env`:
  ```
  GOOGLE_GEMINI_API_KEY=your_key
  GEMINI_MODEL=gemini-pro
  ```
- Run `python app.py` (or deploy to Vercel via `vercel.json`)

### Local API vs Production
- **Local:** Frontend calls `https://ai-training-kappa.vercel.app/predict` (deployed API)
- **Local backend:** Edit `AiChatWindow.tsx` and `chat/page.tsx` to use `http://localhost:5000/predict` instead

---

## How the AI Works

1. User sends a message → `POST /predict`
2. API detects intent (doctor availability, insurance, etc.) via rule-based patterns
3. Response is built from `healthcare_support_data.json` templates
4. Optional: Gemini enhances the reply
5. Tier 0 = AI answers; Tier 1–4 = escalate to human/specialist

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14, React, Tailwind, Framer Motion |
| Backend | Flask, Flask-RESTful, Flask-CORS |
| AI | Google Gemini (optional), rule-based intent detection |
