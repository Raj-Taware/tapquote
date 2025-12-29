# TapQuote - AI Quote Generator

AI-powered electrical quote generation platform.

## Quick Start (Local Development)

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Deploy to Railway

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/tapquote.git
git push -u origin main
```

### 2. Deploy Backend
1. Go to [railway.app](https://railway.app) → New Project
2. Deploy from GitHub → Select your repo
3. Set root directory: `backend`
4. Add environment variable: `OPENAI_API_KEY=your_key`
5. Deploy

### 3. Deploy Frontend
1. Add new service in same project
2. Deploy from GitHub → Same repo
3. Set root directory: `frontend`
4. Add environment variable: `VITE_API_URL=https://your-backend-url.railway.app`
5. Deploy

## Tech Stack
- **Backend**: FastAPI + LangChain + ReportLab
- **Frontend**: React + Vite + Tailwind CSS
- **AI**: OpenAI GPT-3.5-turbo
