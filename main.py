import os
import requests  # type: ignore
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext  # type: ignore
from botbuilder.schema import Activity  # type: ignore
from bot import MyBot
import google.generativeai as genai  # type: ignore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#============================================================================

APP_ID = os.getenv("MICROSOFT_APP_ID", "8117b55b-80e3-415c-b2be-31207706ef36")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "VDl8Q~BIwa~9fdM-iAvnYRIJnZG8ibMMe_QFibNZ")

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDssKxVuhRXW3gZ3PEj4Z1TSjDT5GvhGi0")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

bot = MyBot(gemini_model)

@app.get("/")
async def root():
    return {"status": "Backend çalışıyor!"}

@app.post("/api/messages")
async def messages(request: Request):
    try:
        body = await request.json()
        activity = Activity().deserialize(body)
        auth_header = request.headers.get("Authorization", None)

        async def aux_func(turn_context: TurnContext):
            await bot.on_turn(turn_context)

        await adapter.process_activity(activity, auth_header, aux_func)
        return JSONResponse(content={}, status_code=200)
    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

#============================================================================

DIRECT_LINE_SECRET = os.getenv("DIRECT_LINE_SECRET", "3UlKH4RiNBzUT2QIOYZbwnd88Suz3Yk4PBgiXnuLUZsljhTh5Xf7JQQJ99BGAC5RqLJAArohAAABAZBS18fk.5epkxeyXYkV0Me67xt38qY9PX8YdwCyoqpL4EyTq1p7LMkyflofmJQQJ99BGAC5RqLJAArohAAABAZBS1Gby")

@app.post("/get_token", status_code=status.HTTP_200_OK)
async def get_token():
    url = "https://directline.botframework.com/v3/directline/tokens/generate"
    headers = {"Authorization": f"Bearer {DIRECT_LINE_SECRET}"}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return JSONResponse(content=response.json())
    return JSONResponse(content={"error": "Token alınamadı"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
