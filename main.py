from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, json, subprocess, requests, openai
from git import Repo
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/api-endpoint")
async def api_endpoint(request: Request):
    data = await request.json()
    secret = data.get("secret")
    shared_secret = os.getenv("SHARED_SECRET")

    if secret != shared_secret:
        return JSONResponse({"error": "Invalid secret"}, status_code=403)

    # Respond quickly to confirm receipt
    response = {
        "status": "accepted",
        "email": data.get("email"),
        "task": data.get("task"),
        "nonce": data.get("nonce"),
    }
    # Continue processing asynchronously
    subprocess.Popen(["python", "worker.py", json.dumps(data)])
    return JSONResponse(response)
