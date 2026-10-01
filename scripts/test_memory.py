import os
import asyncio

# Set Vertex AI mode and GCP project for GenAI client
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
os.environ["GOOGLE_CLOUD_PROJECT"] = "qwiklabs-gcp-01-b2884ff80cc8"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east1"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from app.agent import root_agent

async def run_memory_test():
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    app_name = "garden-vineyard-app"

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
        app_name=app_name
    )

    user_id = "estate_manager_01"
    session_1_id = "session_alpha"
    session_2_id = "session_beta"

    print("--- STARTING SESSION 1 ---")
    prompt_1 = "Hi! Remember that my vineyard is in Saint-Émilion, France, my soil pH is 6.4, and my preferred grape variety is Pinot Noir."
    print(f"User ({user_id}, {session_1_id}): {prompt_1}")

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_1_id
    )

    msg1 = types.Content(role="user", parts=[types.Part.from_text(text=prompt_1)])

    response_1_text = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_1_id, new_message=msg1):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_1_text += part.text

    print(f"Agent Response 1: {response_1_text.strip()}\n")

    print("--- STARTING SESSION 2 (New Session ID, Same User ID) ---")
    prompt_2 = "Where is my vineyard located, what is my soil pH, and what is my preferred grape variety?"
    print(f"User ({user_id}, {session_2_id}): {prompt_2}")

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_2_id
    )

    msg2 = types.Content(role="user", parts=[types.Part.from_text(text=prompt_2)])

    response_2_text = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_2_id, new_message=msg2):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_2_text += part.text

    print(f"Agent Response 2: {response_2_text.strip()}\n")

if __name__ == "__main__":
    asyncio.run(run_memory_test())
