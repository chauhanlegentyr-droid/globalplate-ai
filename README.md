# 🍲 GlobalPlate AI

GlobalPlate AI is an AI-powered international culinary assistant built using **Google Gemini**, **FastAPI**, and **Docker** as part of the **IBM Gen AI & Cloud Computing Internship Project**.

It helps users explore authentic recipes from around the world with AI-generated cooking instructions, nutrition insights, and interactive features.

---

## 🚀 Features

- 🤖 AI-powered recipe generation using Google Gemini
- 💬 Streaming AI responses
- 🧠 Multi-turn conversation memory
- 🍽️ Dynamic dish images using the Pexels API
- 🥗 Nutrition summary card
- ✅ Interactive ingredient checklist
- 🎤 Voice input (browser supported)
- 📄 Copy, Download & Print recipe
- 🌙 Dark mode
- 📱 Fully responsive UI
- ☁️ Docker-ready FastAPI deployment
- ❤️ Saved conversations using Local Storage

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Google Gemini API
- Pexels API
- HTML
- CSS
- JavaScript
- Docker

---

## 📂 Project Structure

```
GLOBALPLATE-AI/
│
├── templates/
│   └── index.html
├── main.py
├── requirements.txt
├── Dockerfile
├── README.md
├── .env.example
└── .gitignore
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/GlobalPlate-AI.git
cd GlobalPlate-AI
```

Install dependencies:

```bash
py -m pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and add your API keys.

Run the application:

```bash
py -m uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000
```

---

## 📌 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Web Application |
| `/health` | Health Check |
| `/api/info` | Project Information |
| `/docs` | FastAPI Swagger UI |

---

## 🔒 Security

This repository **does not include API keys**.

Create a local `.env` file containing:

```
GEMINI_API_KEY=YOUR_KEY
PEXELS_API_KEY=YOUR_KEY
```

Never upload `.env` to GitHub.

---

## 👨‍💻 Developer

**Nirbhaysingh A. Chauhan**

IBM Gen AI & Cloud Computing Internship Project
