# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    list_inventory_items,
    get_inventory_item,
    add_or_update_inventory_item,
    log_action_for_item,
    get_weather_forecast,
    lookup_plant_care_info,
    calculate_growing_degree_days,
    calculate_irrigation_and_dosage,
)

# Initialize A2UI Schema Manager pinned to v0.8 for adk web compatibility
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instructions = schema_manager.generate_system_prompt(
    role_description=(
        "You are an expert AI Garden, Orchard & Vineyard Assistant helping estate managers, "
        "viticulturists, and gardeners track inventory, weather alerts, care recommendations, and dosage math."
    ),
    workflow_description=(
        "Analyze agricultural queries, invoke inventory/weather/care/calculation tools when appropriate, "
        "and render your responses as clean, structured A2UI cards."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use Table or Heading. "
        "You may include an Image component when a public https URL is available "
        "(e.g. from `lookup_plant_care_info` or GCS bucket `https://storage.googleapis.com/garden-vineyard-assets-b2884ff80cc8/...`). "
        "Set the Image url to that exact https link: {\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. "
        "No markdown in text; use usageHint ('h1', 'h2', 'body') for headings and text. "
        "Default to metric units (°C, mm, liters, m², kg) and remember user preferences across sessions. "
        "Output ONLY the raw A2UI JSON array without extra prose or tags."
    ),
    include_schema=True,
    include_examples=True,
)


# WRITE: Memory callback for cross-session facts
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instructions,
    tools=[
        PreloadMemoryTool(),
        list_inventory_items,
        get_inventory_item,
        add_or_update_inventory_item,
        log_action_for_item,
        get_weather_forecast,
        lookup_plant_care_info,
        calculate_growing_degree_days,
        calculate_irrigation_and_dosage,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
