# 🧩 Better Wordle Backend & Serverless function
This is the backend service for Better Wordle, a daily word guessing game inspired by Wordle.
Built with Django + Django REST Framework, it powers validation, daily solutions, and secure API access for the frontend.
Hosted on Render 🌐

---
## 🚀 Tech Stack
- Python 3.12+
- Django 5
- Django REST Framework
- Supabase (for word storage)
- JWT Authentication
- Render (deployment)
- Dictionary API (for word validation)
---
## ⚙️ Setup & Local Development
### 1️⃣ Clone the repository
```bash
git clone https://github.com/daviders98/wordle-front.git
cd wordle-back
```
### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate # macOS/Linux
venv\Scripts\activate # Windows
```
### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Create a .env file
```bash
SECRET_KEY=your_secret_key
DEBUG=True
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_KEY=your_supabase_key
DICTIONARY_API=https://api.dictionaryapi.dev/api/v2/entries/en/
JWT_SECRET=your_jwt_secret
JWT_EXP_DELTA_SECONDS=3600
ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_CORS_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
```
### 5️⃣ Run the server
```bash
python manage.py runserver
```
Server runs on:
http://127.0.0.1:8000
---
## 🧠 API Endpoints
All protected endpoints require a JWT token in the Authorization header:
```bash
Authorization: Bearer <your_token>
```
🔑 POST /api/get-jwt/
Generates a new JWT for authenticated API calls.
```json
{ "token": "eyJhbGciOi..." }
```
🧩 POST /api/guess/
Checks if the submitted guess matches the current day’s word.
```json
{ "guess": "APPLE" }
```
Response:
```json
{ "letters": [2, 1, 0, 0, 2] }
```
Legend:
- 0 → letter not in word
- 1 → letter in word but wrong position
- 2 → correct letter and position
✅ POST /api/validate/
Validates if a given word exists (in Supabase or Dictionary API).
```json
{ "word": "STEAM" }
```
Response:
```json
{ "valid": true }
```
🔗 POST /api/combined-guess/
Validates and checks the guess in a single call.
```json
{ "guess": "APPLE" }
```
Invalid Response:
```json
{ "valid": false }
```
Valid Response:
```json
{ "valid": true, "letters": [2, 0, 0, 1, 2] }
```
📜 GET /api/list/
Returns all past words (before today).
```json
[
{
"solution": "APPLE",
"solution_date": "2025-11-02",
"solution_number": 317
},
{
"solution": "MOUSE",
"solution_date": "2025-11-03",
"solution_number": 318
}
]
```
❤️ GET /api/health/
Simple uptime check used by Render for health monitoring.
```json
{ "status": "ok" }
```
---
## 🔐 Security Features
- CSRF & CORS protection via environment configuration
- HTTPS enforced with HSTS (SECURE_HSTS_SECONDS, etc.)
- Secure cookies (CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE)
- Clickjacking & referrer protection
- JWT-based stateless authentication
---
## 🧱 Folder Structure
```text
wordle_back/
├── manage.py
├── wordle_back/
│ ├── settings.py
│ ├── urls.py
│ ├── wsgi.py
│ └── asgi.py
└── server/
├── views.py
├── decorators.py
└── ...
```
---
## 🧩 Deployment (Render)
Render automatically detects Django and runs migrations.
Be sure to add these environment variables in Render Dashboard → Environment:
| Key | Value |
| --- | --- |
| SECRET_KEY | your-secret |
| SUPABASE_URL | https://yourproject.supabase.co
 |
| SUPABASE_KEY | your key |
| JWT_SECRET | your jwt secret |
| ALLOWED_HOSTS | yourapp.onrender.com |
| ALLOWED_CORS_ORIGINS | https://yourfrontend.app
 |
| CSRF_TRUSTED_ORIGINS | https://yourfrontend.app
 |
| DEBUG | False |
---
# ⚙️ Automated Word Generator (Serverless Function)
This module is deployed on Vercel and is responsible for automatically generating and inserting a new daily Wordle solution into Supabase.
It runs every day at 22:00 UTC (configurable in vercel.json), triggered by Vercel’s CRON scheduler.
---
## 🧩 Overview
The serverless setup consists of:
- api/generate_word.py → the main function that interacts with Supabase
- api/trigger_generate_word.py → a secure wrapper that calls the main function with a secret token
- vercel.json → defines CRON schedule and runtime limits
---
## 🕒 Schedule Configuration (vercel.json)
```json
{
"crons": [
{
"path": "/api/trigger_generate_word",
"schedule": "0 22 * * *"
}
],
"functions": {
"api/generate_word.py": {
"maxDuration": 10,
"memory": 128
}
}
}
```
- The CRON schedule "0 22 * * *" means run every day at 22:00 UTC.
- The memory and duration limits prevent runaway executions.
---
## 🧱 Architecture
```
(Vercel CRON)
↓
/api/trigger_generate_word.py
↓ (sends header x-cron-secret)
/api/generate_word.py
↓
Supabase → inserts next daily word
```
---
## 🔐 Environment Variables
These must be configured in Vercel → Project Settings → Environment Variables:
| Key | Description |
| --- | --- |
| SUPABASE_URL | Supabase project REST endpoint |
| SUPABASE_KEY | Supabase service key |
| WORDS_GENERATOR_URL | API endpoint that provides random words |
| CRON_SECRET | Shared secret used between trigger and generator |
| GENERATE_WORD_URL | URL of the main function (/api/generate_word) |
---
## 🔄 Flow Explanation
1️⃣ Vercel CRON runs /api/trigger_generate_word daily
2️⃣ The trigger adds the x-cron-secret header and calls /api/generate_word
3️⃣ The generate function validates the token
4️⃣ Fetches the last solution from Supabase
5️⃣ Calculates the next date and solution number
6️⃣ Fetches a new word from the external generator
7️⃣ Inserts it into Supabase as tomorrow’s word
---
## 🧩 Integration Notes
- The Django backend reads the current day’s word from Supabase.
- The Vercel function automatically appends tomorrow’s word daily.
- Both share the same Supabase credentials but remain independent.
---
## 🧠 Future Improvements
- Add retry logic for Supabase API timeouts
- Use logging + monitoring (e.g. Sentry)
- Add Slack/Discord notifications on word generation success/failure
---
© 2025 DevGarcia – Better Wordle Project