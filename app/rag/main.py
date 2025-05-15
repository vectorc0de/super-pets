from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import os
import socketio
import uvicorn
from dotenv import load_dotenv

class PetShelterSocketAssistant:
    def __init__(self):
        load_dotenv()
        
        # Initialize AI components
        self.setup_ai()
        
        # Initialize Socket.IO server
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.app = socketio.ASGIApp(self.sio)
        
        # Setup socket event handlers
        self.setup_socket_handlers()

    def setup_ai(self):
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.llm = ChatOpenAI(temperature=0, openai_api_key=self.OPENAI_API_KEY)
        
        # Initialize database
        self.db_uri = os.getenv('DB_URI')
        self.db = SQLDatabase.from_uri(
            self.db_uri,
            include_tables=[
                'diagnostic_tests',
                'donations',
                'events',
                'partners',
                'people',
                'pets',
                'procedures',
                'treatments',
                'vaccinations',
                'vet_checks'
            ],
            sample_rows_in_table_info=2
        )
        self.db_chain = SQLDatabaseChain.from_llm(self.llm, self.db, verbose=True)
        
        # Setup message templates
        self.system_message = """You are a helpful assistant for a pet shelter application.
        You can provide information about pets, their medical history, adoption status, and various shelter activities.
        Please use the database context to answer questions about our animals, events, and operations.
        Be friendly and informative, always keeping animal welfare in mind."""
        
        self.human_query_template = HumanMessagePromptTemplate.from_template(
            """Input:
            {human_input}
            
            Context:
            {db_context}
            
            Output:
            """
        )
        
        self.messages = [SystemMessage(content=self.system_message)]

    def setup_socket_handlers(self):
        @self.sio.event
        async def connect(sid, environ):
            print('Client connected:', sid)
            
            greeting = "What is my latest task? Warmly greet me too"
            response = await self.generate_response(greeting)
            await self.sio.emit('response', response)

        @self.sio.event
        async def message(sid, data):
            print('Message received:', data)
            response = await self.generate_response(data)
            await self.sio.emit('response', response)

    def retrieve_from_db(self, query: str) -> str:
        print(f"Database query: {query}")
        db_context = self.db_chain(query)
        result = db_context['result'].strip()
        print(f"Database context: {result}")
        return result

    async def generate_response(self, query: str) -> str:
        db_context = self.retrieve_from_db(query)
        
        query_message = self.human_query_template.format(
            human_input=query, 
            db_context=db_context
        )
        self.messages.append(query_message)
        
        response = self.llm(self.messages).content
        print(f"Generated response: {response}")
        
        # Add response to message history
        self.messages.append(SystemMessage(content=response))
        
        return response

    def run(self, host='0.0.0.0', port=8000):
        uvicorn.run(self.app, host=host, port=port)

# Usage example
if __name__ == '__main__':
    assistant = PetShelterSocketAssistant()
    assistant.run()