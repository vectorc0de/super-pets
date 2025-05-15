from flask_session import Session
from flask_cors import CORS
from supabase import create_client
import stripe
import openai
import os

def init_extensions(app):
    CORS(app, resources={r"/files/*": {"origins": "*"}})
    Session(app)
    
    init_supabase(app)
    init_stripe()
    init_openai()

def init_supabase(app):
    supabase_url = app.config['SUPABASE_URL']
    supabase_anon_key = app.config['SUPABASE_ANON_KEY']
    app.supabase = create_client(supabase_url, supabase_anon_key)

def init_stripe():
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def init_openai():
    openai.api_key = os.getenv('OPENAI_API_KEY')
