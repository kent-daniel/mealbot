import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any
from config import Config
from utils.logger import setup_logger
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token
from google.auth.transport.aiohttp_requests import AuthorizedSession # This is key for aiohttp integration


logger = setup_logger()

class ExperienceAPIClient:
    """Client for communicating with the Experience API."""
    
    def __init__(self):
        # Config should provide the full URL of the Cloud Run service, including 'https://'
        # Example: Config.API_FULL_URL = "https://your-experience-api-xxxxxxx-uc.a.run.app"
        self.api_full_url = Config.API_FULL_URL
        self.timeout = Config.API_TIMEOUT
        self._session: Optional[aiohttp.ClientSession] = None
        self._credentials = None
        self._target_audience = self.api_full_url # For Cloud Run, the audience is typically the service URL

    async def _get_authenticated_session(self) -> aiohttp.ClientSession:
        """
        Lazily gets or creates an aiohttp session authenticated for Google Cloud Run.
        This leverages google-auth's AuthorizedSession for automatic ID token handling.
        """
        if self._session is None or self._session.closed:
            # Discover credentials automatically (from metadata server on GCP, or GOOGLE_APPLICATION_CREDENTIALS)
            self._credentials, project = await asyncio.to_thread(google.auth.default)

            if not self._credentials:
                logger.error("Could not obtain Google Cloud credentials.")
                raise Exception("Google Cloud credentials not found. Ensure running on GCP or GOOGLE_APPLICATION_CREDENTIALS is set.")

            # AuthorizedSession handles fetching and refreshing ID tokens
            # and adding the 'Authorization: Bearer <ID_TOKEN>' header.
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = AuthorizedSession(
                credentials=self._credentials,
                # The target_audience is crucial for Cloud Run
                # The Cloud Run service will validate that the token's audience matches its own URL.
                audience=self._target_audience,
                timeout=timeout
            )
        return self._session


    async def process_video(self, video_url: str) -> Optional[Dict[Any, Any]]:
        try:
            session = await self._get_authenticated_session()
            
            payload = {
                "video_url": video_url,
                "source": "discord_bot"
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ReelMeals-Discord-Bot/1.0"
            }
            
            
            full_url = Config.get_full_api_url()
            logger.info(f"Sending request to: {full_url}")
            
            async with session.post(
                f'{self.api_full_url}{Config.API_ENDPOINT}',
                json=payload,
                headers=headers
            ) as response:
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
            session = await self._get_authenticated_session()
            health_url = f"{self.base_url.rstrip('/')}/health"
            
            async with session.get(health_url) as response:
                return response.status == 200
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """Closes the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None