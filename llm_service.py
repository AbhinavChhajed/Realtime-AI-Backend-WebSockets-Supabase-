import os
import google.generativeai as genai
from google.protobuf.struct_pb2 import Struct
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env")

genai.configure(api_key=api_key)

def check_inventory(product_name: str):
    print(f"--- TOOL CALLED: check_inventory for '{product_name}' ---")
    
    inventory_db = {
        "laptop": 50,
        "mouse": 120,
        "keyboard": 30,
        "monitor": 0
    }
    
    product_key = product_name.lower()
    
    if product_key in inventory_db:
        qty = inventory_db[product_key]
        return {"product": product_name, "quantity": qty, "status": "Available" if qty > 0 else "Out of Stock"}
    else:
        return {"product": product_name, "quantity": 0, "status": "Not Found in Catalog"}

available_tools = {
    "check_inventory": check_inventory
}

tools_list = [check_inventory]
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=tools_list
)
async def stream_llm_response(user_message: str, session_id: str = None):
    chat = model.start_chat(enable_automatic_function_calling=False)
    response = await chat.send_message_async(user_message, stream=True)

    full_response_parts = []
    async for chunk in response:
        for part in chunk.parts:
            full_response_parts.append(part)
            if part.text:
                yield part.text

    function_calls = [p.function_call for p in full_response_parts if p.function_call]

    if function_calls:
        tool_responses = []
        
        for fc in function_calls:
            fn_name = fc.name
            fn_args = dict(fc.args)
            
            print(f"AI requested tool: {fn_name} with args: {fn_args}")
            
            if fn_name in available_tools:
                tool_result = available_tools[fn_name](**fn_args)
                
                tr = genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fn_name,
                        response=tool_result
                    )
                )
                tool_responses.append(tr)

        if tool_responses:
            final_response = await chat.send_message_async(
                genai.protos.Content(parts=tool_responses),
                stream=True
            )
            
            async for tool_chunk in final_response:
                if tool_chunk.text:
                    yield tool_chunk.text
async def generate_summary(session_logs: list):
    if not session_logs:
        return "No interaction recorded."

    conversation_text = ""
    for log in session_logs:
        role = "User" if log['event_type'] == "user_message" else "AI"
        content = log.get('content', '')
        conversation_text += f"{role}: {content}\n"

    prompt = f"""
    Analyze this conversation log. Provide a 1-sentence summary of what the user wanted 
    and if their request was resolved.
    
    Logs:
    {conversation_text}
    """
    
    summary_model = genai.GenerativeModel('gemini-2.5-flash')
    response = await summary_model.generate_content_async(prompt)
    return response.text