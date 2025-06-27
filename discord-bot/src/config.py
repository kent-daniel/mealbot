import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the Discord bot."""
    
    # Discord Bot Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Experience API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    API_ENDPOINT = os.getenv('API_ENDPOINT', '/api/process-video')
    API_KEY = os.getenv('API_KEY')  # Optional API key if needed
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))  # Timeout in seconds
    
    # Bot Behavior Configuration
    MAX_URLS_PER_MESSAGE = int(os.getenv('MAX_URLS_PER_MESSAGE', '3'))
    ENABLE_REACTIONS = os.getenv('ENABLE_REACTIONS', 'true').lower() == 'true'
    
    # Supported Platforms
    SUPPORTED_PLATFORMS = {
        'youtube': os.getenv('ENABLE_YOUTUBE', 'true').lower() == 'true',
        'instagram': os.getenv('ENABLE_INSTAGRAM', 'true').lower() == 'true',
        'tiktok': os.getenv('ENABLE_TIKTOK', 'true').lower() == 'true',
    }
    
    # Channel Configuration (optional)
    ALLOWED_CHANNELS = os.getenv('ALLOWED_CHANNELS', '').split(',') if os.getenv('ALLOWED_CHANNELS') else []
    BLOCKED_CHANNELS = os.getenv('BLOCKED_CHANNELS', '').split(',') if os.getenv('BLOCKED_CHANNELS') else []
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    @classmethod
    def validate(cls):
        """Validate required configuration values."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required")
        
        if not cls.API_BASE_URL:
            raise ValueError("API_BASE_URL is required")
        
        return True
    
    @classmethod
    def get_full_api_url(cls):
        """Get the complete API URL."""
        return f"{cls.API_BASE_URL.rstrip('/')}{cls.API_ENDPOINT}"
