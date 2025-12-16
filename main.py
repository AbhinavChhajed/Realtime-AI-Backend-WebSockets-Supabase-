from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from database import create_session, log_event, get_chat_history, update_session_summary
from llm_service import stream_llm_response, generate_summary

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Real-time AI Backend is running"}

async def process_post_session(session_id: str):
    """
    Background task: Summarize session and update DB after disconnect.
    """
    print(f"Starting post-session processing for {session_id}...")
    
    logs = await get_chat_history(session_id)
    
    summary = await generate_summary(logs)
    print(f"Generated Summary: {summary}")
    
    await update_session_summary(session_id, summary)
    print(f"Session {session_id} updated successfully.")

@app.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, background_tasks: BackgroundTasks):
    await websocket.accept()
    
    await create_session(session_id, user_id="demo_user")
    
    try:
        while True:
            data = await websocket.receive_text()
            await log_event(session_id, "user_message", data)
        
            full_ai_response = ""
            try:
                async for token in stream_llm_response(data):
                    await websocket.send_text(token)
                    full_ai_response += token
                
                await log_event(session_id, "ai_message", full_ai_response)
                
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                await websocket.send_text(error_msg)
                await log_event(session_id, "system_event", error_msg)

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
        await process_post_session(session_id) 