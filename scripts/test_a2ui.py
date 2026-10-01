import os
import asyncio

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
os.environ["GOOGLE_CLOUD_PROJECT"] = "qwiklabs-gcp-01-b2884ff80cc8"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east1"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from app.agent import root_agent

async def test_a2ui():
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    app_name = "garden-vineyard-app"

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
        app_name=app_name
    )

    user_id = "test_a2ui_user"
    session_id = "test_a2ui_session"

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    prompt = "Show pruning guidelines and diagram for Cabernet Sauvignon"
    print(f"Testing A2UI prompt: '{prompt}'")
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

    events = []
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=msg):
        events.append(event)
        if event.content and event.content.parts:
            for p in event.content.parts:
                if p.inline_data:
                    data_str = p.inline_data.data.decode("utf-8")
                    print("\n✅ A2UI BLOB DETECTED!")
                    print(f"MimeType: {p.inline_data.mime_type}")
                    print(f"Data snippet: {data_str[:250]}...")
                elif p.text:
                    print(f"Text snippet: {p.text[:150]}")

if __name__ == "__main__":
    asyncio.run(test_a2ui())
