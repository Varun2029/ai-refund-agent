---
title: AI Refund Agent
emoji: 💸
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Refund AI: Multi-Agent Customer Support Platform

Welcome to **Refund AI**, a full-stack, production-ready AI agent platform designed to automate e-commerce refund operations. 

This repository was developed to showcase an advanced multi-agent architecture handling end-to-end customer support workflows, including natural language understanding, RAG-based policy checking, fraud detection, and manager escalations.

---

## 🎥 Submission Links

- **Loom Video Walkthrough:** https://www.loom.com/share/d01060a28e61417fa7be574cc42292f3

- **Public GitHub Repository:** https://github.com/Varun2029/ai-refund-agent

---

## 🏗️ Code Tour: Repository Architecture & Tool Orchestration

Our architecture separates the frontend client from a robust FastAPI backend. The core AI orchestration is handled by **LangGraph**, which coordinates a team of 5 specialized agents.

### Repository Architecture
```text
ai-refund-agent/
├── app/                           # Backend (FastAPI + Python)
│   ├── agents/                    # AI Agents (Customer, CRM, Policy, Fraud, Decision)
│   ├── api/                       # REST APIs and WebSocket handlers
│   ├── db/                        # PostgreSQL models and database session
│   ├── graph/                     # LangGraph workflow orchestration
│   ├── rag/                       # Local FAISS vector store and Markdown policies
│   ├── schemas/                   # Pydantic data validation models
│   └── services/                  # Business logic (LLM Provider, Email SMTP, Auth)
├── frontend/                      # React SPA (Vite + TailwindCSS + Radix UI)
└── docker-compose.yml             # Containerized deployment
```

### Tool Orchestration (LangGraph Pipeline)
The system uses **LangGraph** to construct a deterministic state machine where each node is an LLM agent with a specific toolset:

1. **Customer Agent (`app/agents/customer_agent.py`)**: Parses the user's natural language request to extract intent, order number, and issue descriptions.
2. **CRM Agent (`app/agents/crm_agent.py`)**: Interacts with the `app/db` to verify the customer exists and retrieves their historical order data. *(No LLM needed here, acts as a deterministic data tool)*
3. **Policy Agent (`app/agents/policy_agent.py`)**: Uses **RAG** (Retrieval-Augmented Generation) via `SentenceTransformers` and `FAISS` to embed the issue and fetch relevant company refund policies.
4. **Fraud Agent (`app/agents/fraud_agent.py`)**: Analyzes customer history and current request against a rule-based engine to generate a risk score (0-100).
5. **Decision Agent (`app/agents/decision_agent.py`)**: Synthesizes the outputs of all previous agents to make a final decision: `APPROVED`, `DENIED`, or `ESCALATED`.

### 🎙️ Voice Stream Handling
Voice capabilities are handled natively in the browser to ensure zero latency and zero backend audio processing costs.
- **Speech-to-Text (Input):** We use the browser's native `Web Speech API` in `frontend/src/lib/speech.ts` to capture microphone input, transcribe it into text in real-time, and send it to the backend via WebSockets.
- **Text-to-Speech (Output):** Once the `Decision Agent` finalizes the refund, a concise, plain-English summary is generated and sent back to the client. The `VoiceController` immediately speaks this result aloud to the customer.

---

## 🧠 Reasoning Logs & Failure/Retry Handling

A major focus of this platform is **observability**. We do not want a "black box" AI.

### Real-Time Reasoning Logs
As the LangGraph pipeline executes, each agent yields its internal thought process and confidence scores via **WebSockets** (`app/api/websocket.py`). 
- **Admin View:** In the `Admin Dashboard -> Agent Logs`, managers can watch the live trace of exactly *why* a policy was matched or *why* a fraud score was elevated. 

### Failure, Retries, and Escalations
The system is designed to fail gracefully and keep humans in the loop:
1. **Agent-Level Fallbacks:** If the `Policy Agent` fails to find relevant RAG documents, or if the LLM provider (Gemini/Groq) times out, the `LLMProvider` service catches the exception and flags the node.
2. **Deterministic Escalations:** If the `Decision Agent` encounters ambiguity (e.g., fraud score > 60, or a missing order number), the pipeline **aborts the automated decision** and updates the database state to `ESCALATED`.
3. **Manager Intervention:** Escalated workflows instantly appear in the **Admin Escalations Panel** (`frontend/src/pages/EscalationsPage.tsx`). Here, a human manager reviews the entire reasoning trace, order history, and manually clicks `Approve` or `Deny`.
4. **SMTP Notifications:** Whether automated or manually resolved, `app/services/email_service.py` safely attempts to deliver an asynchronous email to the customer using `aiosmtplib`. If SMTP fails or is unconfigured, it gracefully degrades to a mock console log.

---

## 🚀 Quick Start Instructions

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/ai-refund-agent.git
cd ai-refund-agent

# Create virtual environment & install requirements
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Important: Add your GEMINI_API_KEY or GROQ_API_KEY to the .env file

# Seed the database with demo users & orders
python -m app.db.seed

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
- Open `http://localhost:5173`
- **Customer View:** Submit a refund request (e.g., *"My headphones for ORD-1001 are broken"*).
- **Admin View:** Select "Admin" on the login page (uses `admin@refundai.com` / `admin123`) to view the dashboard, live reasoning logs, and escalation queue.
