from fastapi import FastAPI, WebSocket, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json
import datetime
import time

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection parameters
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "chatdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to establish PostgreSQL connection with retry logic
def get_db_connection(max_retries=5, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            return conn
        except Exception as e:
            retries += 1
            print(f"Database connection attempt {retries} failed: {e}")
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to database.")
                return None

# Function to create the tables if they don't exist
def setup_database():
    # Wait for PostgreSQL to be ready
    print("Waiting for PostgreSQL to be ready...")
    time.sleep(5)
    
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # Create conversations table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                client_id VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                dialogue JSONB NOT NULL
            )
            ''')
            
            conn.commit()
            print("Database setup complete")
        except Exception as e:
            print(f"Error setting up database: {e}")
        finally:
            cur.close()
            conn.close()
    else:
        print("Failed to set up database - no connection")

# Run database setup on startup
@app.on_event("startup")
async def startup_event():
    setup_database()

# Function to save conversation to database
def save_conversation_to_db(client_id: str, conversation: List[Dict[str, str]]):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            timestamp = datetime.datetime.now()
            
            # Insert the conversation into the database
            cur.execute(
                "INSERT INTO conversations (client_id, timestamp, dialogue) VALUES (%s, %s, %s)",
                (client_id, timestamp, Json(conversation))
            )
            
            conn.commit()
            print(f"Conversation for client {client_id} saved to database")
            return True
        except Exception as e:
            print(f"Error saving conversation to database: {e}")
            return False
        finally:
            cur.close()
            conn.close()
    else:
        print("Failed to save conversation - no database connection")
        return False

# HTML template
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>AI Chat</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            #chatbox {
                height: 400px;
                border: 1px solid #ddd;
                padding: 10px;
                margin-bottom: 20px;
                overflow-y: auto;
                border-radius: 5px;
            }
            .message {
                margin-bottom: 10px;
                padding: 8px 12px;
                border-radius: 18px;
                max-width: 80%;
                word-wrap: break-word;
            }
            .user {
                background-color: #e6f7ff;
                margin-left: auto;
                text-align: right;
                margin-right: 0;
            }
            .bot {
                background-color: #f2f2f2;
                margin-right: auto;
                margin-left: 0;
            }
            .message-container {
                display: flex;
                margin-bottom: 10px;
            }
            form {
                display: flex;
            }
            #messageText {
                flex-grow: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-right: 10px;
            }
            button {
                padding: 10px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
            .typing-indicator {
                color: #666;
                font-style: italic;
                margin-bottom: 10px;
                display: none;
            }
            #endChat {
                margin-top: 10px;
                background-color: #ff6b6b;
            }
            #endChat:hover {
                background-color: #ff5252;
            }
        </style>
    </head>
    <body>
        <h1>AI Chat Assistant</h1>
        <div id="chatbox"></div>
        <div id="typing" class="typing-indicator">AI is typing...</div>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" placeholder="Type your message here..."/>
            <button>Send</button>
        </form>
        <button id="endChat" onclick="endChat()">Encerrar Conversa</button>
        <script>
            const chatbox = document.getElementById('chatbox');
            const typingIndicator = document.getElementById('typing');
            
            var ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            // Add a welcome message when the page loads
            window.onload = function() {
                // No welcome message here - will be sent from server
            };
            
            ws.onopen = function(event) {
                // Request initial message from server when connection opens
                ws.send("INIT_CONNECTION");
            };
            
            ws.onmessage = function(event) {
                typingIndicator.style.display = "none";
                const data = JSON.parse(event.data);
                
                if (data.action === "close") {
                    alert("Conversa encerrada e salva com sucesso!");
                    // Opcional: redirecionar ou recarregar a página
                    window.location.reload();
                    return;
                }
                
                addMessage(data.message, data.sender);
                
                // Auto-scroll to the bottom of the chat
                chatbox.scrollTop = chatbox.scrollHeight;
            };
            
            function addMessage(text, sender) {
                const messageContainer = document.createElement('div');
                messageContainer.className = "message-container";
                
                const message = document.createElement('div');
                message.className = `message ${sender}`;
                message.textContent = text;
                
                if (sender === "user") {
                    messageContainer.style.justifyContent = "flex-end";
                } else {
                    messageContainer.style.justifyContent = "flex-start";
                }
                
                messageContainer.appendChild(message);
                chatbox.appendChild(messageContainer);
            }
            
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                if (input.value.trim() !== "") {
                    // Display user message immediately
                    addMessage(input.value, "user");
                    
                    // Show typing indicator
                    typingIndicator.style.display = "block";
                    
                    // Send to server
                    ws.send(input.value);
                    
                    // Clear input field
                    input.value = '';
                    
                    // Auto-scroll to the bottom of the chat
                    chatbox.scrollTop = chatbox.scrollHeight;
                }
                event.preventDefault();
            }
            
            function endChat() {
                if (confirm("Deseja encerrar a conversa? O diálogo será salvo.")) {
                    ws.send("END_CONVERSATION");
                }
            }
        </script>
    </body>
</html>
"""

class ChatHistory:
    def __init__(self):
        self.conversations = {}
        self.active_connections = {}
    
    def add_message(self, client_id: str, role: str, content: str):
        if client_id not in self.conversations:
            self.conversations[client_id] = []
        
        self.conversations[client_id].append({"role": role, "content": content})
    
    def get_conversation(self, client_id: str) -> List[Dict[str, str]]:
        if client_id not in self.conversations:
            # Initialize with a system message
            self.conversations[client_id] = [
                {"role": "system", "content": """
                Você é um assistente virtual especializado em realizar pré-consultas para pacientes que passarão por exames médicos. Siga estritamente estas diretrizes:

                1. Início da Conversa:
                - Cumprimente o paciente de forma acolhedora
                - Explique que o objetivo é coletar informações para a avaliação médica
                - Informe sobre a confidencialidade dos dados

                2. Coleta de Dados:
                - Solicite nome completo, idade, sexo e contato
                - Pergunte sobre ocupação e hábitos relevantes
                - Investigue doenças pré-existentes e tratamentos atuais
                - Questione sobre histórico de cirurgias e procedimentos
                - Pergunte sobre histórico familiar de doenças relevantes
                - Solicite descrição detalhada dos sintomas atuais
                - Verifique medicamentos em uso e possíveis alergias
                - Pergunte sobre exames anteriores relacionados

                3. Comportamento:
                - Seja respeitoso e profissional
                - Faça uma pergunta por vez, aguardando a resposta antes de prosseguir
                - Use linguagem simples e acessível
                - Mantenha foco na coleta de informações médicas relevantes
                - Não ofereça diagnósticos ou interpretações médicas
                - Se o paciente mencionar sintomas graves, oriente a buscar atendimento imediato

                4. Importante:
                - Este sistema é apenas um suporte para o médico
                - Não substitui uma consulta presencial
                - As informações são confidenciais
                - O diagnóstico e decisão final são do profissional de saúde

                Comece a conversa cumprimentando o paciente e solicitando seu nome.
                """}
            ]
            
            # Add an initial assistant message to guide the first interaction
            self.conversations[client_id].append({
                "role": "assistant", 
                "content": "Olá, seja bem-vindo(a) ao nosso serviço de pré-consulta para exames! Para que possamos ajudar o seu médico a entender melhor o seu quadro de saúde, por favor, responda às perguntas que serão apresentadas a seguir. Lembre-se de que todas as informações são confidenciais e serão utilizadas apenas como suporte para a avaliação médica. Este atendimento não substitui uma consulta presencial e, em caso de emergência, procure atendimento imediato. Ao continuar, você concorda com os termos de uso e nossa política de privacidade. Para começar, por favor, me informe seu nome completo."
            })
        
        return self.conversations[client_id]
    
    def register_connection(self, client_id: str, websocket: WebSocket):
        self.active_connections[client_id] = websocket
    
    def remove_connection(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    def end_conversation(self, client_id: str) -> bool:
        """End the conversation and save it to the database"""
        if client_id in self.conversations:
            # Save conversation to database
            conversation = self.conversations[client_id]
            save_result = save_conversation_to_db(client_id, conversation)
            
            # Clean up conversation data
            if save_result:
                del self.conversations[client_id]
            
            return save_result
        return False

# Initialize chat history
chat_history = ChatHistory()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Generate a unique ID for this client
    client_id = str(id(websocket))
    
    # Register this connection
    chat_history.register_connection(client_id, websocket)
    
    try:
        while True:
            # Receive message from client
            user_message = await websocket.receive_text()
            
            # If this is the initial connection request, send welcome message
            if user_message == "INIT_CONNECTION":
                # Get conversation which will initialize with system message and assistant welcome
                conversation = chat_history.get_conversation(client_id)
                
                # Send the welcome message (which is the last message in the conversation)
                welcome_message = conversation[-1]["content"]
                await websocket.send_json({
                    "sender": "bot",
                    "message": welcome_message
                })
                continue
            
            # If this is an end conversation request
            if user_message == "END_CONVERSATION":
                # Save conversation to database
                save_result = chat_history.end_conversation(client_id)
                
                # Send confirmation to client
                await websocket.send_json({
                    "action": "close",
                    "success": save_result,
                    "message": "Conversa encerrada e salva com sucesso" if save_result else "Erro ao salvar conversa"
                })
                
                # Clean up connection
                chat_history.remove_connection(client_id)
                break
            
            # Add user message to history
            chat_history.add_message(client_id, "user", user_message)
            
            try:
                # Get the full conversation history for context
                conversation = chat_history.get_conversation(client_id)
                
                # Call OpenAI API
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # You can change this to a different model
                    messages=conversation,
                    max_tokens=1000,
                    temperature=0.2,
                )
                
                # Extract the assistant's response
                ai_message = response.choices[0].message.content
                
                # Add AI response to history
                chat_history.add_message(client_id, "assistant", ai_message)
                
                await websocket.send_json({
                    "sender": "bot",
                    "message": ai_message
                })
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                await websocket.send_json({
                    "sender": "bot",
                    "message": f"Encontrei um erro: {error_message}"
                })
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        # Clean up connection on error
        chat_history.remove_connection(client_id)