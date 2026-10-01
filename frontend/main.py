import os
import json
import re
import uuid
from typing import Dict, Any, List

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-01-b2884ff80cc8")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-east1")

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types

from app.agent import root_agent

app = FastAPI(title="AI Garden & Vineyard Assistant Proxy")

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
app_name = "garden-vineyard-app"

runner = Runner(
    agent=root_agent,
    session_service=session_service,
    memory_service=memory_service,
    app_name=app_name
)

_active_sessions: Dict[str, str] = {}


@app.post("/chat")
async def chat(req: Request):
    try:
        body = await req.json()
        message = body.get("message", "")
        user_id = body.get("user_id") or "web-user"

        if user_id not in _active_sessions:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            _active_sessions[user_id] = session_id
        
        session_id = _active_sessions[user_id]

        msg = types.Content(role="user", parts=[types.Part.from_text(text=message)])
        
        parts_out: List[Dict[str, Any]] = []

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=msg):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.inline_data:
                        blob_str = part.inline_data.data.decode("utf-8")
                        blob_clean = re.sub(r"</?(?:a2a_datapart_json|a2ui-json)>", "", blob_str).strip()
                        try:
                            json_obj = json.loads(blob_clean)
                            inner = json_obj.get("data", json_obj)
                            parts_out.append({"kind": "a2ui", "data": inner})
                        except Exception:
                            parts_out.append({"kind": "text", "text": blob_str})
                    elif part.text:
                        raw_text = part.text.strip()
                        if "<a2ui-json>" in raw_text or "<a2a_datapart_json>" in raw_text or raw_text.startswith("{") and "components" in raw_text:
                            clean_text = re.sub(r"</?(?:a2a_datapart_json|a2ui-json)>", "", raw_text).strip()
                            try:
                                json_obj = json.loads(clean_text)
                                inner = json_obj.get("data", json_obj)
                                if "surfaceUpdate" in inner or "components" in inner or "surfaceId" in inner:
                                    if "components" in inner and "surfaceUpdate" not in inner:
                                        inner = {"surfaceUpdate": inner}
                                    parts_out.append({"kind": "a2ui", "data": inner})
                                else:
                                    parts_out.append({"kind": "text", "text": raw_text})
                            except Exception:
                                parts_out.append({"kind": "text", "text": raw_text})
                        else:
                            parts_out.append({"kind": "text", "text": raw_text})

        if not parts_out:
            parts_out = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]

        return JSONResponse({"parts": parts_out})

    except Exception as exc:
        return JSONResponse(
            status_code=200,
            content={"parts": [{"kind": "text", "text": f"Error processing request: {type(exc).__name__}: {exc}"}]}
        )


app.mount("/", StaticFiles(directory="frontend/static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8083))
    uvicorn.run(app, host="0.0.0.0", port=port)
