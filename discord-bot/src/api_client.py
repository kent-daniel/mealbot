import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any
from config import Config
from utils.logger import setup_logger

logger = setup_logger()

class ExperienceAPIClient:
    """Client for communicating with the Experience API."""
    
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.endpoint = Config.API_ENDPOINT
        self.timeout = Config.API_TIMEOUT
        self.session = None
    
    async def _get_session(self):
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def process_video(self, video_url: str) -> Optional[Dict[Any, Any]]:
        try:
            session = await self._get_session()
            
            payload = {
                "video_url": video_url,
                "source": "discord_bot"
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ReelMeals-Discord-Bot/1.0"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                # Alternative: headers["X-API-Key"] = self.api_key
            
            full_url = Config.get_full_api_url()
            logger.info(f"Sending request to: {full_url}")
            
            async with session.post(f'{full_url}/', json=payload, headers=headers) as response:
                # Log response status
                logger.info(f"API response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info("Successfully received recipe data from API")
                    return data
                
                elif response.status == 400:
                    error_data = await response.text()
                    logger.warning(f"Bad request to API: {error_data}")
                    raise Exception("Invalid video URL or unsupported platform")
                
                elif response.status == 404:
                    logger.warning("API endpoint not found")
                    raise Exception("API service unavailable")
                
                elif response.status == 429:
                    logger.warning("API rate limit exceeded")
                    raise Exception("Too many requests. Please try again later.")
                
                elif response.status >= 500:
                    logger.error(f"API server error: {response.status}")
                    raise Exception("API server error. Please try again later.")
                
                else:
                    error_text = await response.text()
                    logger.error(f"Unexpected API response {response.status}: {error_text}")
                    raise Exception(f"Unexpected API response: {response.status}")
        
        except aiohttp.ClientTimeout:
            logger.error("API request timed out")
            raise Exception("Request timed out. The video might be too long to process.")
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise Exception("Network error. Please check your connection.")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise Exception("Invalid response from API")
        
        except Exception as e:
            logger.error(f"Unexpected error in API client: {e}")
            raise
    
    async def health_check(self) -> bool:
        try:
            session = await self._get_session()
            health_url = f"{self.base_url.rstrip('/')}/health"
            
            async with session.get(health_url) as response:
                return response.status == 200
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if self.session and not self.session.closed:
            # Note: This is not ideal for async cleanup, but serves as a fallback
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except:
                pass
