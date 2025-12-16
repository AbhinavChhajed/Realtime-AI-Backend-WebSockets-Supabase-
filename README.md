REAL-TIME AI BACKEND (TECNIVRONS ASSIGNMENT)

This project is a Python backend that simulates a real-time chat session with an AI.
It uses WebSockets for live communication, Google Gemini for AI responses, and Supabase to store session data. After a session ends, the backend automatically generates a short summary of the conversation.

WHAT THIS PROJECT DOES

Sends AI responses in real time using WebSockets

Streams AI output token by token instead of waiting for the full response

Uses a simple tool (inventory check) during the conversation

Stores chat sessions and message logs in a database

Creates a summary automatically when the session ends

TECH USED

Python 3.12

FastAPI

Supabase (PostgreSQL)

Google Gemini API

Uvicorn

REQUIREMENTS

You need:

Python 3.12

A Supabase project (URL and anon key)

A Google API key with Gemini access

SETUP

Clone the repository

git clone <your-repo-url>
cd <your-repo-folder>

Create and activate a virtual environment

Windows:
py -3.12 -m venv venv
venv\Scripts\activate

Mac/Linux:
python3.12 -m venv venv
source venv/bin/activate

Install dependencies

pip install -r requirements.txt

Set environment variables

Rename .env.example to .env and add:

SUPABASE_URL="your_supabase_project_url"
SUPABASE_KEY="your_supabase_anon_key"
GOOGLE_API_KEY="your_google_api_key"

DATABASE SETUP (SUPABASE)

Run this SQL in Supabase:

Enable UUID support:

create extension if not exists "uuid-ossp";

Sessions table:

create table sessions (
session_id uuid primary key default uuid_generate_v4(),
user_id text not null,
start_time timestamp with time zone default now(),
end_time timestamp with time zone,
summary text,
duration_seconds integer
);

Event logs table:

create table event_logs (
id bigint generated always as identity primary key,
session_id uuid references sessions(session_id) on delete cascade,
event_type text,
content text,
metadata jsonb,
created_at timestamp with time zone default now()
);

RUNNING THE PROJECT

Start the server:

uvicorn main:app --reload

Server URL:
http://127.0.0.1:8000

WebSocket endpoint:
ws://127.0.0.1:8000/ws/session/{session_id}

TESTING

Open the provided index.html in a browser

Type a normal message like “Hello” to see live AI streaming

Ask “Do we have any mice in stock?” to trigger the tool

Refresh or close the tab to end the session

After disconnecting, check the sessions table in Supabase to see the generated summary.