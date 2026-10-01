# 🌿 AI Garden & Vineyard Assistant

An intelligent, multi-domain agricultural agent built with the **Agent Development Kit (ADK)** for managing small-scale home gardens, orchards, and commercial vineyards.

---

## 🌟 Key Features & Architecture

- **Domain-Specific Inventory (Firestore)**:
  - Tracks plants, vines, soil parameters, and health status in Google Cloud Firestore (`property_inventory` collection).
  - Pre-seeded with items covering Garden (Tomatoes, Strawberries), Orchard (Gala Apple), and Vineyard (Cabernet Sauvignon).

- **Visual Agricultural Guidance (Cloud Storage & Imagen)**:
  - Public Cloud Storage bucket (`gs://garden-vineyard-assets-b2884ff80cc8`) hosting generated visual diagrams (Double Guyot Grapevine Pruning, High-Density Orchard Layout).

- **Agronomic Calculation Tools**:
  - GDD (Growing Degree Days) calculation based on base temperature thresholds.
  - Precise water and fertilizer dosage math based on plot surface area and ET0 evapotranspiration rates.
  - Weather forecasts and frost risk alerts.

- **Persistent Memory Bank**:
  - Multi-session user memory (`PreloadMemoryTool` + `add_session_to_memory` callback) storing climate preferences, soil types, and unit choices.

- **Agent-to-User Interface (A2UI)**:
  - Pinned to A2UI v0.8 schema for rich visual output rendering (Card, Column, Text, and Image components).

- **Custom Interactive Frontend**:
  - Dark-mode responsive FastAPI chat proxy with built-in A2UI card renderer.

- **Vertex AI Agent Engine Deployment**:
  - Deployed to Google Cloud Vertex AI Agent Platform (`agent_runtime`) with native A2A protocol and ADK `:streamQuery` endpoints.

---

## 🛠️ Project Structure

```
garden-vineyard-agent/
├── app/
│   ├── agent.py               # Root agent definition & callback configuration
│   ├── tools.py               # Firestore CRUD, Weather, GDD, Dosage, and Care tools
│   ├── a2ui_utils.py          # A2UI wrapper & callback utilities
│   └── app_utils/             # ADK runtime adapters & A2A middleware
├── frontend/
│   ├── main.py                # FastAPI proxy server
│   └── static/
│       └── index.html         # Web UI with native A2UI card renderer
├── scripts/
│   ├── seed_firestore.py      # Firestore database seeder
│   ├── test_memory.py         # Cross-session Memory Bank verification runner
│   └── test_a2ui.py           # A2UI payload verification test
├── pyproject.toml             # Dependencies (adk, google-cloud-firestore, a2ui-agent-sdk)
└── agents-cli-manifest.yaml   # Agent manifest configuration
```

---

## 🚀 Running Locally

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run Agent Playground**:
   ```bash
   agents-cli playground
   ```

3. **Run Custom Web Frontend**:
   ```bash
   uv run python frontend/main.py
   ```
   Open `http://localhost:8083` in your browser.

---

## ☁️ Deployment & Verification

Deploy to Vertex AI Agent Engine:
```bash
agents-cli deploy --project <YOUR_PROJECT_ID> --region us-east1
```

Query remote agent over A2A protocol:
```bash
agents-cli run --url https://<LOCATION>-aiplatform.googleapis.com/v1/projects/<PROJECT>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID> --mode a2a "Show my vineyard inventory"
```
