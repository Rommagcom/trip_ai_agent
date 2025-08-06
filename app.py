import os
import json
from flask import Flask, render_template, request, jsonify
from pymilvus import MilvusClient
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing_extensions import Annotated, TypedDict
from typing import Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio

load_dotenv()

app = Flask(__name__)

class ConversationalResponse(TypedDict):
    response: Annotated[str, ..., "A conversational response to the user's query"]

class FinalResponse(TypedDict):
    final_output: Union[ConversationalResponse, None]

class GenericResponse(BaseModel):
    """Respond to the user in this format."""
    final_output: str = Field(description="A detailed, full response to the user's query in markdown format. Include all found information about tours, prices, descriptions, and recommendations. DO NOT use short codes or abbreviations.")
    details: str = Field(description="Additional details or conversational response to the user's query in markdown format")

# Initialize Ollama model
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

response_model_raw = ChatOllama(model="qwen3:8b", base_url=OLLAMA_BASE_URL)

# Initialize MCP client
mcp_client = None
mcp_tools = []

async def initialize_mcp_client():
    global mcp_client, mcp_tools
    try:
        mcp_client = MultiServerMCPClient({
            "web_search": {
                "url": "http://127.0.0.1:9010/mcp",
                "transport": "streamable_http",
            }
        })
        mcp_tools = await mcp_client.get_tools()
        print(f"✅ MCP tools initialized: {len(mcp_tools)} tools available")
    except Exception as e:
        print(f"Warning: Could not initialize MCP client: {e}")
        mcp_tools = []

# Initialize MCP client on startup
asyncio.run(initialize_mcp_client())


SYSTEM_PROMPT_TEMPLATE = """
Вы — ИИ-ассистент для поиска туров и путешествий. Вы помогаете пользователям найти информацию на основе их запросов.
У тебя есть доступ к инструментам для поиска информации, странах и предложениях, включая векторную базу данных Milvus.

{tools_list}

ВСЕГДА используйте инструменты для ответа на вопросы. НИКОГДА не отвечайте, используя только свои знания.
Если ты не можешь ответить с помощью инструмента, напиши: "Я не могу найти информацию по Вашему запросу."

ВАЖНО: В поле final_output вы ДОЛЖНЫ предоставить ПОЛНЫЙ и ПОДРОБНЫЙ ответ пользователю в формате markdown.
НЕ используйте короткие коды или сокращения типа 'processed_data', 'data_processed', 'summary'.
Предоставьте детальную информацию о турах, ценах, описаниях, рекомендациях и всех найденных данных.

Верни подробный ответ на исходный вопрос пользователя в формате markdown.

"""

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
async def search_tours():
    try:
        data = request.get_json()
        user_input = data.get('query', '')
        
        if not user_input:
            return jsonify({'error': 'Query is required'}), 400

        # Prepare the prompt
        tools_list = "\n".join([f"- {tool.name}: {tool.description}" for tool in mcp_tools]) if mcp_tools else "Нет доступных инструментов"
        
        USER_PROMPT = f"""
Ответь на вопрос пользователя максимально точно и подробно: {user_input}
"""

         
        # Create agent
        agent = create_react_agent(response_model_raw, mcp_tools, response_format=GenericResponse, debug=True)
        
        # Invoke agent with system prompt
        system_message = SYSTEM_PROMPT_TEMPLATE.format(tools_list=tools_list)
        user_message = USER_PROMPT.format(user_input=user_input)
        
        print("System message:", system_message[:200] + "...")
        print("User message:", user_input)
        
        response = await agent.ainvoke({
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ]
        })
        
        print("Agent response type:", type(response))
        print("Agent response keys:", response.keys() if isinstance(response, dict) else "Not a dict")
        print("Agent response:", response)
        
        # Extract the final answer
        print("Full response structure:", response)
        
        if isinstance(response, dict):
            # Try to extract from structured_response
            if "structured_response" in response:
                structured_response = response["structured_response"]
                print("Structured response:", structured_response)
                
                if hasattr(structured_response, 'final_output'):
                    final_output = structured_response.final_output
                    details = getattr(structured_response, 'details', '')
                elif isinstance(structured_response, dict):
                    final_output = structured_response.get('final_output', str(structured_response))
                    details = structured_response.get('details', '')
                else:
                    final_output = str(structured_response)
                    details = ''
            
            # Try to extract from other possible keys
            elif "output" in response:
                final_output = response["output"]
                details = response.get("details", "")
            elif "result" in response:
                final_output = response["result"]
                details = response.get("details", "")
            else:
                # Try to find any text content in the response
                final_output = str(response)
                details = ""
        else:
            final_output = str(response)
            details = ''
        
        # If we still don't have meaningful content, try to extract from the raw response
        if not final_output or final_output == "None" or len(final_output.strip()) < 10 or final_output in ['processed_data', 'data_processed', 'summary']:
            # Look for any text content in the response
            response_str = str(response)
            
            # Try to extract from the full response text
            if "structured_summary_above" in response_str:
                # Extract content after structured_summary_above
                parts = response_str.split("structured_summary_above")
                if len(parts) > 1:
                    extracted_content = parts[1].strip()
                    if len(extracted_content) > 20:  # Make sure we have meaningful content
                        final_output = extracted_content
                    else:
                        final_output = "Получен ответ от ИИ, но формат не распознан. Попробуйте переформулировать запрос."
                else:
                    final_output = "Получен ответ от ИИ, но формат не распознан. Попробуйте переформулировать запрос."
            elif "Окончательный ответ:" in response_str:
                # Extract content after "Окончательный ответ:"
                parts = response_str.split("Окончательный ответ:")
                if len(parts) > 1:
                    extracted_content = parts[1].strip()
                    if len(extracted_content) > 20:
                        final_output = extracted_content
                    else:
                        final_output = "Получен ответ от ИИ, но формат не распознан. Попробуйте переформулировать запрос."
                else:
                    final_output = "Получен ответ от ИИ, но формат не распознан. Попробуйте переформулировать запрос."
            else:
                # Try to find any meaningful text in the response
                if len(response_str) > 100:  # If response is long enough, use it
                    final_output = response_str
                else:
                    final_output = "Получен ответ от ИИ, но формат не распознан. Попробуйте переформулировать запрос."
        
        return jsonify({
            "result": final_output,
            "details": details
        })

    except Exception as e:
        print(f"Error in search_tours: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000) 