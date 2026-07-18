import os
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Setting up templates directory to read our HTML user interface
templates = Jinja2Templates(directory="templates")

# Pull the Google AI Studio API key securely from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = f"https://googleapis.com{GEMINI_API_KEY}"

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/cook")
async def culinary_stream(request: Request):
    body = await request.json()
    user_dish = body.get("message", "")

    # The System Prompt forces the AI to strictly stay in character as GlobalPlate
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"You are GlobalPlate, an elite international chef and cultural culinary historian. "
                    f"The user wants to explore this dish or ingredient: '{user_dish}'. "
                    f"Provide your response in exactly this structure:\n"
                    f"1. 🌍 CULTURAL PROFILE: Explain where this dish originates and its cultural significance.\n"
                    f"2. 📝 THE TRADITIONAL RECIPE: List exact ingredients (provide dual units: metric and imperial).\n"
                    f"3. 🍳 STEP-BY-STEP COOKING GUIDE: Stream clear, chronological instructions.\n"
                    f"4. 💡 CULINARY TRICK: Share one authentic insider secret to making this dish taste genuinely traditional."
                )
            }]
        }]
    }

    async def event_generator():
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", GEMINI_URL, json=payload, timeout=60.0) as response:
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    clean_line = line.strip()

                    # Clean up trailing braces/brackets from the raw chunks
                    if clean_line.startswith("[") or clean_line.startswith(","):
                        clean_line = clean_line[1:]
                    if clean_line.endswith("]") or clean_line.endswith(","):
                        clean_line = clean_line[:-1]

                    try:
                        chunk_data = json.loads(clean_line)
                        text_chunk = chunk_data["candidates"][0]["content"]["parts"][0]["text"]
                        yield f"data: {json.dumps({'text': text_chunk})}\n\n"
                    except Exception:
                        pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")
