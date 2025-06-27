# ReelMeals Discord Bot

A Discord bot that automatically detects video URLs in messages and extracts recipe information using the ReelMeals Experience API.

## Features

- 🔍 **Auto URL Detection**: Automatically detects video URLs from YouTube, Instagram, and TikTok
- 🍽️ **Recipe Extraction**: Calls your Experience API to extract recipe data from videos
- 📱 **No Commands Needed**: Just paste a video link and get instant recipe extraction
- 🎨 **Rich Embeds**: Beautiful Discord embeds showing recipe details
- ⚡ **Real-time Reactions**: Visual feedback with emoji reactions
- 🛡️ **Error Handling**: Comprehensive error handling and user-friendly messages
- 🔧 **Configurable**: Extensive configuration options via environment variables

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- A Discord application and bot token
- Your Mealbot Experience API running
- uv package manager setup

### 2. Installation

```bash
# Clone or download the bot files
cd discord-bot

# Install dependencies
uv venv && uv pip install --system -e .

```

### 3. Configuration

Edit the `.env` file with your settings:

```env
# Required: Your Discord bot token
DISCORD_TOKEN=your_discord_bot_token_here

# Required: Your Experience API URL
API_BASE_URL=http://localhost:8000
API_ENDPOINT=/api/process-video

# Optional: API authentication
API_KEY=your_api_key_if_needed
```

### 4. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable these bot permissions:
   - Read Messages
   - Send Messages
   - Add Reactions
   - Embed Links
   - Use External Emojis
6. Invite the bot to your server using the OAuth2 URL generator

### 5. Run the Bot

```bash
python bot.py
```

## Docker Setup

### Build and Run with Docker Compose

```bash
# Start with docker-compose
docker-compose up mealbot

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## How It Works

1. **User pastes a video URL** in any Discord channel where the bot has access
2. **Bot detects the URL** automatically (no commands needed)
3. **Adds a 🔄 reaction** to show it's processing
4. **Calls your Experience API** with the video URL
5. **Displays the recipe** in a beautiful embed format
6. **Updates reaction** to ✅ for success or ❌ for errors

## Supported Platforms

- **YouTube**: youtube.com, youtu.be, youtube.com/shorts
- **Instagram**: instagram.com/reel, instagram.com/p, instagram.com/tv
- **TikTok**: tiktok.com, vm.tiktok.com

## Configuration Options

### Environment Variables

| Variable               | Default                 | Description                                 |
| ---------------------- | ----------------------- | ------------------------------------------- |
| `DISCORD_TOKEN`        | Required                | Your Discord bot token                      |
| `API_BASE_URL`         | `http://localhost:8000` | Base URL of your Experience API             |
| `API_ENDPOINT`         | `/api/process-video`    | API endpoint for video processing           |
| `API_KEY`              | None                    | Optional API key for authentication         |
| `API_TIMEOUT`          | `30`                    | API request timeout in seconds              |
| `MAX_URLS_PER_MESSAGE` | `3`                     | Maximum URLs to process per message         |
| `ENABLE_REACTIONS`     | `true`                  | Enable emoji reactions for feedback         |
| `ENABLE_YOUTUBE`       | `true`                  | Enable YouTube URL processing               |
| `ENABLE_INSTAGRAM`     | `true`                  | Enable Instagram URL processing             |
| `ENABLE_TIKTOK`        | `true`                  | Enable TikTok URL processing                |
| `ALLOWED_CHANNELS`     | None                    | Comma-separated list of allowed channel IDs |
| `BLOCKED_CHANNELS`     | None                    | Comma-separated list of blocked channel IDs |
| `LOG_LEVEL`            | `INFO`                  | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE`             | `bot.log`               | Log file path                               |

### Channel Restrictions

You can restrict the bot to specific channels:

```env
# Only process URLs in these channels
ALLOWED_CHANNELS=123456789,987654321

# Never process URLs in these channels
BLOCKED_CHANNELS=111111111,222222222
```

## Commands

- `!help` - Show help information
- `!status` - Show bot status

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if bot has proper permissions in the channel
2. **API errors**: Verify your API_BASE_URL and API_ENDPOINT are correct
3. **Missing reactions**: Ensure bot has "Add Reactions" permission
4. **No embeds**: Ensure bot has "Embed Links" permission
