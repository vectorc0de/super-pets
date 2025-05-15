import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_sessions')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_THRESHOLD = 1000
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://default.supabase.co')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'default_anon_key')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'default_stripe_key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'default_openai_key')
    
    LOGO_URL = "https://vtooxzdgxuoxwgcdzkbd.supabase.co/storage/v1/object/public/logo/pawportallogo.png?t=2024-08-22T18%3A49%3A14.515Z"
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', 'default_resend_key')

    @staticmethod
    def init_app(app):
        pass
