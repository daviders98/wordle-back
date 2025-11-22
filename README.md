# 🧩 Better Wordle Backend & Serverless function
This is the backend service for Better Wordle, a daily word guessing game inspired by Wordle.
Built with Django + Django REST Framework, it powers validation, daily solutions, and secure API access for the frontend. Includes my own encrypted collection of possible word solutions.
Hosted on Render 🌐

---
## 🚀 Tech Stack
- Python 3.12+
- Django 5
- Django REST Framework
- Supabase (for word storage)
- JWT Authentication
- Render (deployment)
- Encrypted Word Generator (2000 5 letter-words database)

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
JWT_SECRET=your_jwt_secret
JWT_EXP_DELTA_SECONDS=3600
ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_CORS_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
DICTIONARY_API="https://your-dictionary-api-url.com/"
CRON_SECRET=your_cron_secret
WORDLE_AES_KEY="your_32_character_key"
WORDLE_AES_IV="your_16_character_key"
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
Combined validation + letter scoring (using external dictionary API).
Uses your **Supabase table** to compare answer and guess.
```json
{ "guess": "APPLE" }
```

Response:
```json
{ "valid": true, "letters": [2, 1, 0, 0, 2] }
```

Legend:
- 0 → letter not in word  
- 1 → letter in word but wrong position  
- 2 → correct letter and position

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
Simple uptime check used by Render.

---
## 🔐 Security Features
- CSRF & CORS protection
- HTTPS + HSTS
- Secure cookies
- JWT-based authentication
- Rate limiting

---
## 🧱 Folder Structure
```text
wordle_back/
├── manage.py
├── wordle_back/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── server/
   ├── views.py
   ├── decorators.py
   └── ...
```

---
## 🧩 Deployment (Render)
Render automatically detects Django and runs migrations.

Environment variables required:
| Key | Value |
| --- | --- |
| SECRET_KEY | your-secret |
| SUPABASE_URL | https://yourproject.supabase.co |
| SUPABASE_KEY | your key |
| JWT_SECRET | your jwt secret |
| ALLOWED_HOSTS | yourapp.onrender.com |
| ALLOWED_CORS_ORIGINS | https://yourfrontend.app |
| CSRF_TRUSTED_ORIGINS | https://yourfrontend.app |
| DEBUG | False |

---
⚙️ Automated Word Generator (Serverless Function)
**Control** the word generator.
The generator API pulls from your private 2000-word list instead of any external dictionary.
You need to encrypt the data so people cannot reverse engineer the possible answer.

Runs daily at 22:00 UTC.

---
## 🧩 Overview
- api/generate_word.py → generates tomorrow's word
- api/trigger_generate_word.py → secure scheduled entry point
- vercel.json → defines CRON schedule + config

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

---
## 🧱 Architecture
```
(Vercel CRON)
↓
/api/trigger_generate_word.py
↓ (secure header: x-cron-secret)
/api/generate_word.py
↓
Supabase → inserts tomorrow's word
```

---
## 🔐 Environment Variables (Vercel)
| Key | Description |
| --- | --- |
| SUPABASE_URL | Supabase REST endpoint |
| SUPABASE_KEY | Supabase service key |
| CRON_SECRET | secret key |
| GENERATE_WORD_URL | main function endpoint |

---
## 🔄 Flow Explanation
1️⃣ Vercel CRON hits trigger  
2️⃣ Trigger sends secure request  
3️⃣ Generator validates secret  
4️⃣ Reads last word  
5️⃣ Computes next word date  
6️⃣ Fetches a word from your 2000-word API  
7️⃣ Inserts into Supabase  

---
## 🧩 Integration Notes
- Django backend fetches today’s word from Supabase
- Vercel generator inserts tomorrow’s word
- Both fully independent

---
## 🧠 Future Improvements
- Add retry logic  
- Logging / monitoring  
- Slack/Discord notifications  

---
© 2025 DevGarcia – Better Wordle Project