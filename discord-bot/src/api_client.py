import aiohttp
import asyncio
import json
import os # Added for os.environ.get, though the function using it was removed
from typing import Optional, Dict, Any
import google.auth.transport.requests
import google.oauth2.id_token
from .utils.logger import setup_logger
from .config import Config

logger = setup_logger()

class ExperienceAPIClient:
    """Client for communicating with the Experience API."""

    def __init__(self):
        # Config should provide the full URL of the Cloud Run service, including 'https://'
        self.api_full_url = Config.API_BASE_URL
        self.timeout = Config.API_TIMEOUT
        self._session: Optional[aiohttp.ClientSession] = None # Initialize aiohttp session
        self._id_token: Optional[str] = None # To store the fetched ID token

    async def _get_authenticated_session(self) -> aiohttp.ClientSession:
        """
        Ensures an authenticated aiohttp session exists.
        Fetches a new ID token if one doesn't exist or if the session needs to be re-created.
        """
        # Check if the session needs to be created or re-created
        if self._session is None or self._session.closed:
            logger.info("Creating a new authenticated aiohttp session.")
            try:
                # The target audience for the ID token is the full URL of the Cloud Run service.
                # This call is synchronous, but typically fast and handled once per session creation.
                target_audience = self.api_full_url
                auth_req = google.auth.transport.requests.Request()
                self._id_token = google.oauth2.id_token.fetch_id_token(auth_req, target_audience)

                if not self._id_token:
                    raise Exception("Failed to fetch ID token for authentication.")

            except Exception as e:
                logger.error(f"Error fetching ID token: {e}", exc_info=True)
                raise 

            headers = {
                "Authorization": f"Bearer {self._id_token}",
                "Content-Type": "application/json" # Essential for JSON payloads
            }
            # Create a new aiohttp ClientSession with the authentication headers and timeout
            self._session = aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session

    async def _make_request(self, method: str, endpoint: str, payload: Optional[Dict[Any, Any]] = None, retry_count: int = 0) -> Optional[Dict[Any, Any]]:
        """
        Internal helper to make authenticated API requests with retry logic.
        """
        try:
            session = await self._get_authenticated_session()
            full_endpoint_url = f'{self.api_full_url.rstrip("/")}{endpoint}'
            logger.info(f"Sending {method} request to: {full_endpoint_url}")

            async with session.request(method, full_endpoint_url, json=payload) as response:
                logger.info(f"API response status: {response.status}")

                if response.status == 200:
                    return await response.json()
                elif response.status == 401 and retry_count == 0:
                    logger.warning("API token potentially expired (401). Attempting to refresh token and retry.")
                    await self.close() # Force session and token refresh
                    return await self._make_request(method, endpoint, payload, retry_count=1) # Retry once
                elif response.status == 400:
                    error_data = await response.text()
                    logger.warning(f"Bad request to API (400): {error_data}")
                    raise Exception(f"Invalid video URL or unsupported platform: {error_data}")
                elif response.status == 404:
                    logger.warning("API endpoint not found (404). Check API_FULL_URL and API_ENDPOINT.")
                    raise Exception("API service unavailable or endpoint not found.")
                elif response.status == 429:
                    logger.warning("API rate limit exceeded (429).")
                    raise Exception("Too many requests. Please try again later.")
                elif response.status >= 500:
                    error_text = await response.text()
                    logger.error(f"API server error ({response.status}): {error_text}")
                    raise Exception(f"API server error. Please try again later. Details: {error_text}")
                else:
                    error_text = await response.text()
                    logger.error(f"Unexpected API response {response.status}: {error_text}")
                    raise Exception(f"Unexpected API response: {response.status} - {error_text}")

        except aiohttp.ClientError as e:
            if isinstance(e, aiohttp.ClientTimeout):
                logger.error("API request timed out.")
                raise Exception("Request timed out. The video might be too long to process or the API is slow.")
            elif retry_count == 0:
                logger.warning(f"Network error during API request: {e}. Attempting to recreate session and retry.", exc_info=True)
                await self.close() # Force session recreation
                return await self._make_request(method, endpoint, payload, retry_count=1) # Retry once
            else:
                logger.error(f"Persistent network error during API request: {e}", exc_info=True)
                raise Exception(f"Network error. Please check your connection. Details: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from API: {e}", exc_info=True)
            raise Exception("Invalid response from API: Expected JSON but received malformed data.")
        except Exception as e:
            logger.error(f"An unexpected error occurred in API client: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred during API call: {e}")

    async def process_video(self, video_url: str) -> Optional[Dict[Any, Any]]:
        """
        Sends a video URL to the Experience API for processing.
        """
        payload = {
            "video_url": video_url,
            "source": "discord_bot"
        }
        return await self._make_request("POST", Config.API_ENDPOINT, payload)

    async def health_check(self) -> bool:
        """
        Performs a health check on the Experience API.
        """
        try:
            # The health check endpoint is typically just '/' or '/health' relative to the base URL
            # We'll use '/' as per the API's health check handler in main.py
            response_data = await self._make_request("GET", "/health")
            return response_data is not None # If request succeeds, it's healthy
        except Exception as e:
            logger.error(f"Health check failed due to exception: {e}", exc_info=True)
            return False

    async def close(self):
        """Closes the aiohttp session if it's open."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            logger.info("aiohttp session closed.")
