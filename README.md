# GlobalPlate AI

GlobalPlate AI is an AI-powered international culinary assistant created for the IBM Gen AI & Cloud Computing internship project.

## Features

- Live Gemini-powered recipe generation
- Streaming AI responses
- Multi-turn conversation memory
- Saved dish conversations in browser storage
- Dynamic dish images using Pexels
- Nutrition summary card
- Ingredient checklist
- Voice input where supported
- Copy, download and print/PDF tools
- Dark mode and responsive design
- Docker-ready FastAPI deployment
- Health and API information endpoints

## Local setup

1. Copy `.env.example` to `.env`.
2. Add your Gemini and Pexels API keys.
3. Install dependencies:

```bash
py -m pip install -r requirements.txt
```

4. Run:

```bash
py -m uvicorn main:app --reload
```

5. Open `http://127.0.0.1:8000`.

## Useful endpoints

- `/` — web application
- `/health` — deployment health check
- `/api/info` — public project information
- `/docs` — FastAPI documentation

## Security

Never commit `.env` or API keys to GitHub.

## Developer

Developed by **Nirbhaysingh A. Chauhan**.
