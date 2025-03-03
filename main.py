# from fastapi import FastAPI, WebSocket, Depends, HTTPException, Request
# from fastapi.responses import HTMLResponse
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel, Field
# import os
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
# from typing import List, Dict, Any


# load_dotenv()


# app = FastAPI()


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# html = """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>AI Chat</title>
#         <style>
#             body {
#                 font-family: Arial, sans-serif;
#                 max-width: 800px;
#                 margin: 0 auto;
#                 padding: 20px;
#             }
#             h1 {
#                 color: #333;
#                 text-align: center;
#             }
#             #chatbox {
#                 height: 400px;
#                 border: 1px solid #ddd;
#                 padding: 10px;
#                 margin-bottom: 20px;
#                 overflow-y: auto;
#                 border-radius: 5px;
#             }
#             .message {
#                 margin-bottom: 10px;
#                 padding: 8px 12px;
#                 border-radius: 18px;
#                 max-width: 80%;
#                 word-wrap: break-word;
#             }
#             .user {
#                 background-color: #e6f7ff;
#                 margin-left: auto;
#                 text-align: right;
#                 margin-right: 0;
#             }
#             .bot {
#                 background-color: #f2f2f2;
#                 margin-right: auto;
#                 margin-left: 0;
#             }
#             .message-container {
#                 display: flex;
#                 margin-bottom: 10px;
#             }
#             form {
#                 display: flex;
#             }
#             #messageText {
#                 flex-grow: 1;
#                 padding: 10px;
#                 border: 1px solid #ddd;
#                 border-radius: 5px;
#                 margin-right: 10px;
#             }
#             button {
#                 padding: 10px 15px;
#                 background-color: #4CAF50;
#                 color: white;
#                 border: none;
#                 border-radius: 5px;
#                 cursor: pointer;
#             }
#             button:hover {
#                 background-color: #45a049;
#             }
#             .typing-indicator {
#                 color: #666;
#                 font-style: italic;
#                 margin-bottom: 10px;
#                 display: none;
#             }
#         </style>
#     </head>
#     <body>
#         <h1>AI Chat Assistant</h1>
#         <div id="chatbox"></div>
#         <div id="typing" class="typing-indicator">AI is typing...</div>
#         <form action="" onsubmit="sendMessage(event)">
#             <input type="text" id="messageText" autocomplete="off" placeholder="Type your message here..."/>
#             <button>Send</button>
#         </form>
#         <script>
#             const chatbox = document.getElementById('chatbox');
#             const typingIndicator = document.getElementById('typing');
            
#             var ws = new WebSocket("ws://localhost:8000/ws");
            
#             // Add a welcome message when the page loads
#             window.onload = function() {
#                 addMessage("Olá, seja bem-vindo(a) ao nosso serviço de pré-consulta para exames! Para que possamos ajudar o seu médico a entender melhor o seu quadro de saúde, por favor, responda às perguntas que serão apresentadas a seguir. Lembre-se de que todas as informações são confidenciais e serão utilizadas apenas como suporte para a avaliação médica. Este atendimento não substitui uma consulta presencial e, em caso de emergência, procure atendimento imediato. Ao continuar, você concorda com os termos de uso e nossa política de privacidade. Vamos começar?", "bot");
#             };
            
#             ws.onmessage = function(event) {
#                 typingIndicator.style.display = "none";
#                 const data = JSON.parse(event.data);
#                 addMessage(data.message, data.sender);
                
#                 // Auto-scroll to the bottom of the chat
#                 chatbox.scrollTop = chatbox.scrollHeight;
#             };
            
#             function addMessage(text, sender) {
#                 const messageContainer = document.createElement('div');
#                 messageContainer.className = "message-container";
                
#                 const message = document.createElement('div');
#                 message.className = `message ${sender}`;
#                 message.textContent = text;
                
#                 if (sender === "user") {
#                     messageContainer.style.justifyContent = "flex-end";
#                 } else {
#                     messageContainer.style.justifyContent = "flex-start";
#                 }
                
#                 messageContainer.appendChild(message);
#                 chatbox.appendChild(messageContainer);
#             }
            
#             function sendMessage(event) {
#                 var input = document.getElementById("messageText");
#                 if (input.value.trim() !== "") {
#                     // Display user message immediately
#                     addMessage(input.value, "user");
                    
#                     // Show typing indicator
#                     typingIndicator.style.display = "block";
                    
#                     // Send to server
#                     ws.send(input.value);
                    
#                     // Clear input field
#                     input.value = '';
                    
#                     // Auto-scroll to the bottom of the chat
#                     chatbox.scrollTop = chatbox.scrollHeight;
#                 }
#                 event.preventDefault();
#             }
#         </script>
#     </body>
# </html>
# """


# class ChatHistory:
#     def __init__(self):
#         self.conversations = {}
    
#     def add_message(self, client_id: str, role: str, content: str):
#         if client_id not in self.conversations:
#             self.conversations[client_id] = []
        
#         self.conversations[client_id].append({"role": role, "content": content})
    
#     def get_conversation(self, client_id: str) -> List[Dict[str, str]]:
#         if client_id not in self.conversations:
#             # Initialize with a system message
#             self.conversations[client_id] = [
#                 {"role": "system", "content": """
#                  Você é um assistente virtual especializado em realizar pré-consultas para pacientes que passarão por exames. Seu objetivo é coletar de forma detalhada e aprofundada todas as informações relevantes para a avaliação médica, garantindo sempre a segurança jurídica e a confidencialidade dos dados. Lembre-se: este sistema não substitui o atendimento médico presencial nem fornece diagnóstico definitivo. As informações coletadas destinam-se a auxiliar o médico na análise, mas a responsabilidade pela interpretação e decisão final é exclusiva do profissional de saúde.
#                 1. Início da Conversa
#                 Cumprimente o paciente de forma acolhedora e explique que o objetivo é realizar uma pré-consulta para coletar informações que ajudarão na avaliação médica.
#                 Informe que todas as informações serão tratadas com estrita confidencialidade e que o sistema não oferece diagnóstico, sendo apenas um suporte para o médico.
#                 2. Coleta de Dados Pessoais e Contexto
#                 Solicite os dados essenciais: nome completo, idade, sexo e contato.
#                 Pergunte sobre a ocupação e hábitos de vida que possam influenciar o quadro clínico.
#                 3. Histórico Clínico Detalhado
#                 Questione sobre doenças pré-existentes, condições crônicas e tratamentos em andamento.
#                 Investigue cirurgias e procedimentos anteriores, incluindo datas e motivos.
#                 Indague sobre histórico familiar de doenças relevantes (por exemplo, diabetes, hipertensão, doenças cardíacas).
#                 4. Sintomas e Queixas Atuais
#                 Solicite uma descrição detalhada dos sintomas atuais, considerando início, duração, intensidade, e evolução.
#                 Explore fatores que agravem ou aliviem os sintomas.
#                 Estimule o paciente a relatar quaisquer sintomas, mesmo os que possam parecer irrelevantes.
#                 5. Informações sobre Medicações e Alergias
#                 Pergunte sobre os medicamentos utilizados regularmente, incluindo dosagens e frequência.
#                 Verifique a existência de alergias a medicamentos, alimentos ou outras substâncias, pedindo detalhes sobre reações anteriores.
#                 6. Exames Anteriores e Investigações
#                 Questione se o paciente já realizou exames relacionados ao quadro atual, solicitando informações sobre datas, resultados e interpretações anteriores.
#                 Oriente o paciente sobre a importância de levar exames pré-existentes à consulta.
#                 7. Exploração de Outras Informações Relevantes
#                 Incentive o paciente a compartilhar informações adicionais que julgue importantes para a avaliação, mesmo que pareçam secundárias.
#                 Utilize perguntas abertas para descobrir fatores de risco ou detalhes não mencionados inicialmente.
#                 8. Orientação para Aprofundamento
#                 Se as respostas forem superficiais, faça perguntas complementares para obter mais detalhes, como “pode me contar mais sobre…?”, “como você percebe essa mudança?” ou “pode descrever melhor como se sente quando…?”.
#                 9. Guardrails de Segurança e Conformidade Legal
#                 Isenção de Responsabilidade: Inclua uma mensagem automática ao final da coleta informando que as informações prestadas não substituem uma consulta médica completa e não devem ser utilizadas para diagnóstico sem a devida avaliação de um profissional qualificado.
#                 Confidencialidade: Garanta que os dados serão armazenados e tratados conforme as normas de proteção de dados vigentes (por exemplo, LGPD), e que serão utilizados exclusivamente para auxiliar na consulta.
#                 Limitações do Sistema: Se o paciente mencionar sintomas graves ou situações de emergência, oriente-o imediatamente a procurar atendimento médico urgente.
#                 Registro de Consentimento: Sempre que possível, solicite o consentimento do paciente para o uso dos dados, esclarecendo que ele autoriza o encaminhamento das informações para o médico responsável.
#                 Neutralidade e Segurança: Evite fornecer conselhos ou interpretações que possam ser entendidos como diagnósticos. Caso haja dúvidas sobre a integridade ou a completude das informações, indique a necessidade de uma avaliação presencial.                 
#                  """}
#             ]
        
#         return self.conversations[client_id]


# chat_history = ChatHistory()

# @app.get("/")
# async def get():
#     return HTMLResponse(html)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
    
#     # Generate a unique ID for this client
#     client_id = id(websocket)
    
#     try:
#         while True:
#             # Receive message from client
#             user_message = await websocket.receive_text()
            
#             # Add user message to history
#             chat_history.add_message(client_id, "user", user_message)
            
#             try:
#                 # Get the full conversation history for context
#                 conversation = chat_history.get_conversation(client_id)
                
#                 # Call OpenAI API
#                 response = client.chat.completions.create(
#                     model="gpt-4o-mini",  # You can change this to a different model
#                     messages=conversation,
#                     max_tokens=1000,
#                     temperature=0.2,
#                 )
                
#                 # Extract the assistant's response
#                 ai_message = response.choices[0].message.content
                
#                 # Add AI response to history
#                 chat_history.add_message(client_id, "assistant", ai_message)
                
#                 # Send response back to client
#                 await websocket.send_json({
#                     "sender": "bot",
#                     "message": ai_message
#                 })
                
#             except Exception as e:
#                 # Handle API errors
#                 error_message = f"Error: {str(e)}"
#                 await websocket.send_json({
#                     "sender": "bot",
#                     "message": f"I encountered an error: {error_message}"
#                 })
                
#     except Exception as e:
#         print(f"WebSocket error: {e}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, WebSocket, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any

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

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        <script>
            const chatbox = document.getElementById('chatbox');
            const typingIndicator = document.getElementById('typing');
            
            var ws = new WebSocket("ws://localhost:8000/ws");
            
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
        </script>
    </body>
</html>
"""

class ChatHistory:
    def __init__(self):
        self.conversations = {}
    
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

# Initialize chat history
chat_history = ChatHistory()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Generate a unique ID for this client
    client_id = id(websocket)
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)