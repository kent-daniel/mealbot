import aiohttp
import asyncio
import json
import os # Added for os.environ.get, though the function using it was removed
from typing import Optional, Dict, Any
import google.auth.transport.requests
import google.oauth2.id_token

logger = setup_logger()

class ExperienceAPIClient:
    """Client for communicating with the Experience API."""

    def __init__(self):
        # Config should provide the full URL of the Cloud Run service, including 'https://'
        self.api_full_url = Config.API_FULL_URL
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

    async def process_video(self, video_url: str) -> Optional[Dict[Any, Any]]:
        """
        Sends a video URL to the Experience API for processing.
        """
        try:
            # Get an authenticated aiohttp session
            session = await self._get_authenticated_session()

            payload = {
                "video_url": video_url,
                "source": "discord_bot"
            }

            # Construct the full URL for the API endpoint
            # rstrip('/') ensures no double slashes if API_FULL_URL ends with one
            full_endpoint_url = f'{self.api_full_url.rstrip("/")}{Config.API_ENDPOINT}'
            logger.info(f"Sending request to: {full_endpoint_url} with video_url: {video_url}")

            # Make the POST request
            async with session.post(
                full_endpoint_url,
                json=payload # aiohttp handles setting Content-Type: application/json when 'json' argument is used
            ) as response:
                # Log response status for debugging
                logger.info(f"API response status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    logger.info("Successfully received recipe data from API")
                    return data

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

        except aiohttp.ClientTimeout:
            logger.error("API request timed out.")
            raise Exception("Request timed out. The video might be too long to process or the API is slow.")

        except aiohttp.ClientError as e:
            logger.error(f"Network error during API request: {e}", exc_info=True)
            raise Exception(f"Network error. Please check your connection. Details: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from API: {e}", exc_info=True)
            raise Exception("Invalid response from API: Expected JSON but received malformed data.")

        except Exception as e:
            # Catch any other unexpected exceptions and log them with traceback
            logger.error(f"An unexpected error occurred in API client: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred during video processing: {e}")

    async def health_check(self) -> bool:
        """
        Performs a health check on the Experience API.
        """
        try:
            session = await self._get_authenticated_session()
            # Construct the health check URL using the base API URL
            health_url = f"{self.api_full_url.rstrip('/')}/health"
            logger.info(f"Performing health check on: {health_url}")

            async with session.get(health_url) as response:
                status_ok = response.status == 200
                if not status_ok:
                    logger.warning(f"Health check failed with status: {response.status}")
                else:
                    logger.info("Health check successful (status 200).")
                return status_ok

        except Exception as e:
            logger.error(f"Health check failed due to exception: {e}", exc_info=True)
            return False

    async def close(self):
        """Closes the aiohttp session if it's open."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            logger.info("aiohttp session closed.")