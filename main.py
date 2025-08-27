import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import google.generativeai as genai  # type: ignore

#======================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDssKxVuhRXW3gZ3PEj4Z1TSjDT5GvhGi0")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

#======================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#======================================================

@app.get("/")
async def health_check():
    return {"status": "LangGraph Gemini backend çalışıyor!"}

#======================================================

async def handle_invoke(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    if not messages:
        return {"error": "Mesaj listesi boş"}

    user_message = messages[-1].get("content", "")
    if not user_message:
        return {"error": "Mesaj içeriği boş"}

    async def stream_response():
        chat = model.start_chat()
        async for chunk in chat.send_message_async(user_message, stream=True):
            if chunk.text:
                yield chunk.text

    return StreamingResponse(stream_response(), media_type="text/plain")

#======================================================

@app.post("/invoke")
async def invoke(request: Request):
    return await handle_invoke(request)

@app.post("/api/copilotkit")
async def copilotkit_endpoint(request: Request):
    return await handle_invoke(request)

#======================================================