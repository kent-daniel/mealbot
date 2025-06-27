import discord
import asyncio
from utils.url_detector import URLDetector
from api_client import ExperienceAPIClient
from utils.embeds import RecipeEmbedBuilder
from utils.logger import setup_logger
from config import Config

logger = setup_logger()

class URLProcessor:
    """Handles processing of messages containing video URLs."""
    
    def __init__(self):
        self.url_detector = URLDetector()
        self.api_client = ExperienceAPIClient()
        self.embed_builder = RecipeEmbedBuilder()
    
    async def process_message(self, message):
        """Process a Discord message for video URLs."""
        if not self._is_channel_allowed(message.channel):
            return
        
        urls = self.url_detector.extract_video_urls(message.content)
        
        if not urls:
            return
        
        if len(urls) > Config.MAX_URLS_PER_MESSAGE:
            urls = urls[:Config.MAX_URLS_PER_MESSAGE]
            await message.channel.send(
                f"⚠️ Too many URLs detected. Processing only the first {Config.MAX_URLS_PER_MESSAGE} URLs."
            )
        
        for url in urls:
            await self._process_single_url(message, url)
    
    async def _process_single_url(self, message, url):
        """Process a single video URL."""
        try:
            if Config.ENABLE_REACTIONS:
                await message.add_reaction("🔄")
            
            logger.info(f"Processing URL: {url}")
            
            # recipe_data = await self.api_client.process_video(url)
            
            # if recipe_data:
            #     embed = self.embed_builder.create_recipe_embed(recipe_data, url)
            #     await message.channel.send(embed=embed)
                
            #     # Update reaction to success
            #     if Config.ENABLE_REACTIONS:
            #         await message.remove_reaction("🔄", message.guild.me)
            #         await message.add_reaction("✅")
                
            #     logger.info(f"Successfully processed URL: {url}")
            # else:
            #     # Handle case where API returns no data
            #     await self._handle_processing_error(message, "No recipe data found in video")
        
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await self._handle_processing_error(message, str(e))
    
    async def _handle_processing_error(self, message, error_msg):
        """Handle errors during URL processing."""
        try:
            # Update reaction to error
            if Config.ENABLE_REACTIONS:
                await message.remove_reaction("🔄", message.guild.me)
                await message.add_reaction("❌")
            
            # Send error embed
            embed = self.embed_builder.create_error_embed(error_msg)
            await message.channel.send(embed=embed)
            
        except discord.errors.Forbidden:
            logger.warning("Cannot add reaction or send message - missing permissions")
        except Exception as e:
            logger.error(f"Error handling processing error: {e}")
    
    def _is_channel_allowed(self, channel):
        """Check if the channel is allowed for processing."""
        channel_id = str(channel.id)
        
        # Check blocked channels first
        if Config.BLOCKED_CHANNELS and channel_id in Config.BLOCKED_CHANNELS:
            return False
        
        # Check allowed channels (if specified)
        if Config.ALLOWED_CHANNELS and channel_id not in Config.ALLOWED_CHANNELS:
            return False
        
        return True
