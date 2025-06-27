import discord
from discord.ext import commands
import asyncio
import logging
from config import Config
from url_processor import URLProcessor
from utils.logger import setup_logger

# Setup logging
logger = setup_logger()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.dm_messages = True
intents.dm_reactions = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
url_processor = URLProcessor()

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Set bot status
    activity = discord.Activity(type=discord.ActivityType.watching, name="for recipe links 🍽️")
    await bot.change_presence(activity=activity)
    
    # Sync commands globally for user installs and DMs
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} command(s) globally')
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    """Handle incoming messages and detect video URLs."""
    if message.author == bot.user:
        return
    
    if message.author.bot:
        return
    
    try:
        await url_processor.process_message(message)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        try:
            await message.add_reaction("❌")
        except discord.errors.Forbidden:
            logger.warning("Cannot add reaction - missing permissions")
    
    await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    """Handle bot errors."""
    logger.error(f"An error occurred in event {event}: {args}, {kwargs}")

@bot.command(name='help')
async def help_command(ctx):
    """Display help information."""
    embed = discord.Embed(
        title="🍽️ ReelMeals Bot Help",
        description="I automatically detect and process recipe videos!",
        color=0x00ff00
    )
    
    embed.add_field(
        name="How to use:",
        value="Just paste any video link from YouTube, Instagram, or TikTok and I'll extract the recipe for you!",
        inline=False
    )
    
    embed.add_field(
        name="Supported platforms:",
        value="• YouTube (youtube.com, youtu.be)\n• Instagram (instagram.com)\n• TikTok (tiktok.com)",
        inline=False
    )
    
    embed.add_field(
        name="Reactions:",
        value="🔄 Processing your video\n✅ Recipe extracted successfully\n❌ Error occurred",
        inline=False
    )
    
    if isinstance(ctx.channel, discord.DMChannel):
        embed.add_field(
            name="💬 DM Usage:",
            value="You can send me links directly here in DMs! No need for commands.",
            inline=False
        )
    
    embed.set_footer(text="ReelMeals - Turn Reel Inspiration into Real Meals")
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status_command(ctx):
    """Display bot status information."""
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=0x0099ff
    )
    
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="API Status", value="🟢 Connected", inline=True)
    
    await ctx.send(embed=embed)

def main():
    """Main function to run the bot."""
    try:
        # Validate configuration before starting
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Log bot configuration
        logger.info(f"Bot intents: {intents}")
        logger.info(f"API URL: {Config.get_full_api_url()}")
        logger.info(f"Log level: {Config.LOG_LEVEL}")
        
        logger.info("Starting ReelMeals Discord Bot...")
        bot.run(Config.DISCORD_TOKEN)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}")
    except discord.LoginFailure:
        logger.error("Invalid Discord token provided")
        print("Invalid Discord token provided")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"Failed to start bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
