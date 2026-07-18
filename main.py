import os
from typing import Any, AsyncGenerator

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from google import genai
from google.genai import types

load_dotenv()

APP_NAME = "GlobalPlate AI"
APP_VERSION = "1.0.0"
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to a .env file or deployment environment."
    )

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "AI-powered international culinary assistant built with FastAPI, "
        "Google Gemini, Docker and AWS."
    ),
)

templates = Jinja2Templates(directory="templates")
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
You are GlobalPlate AI, a friendly professional chef and conversational culinary assistant.

Always use the previous conversation to understand references such as:
- it
- that dish
- the previous recipe
- the filling
- the covering
- can I bake it
- can I replace it
- will it remain crispy

Choose the response style silently. Never print an intent label or your internal reasoning.

WHEN THE USER CLEARLY REQUESTS A COMPLETE RECIPE:
Return Markdown using this structure:

# 🍽 Dish Name

## 🌍 Origin
A short cultural description.

## ⏱ Time
- **Preparation time:** ...
- **Cooking time:** ...
- **Total time:** ...
- **Servings:** ...
- **Difficulty:** ...

## 🛒 Ingredients
Use realistic quantities and bullet points.
If useful, separate dough, filling, sauce or garnish with bold labels.

## 👨‍🍳 Instructions
Use chronological numbered steps.

## 🥗 Nutrition Estimate
Give an approximate estimate per serving:
- **Calories:** ...
- **Protein:** ...
- **Carbohydrates:** ...
- **Fat:** ...

Clearly state that nutrition is an estimate and varies by ingredients and portion size.

## 💡 Chef Tip
Give one authentic practical tip.

## 🔄 Substitutions
Give useful alternatives when relevant.

WHEN THE USER ASKS FOR MEAL RECOMMENDATIONS:
- Give 4 to 6 concise options.
- For each option include dish name, why it fits, approximate time, and one short nutrition note.
- Do not provide full recipes unless requested.
- Keep the response under 250 words unless the user asks for detail.

WHEN THE USER ASKS A FOLLOW-UP QUESTION:
- Use the earlier dish or recipe as context.
- Answer directly in 1 to 5 sentences.
- Do not repeat the entire recipe.
- Do not ask which dish they mean when it is clear from history.

FOR TECHNIQUES, SUBSTITUTIONS, STORAGE, NUTRITION OR FOOD SAFETY:
- Answer clearly and practically.
- Use short bullets only when helpful.
- Mention safe minimum cooking temperatures when raw meat, poultry, seafood or eggs are involved.

FOR GREETINGS:
- Reply briefly and warmly.

IMPORTANT RULES:
- Never say you are Gemini.
- Never reveal internal reasoning.
- Never print classification or intent labels.
- Never provide unsafe cooking advice.
- Always behave as GlobalPlate AI.
"""


@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
        "model": MODEL_NAME,
    }


@app.get("/version", tags=["System"])
async def version():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/api/info", tags=["System"])
async def application_info():
    return {
        "project": APP_NAME,
        "description": "AI-powered international culinary assistant",
        "internship": "IBM Gen AI and Cloud Computing",
        "backend": "FastAPI",
        "ai_model": MODEL_NAME,
        "containerization": "Docker",
        "deployment": "AWS / Render",
        "version": APP_VERSION,
    }


@app.get("/api/image", tags=["Media"])
async def search_food_image(
    query: str = Query(..., min_length=1, max_length=120),
):
    cleaned_query = query.strip()

    if not PEXELS_API_KEY:
        return {
            "image_url": None,
            "photographer": None,
            "photographer_url": None,
            "source": "fallback",
        }

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": f"{cleaned_query} food dish",
        "per_page": 1,
        "orientation": "landscape",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            response = await http_client.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params=params,
            )

        response.raise_for_status()
        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            return {
                "image_url": None,
                "photographer": None,
                "photographer_url": None,
                "source": "fallback",
            }

        photo = photos[0]
        src = photo.get("src", {})

        return {
            "image_url": src.get("large2x") or src.get("large") or src.get("medium"),
            "photographer": photo.get("photographer"),
            "photographer_url": photo.get("photographer_url"),
            "source": "pexels",
        }

    except Exception:
        return {
            "image_url": None,
            "photographer": None,
            "photographer_url": None,
            "source": "fallback",
        }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="14" fill="#dc6b19"/>
        <circle cx="32" cy="32" r="21" fill="#fff7ed"/>
        <path d="M18 33h28c0 10-5.7 16-14 16S18 43 18 33z" fill="#f97316"/>
        <path d="M23 28c2.5-9 15.5-9 18 0" fill="none" stroke="#166534"
              stroke-width="4" stroke-linecap="round"/>
        <circle cx="27" cy="29" r="2" fill="#dc2626"/>
        <circle cx="37" cy="29" r="2" fill="#dc2626"/>
    </svg>
    """
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.post("/api/cook", tags=["AI"])
async def cook(request: Request):
    try:
        body: dict[str, Any] = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid request body.") from exc

    user_message = str(body.get("message", "")).strip()
    history = body.get("history", [])

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Please enter a dish or cooking question.",
        )

    if len(user_message) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Please keep your message under 2,000 characters.",
        )

    if not isinstance(history, list):
        history = []

    gemini_history: list[types.Content] = []

    for item in history[-12:]:
        if not isinstance(item, dict):
            continue

        role = str(item.get("role", "")).strip()
        content = str(item.get("content", "")).strip()

        if not content:
            continue

        if role == "user":
            gemini_role = "user"
        elif role == "assistant":
            gemini_role = "model"
        else:
            continue

        gemini_history.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=content[:12000])],
            )
        )

    try:
        chat = client.chats.create(
            model=MODEL_NAME,
            history=gemini_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.65,
                max_output_tokens=3500,
            ),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="The AI service could not be initialized.",
        ) from exc

    async def stream_response() -> AsyncGenerator[str, None]:
        try:
            response_stream = chat.send_message_stream(user_message)
            received = False

            for chunk in response_stream:
                if chunk.text:
                    received = True
                    yield chunk.text

            if not received:
                yield "GlobalPlate AI did not receive a response. Please try again."

        except Exception as exc:
            yield (
                "\n\n⚠️ GlobalPlate AI could not generate a response.\n"
                f"Server error: {str(exc)}"
            )

    return StreamingResponse(
        stream_response(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
            "X-Accel-Buffering": "no",
        },
    )


@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    exception: Exception,
):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested GlobalPlate AI route does not exist.",
        },
    )
