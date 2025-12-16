# Real-time AI Backend (Tecnvirons Assignment)

A high-performance, asynchronous Python backend simulating a real-time conversational session. This project implements bi-directional WebSockets, real-time LLM streaming with **Google Gemini**, persistent storage with **Supabase**, and automated post-session summarization.

## 🚀 Features

* **Real-time Streaming:** Immediate token-by-token responses using WebSockets to simulate low-latency conversation.
* **Complex LLM Interaction:** Implements **Function Calling** (Tool Use) to simulate internal data fetching during the conversation.
* **Asynchronous Architecture:** Built with **FastAPI** to handle concurrent sessions without blocking.
* **Data Persistence:** Stores session metadata and granular event logs in a **Supabase (PostgreSQL)** database.
* **Post-Session Automation:** Automatically triggers a background task upon disconnection to analyze the logs and generate a session summary.

## 🛠 Tech Stack

* **Language:** Python 3.12
* **Framework:** FastAPI (Asynchronous Web Framework)
* **Database:** Supabase (PostgreSQL)
* **LLM:** Google Gemini (via `google-generativeai`)
* **Server:** Uvicorn

## 📋 Prerequisites

Before running the project, ensure you have:
1.  **Python 3.12** installed on your machine.
2.  A **Supabase** project (you need the URL and Anon Key).
3.  A **Google Cloud API Key** with access to Gemini models.

## ⚙️ Installation & Setup
```bash
1. Clone the Repository
git clone https://github.com/AbhinavChhajed/Realtime-AI-Backend-WebSockets-Supabase-
cd Realtime-AI-Backend-WebSockets-Supabase-


2. Create Virtual Environment
Bash
# Windows (verify version first: py --list)
py -3.12 -m venv venv
venv\Scripts\activate

# Mac/Linux
python3.12 -m venv venv
source venv/bin/activate

3. Install Dependencies
Bash
pip install -r requirements.txt

4. Configure Environment
Rename the .env.example file to .env:
Bash
mv .env.example .env
Open .env and add your credentials.

SUPABASE_URL="your_supabase_project_url"
SUPABASE_KEY="your_supabase_anon_key"
GOOGLE_API_KEY="your_google_gemini_api_key"

🗄️ Database Schema (Supabase)
You must execute the following SQL commands in your Supabase SQL Editor to set up the required tables.
SQL

create table sessions (
  session_id uuid primary key default uuid_generate_v4(),
  user_id text not null,
  start_time timestamp with time zone default now(),
  end_time timestamp with time zone,
  summary text,
  duration_seconds integer
);

create table event_logs (
  id bigint generated always as identity primary key,
  session_id uuid references sessions(session_id) on delete cascade,
  event_type text check (event_type in ('user_message', 'ai_message', 'tool_call', 'system_event')),
  content text,
  metadata jsonb,
  created_at timestamp with time zone default now()
);

🏃‍♂️ How to Run
Start the WebSocket server using Uvicorn:
Bash
uvicorn main:app --reload
The server will start at http://127.0.0.1:8000.
The WebSocket endpoint is available at ws://127.0.0.1:8000/ws/session/{session_id}.