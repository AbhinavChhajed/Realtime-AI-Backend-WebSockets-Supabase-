import os
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase credentials not found in .env file")

supabase: Client = create_client(url, key)


async def create_session(session_id: str, user_id: str):
    """
    Creates a new session record in the 'sessions' table.
    """
    data = {
        "session_id": session_id,
        "user_id": user_id,
        "start_time": datetime.now(timezone.utc).isoformat()
    }
    await asyncio.to_thread(lambda: supabase.table("sessions").insert(data).execute())

async def log_event(session_id: str, event_type: str, content: str, metadata: dict = None):
    """
    Logs an event (user message, AI response, tool call) to 'event_logs'.
    """
    data = {
        "session_id": session_id,
        "event_type": event_type,
        "content": content,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await asyncio.to_thread(lambda: supabase.table("event_logs").insert(data).execute())

async def get_chat_history(session_id: str):
    """
    Fetches the conversation history for a specific session.
    """
    response = await asyncio.to_thread(
        lambda: supabase.table("event_logs")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return response.data

async def update_session_summary(session_id: str, summary: str):
    """
    Updates the session with the generated summary and sets the end time.
    """
    session_res = await asyncio.to_thread(
        lambda: supabase.table("sessions")
        .select("start_time")
        .eq("session_id", session_id)
        .single()
        .execute()
    )
    
    start_time_str = session_res.data.get("start_time")
    end_time = datetime.now(timezone.utc)
    
    duration_seconds = 0
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        duration_seconds = int((end_time - start_time).total_seconds())

    data = {
        "summary": summary,
        "end_time": end_time.isoformat(),
        "duration_seconds": duration_seconds
    }
    
    await asyncio.to_thread(
        lambda: supabase.table("sessions")
        .update(data)
        .eq("session_id", session_id)
        .execute()
    )