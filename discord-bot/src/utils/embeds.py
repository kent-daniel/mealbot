import discord
from datetime import datetime
from typing import Dict, Any, Optional

class RecipeEmbedBuilder:
    """Builds Discord embeds for recipe data and other responses."""
    
    def __init__(self):
        self.colors = {
            'success': 0x00ff00,
            'error': 0xff0000,
            'warning': 0xffaa00,
            'info': 0x0099ff,
            'recipe': 0xff6b6b
        }
    
    def create_recipe_embed(self, recipe_data: Dict[Any, Any], video_url: str) -> discord.Embed:
        """
        Create a rich embed for recipe data.
        
        Args:
            recipe_data: Recipe data from the API
            video_url: Original video URL
            
        Returns:
            Discord embed with recipe information
        """
        # Extract recipe information (adjust based on your API response structure)
        title = recipe_data.get('title', 'Recipe from Video')
        description = recipe_data.get('description', 'Recipe extracted from video')
        ingredients = recipe_data.get('ingredients', [])
        instructions = recipe_data.get('instructions', [])
        prep_time = recipe_data.get('prep_time')
        cook_time = recipe_data.get('cook_time')
        servings = recipe_data.get('servings')
        cuisine = recipe_data.get('cuisine')
        difficulty = recipe_data.get('difficulty')
        
        # Create embed
        embed = discord.Embed(
            title=f"🍽️ {title}",
            description=description,
            color=self.colors['recipe'],
            timestamp=datetime.utcnow()
        )
        
        # Add video URL
        embed.add_field(
            name="📹 Original Video",
            value=f"[Watch Video]({video_url})",
            inline=False
        )
        
        # Add recipe details
        details = []
        if prep_time:
            details.append(f"⏱️ Prep: {prep_time}")
        if cook_time:
            details.append(f"🔥 Cook: {cook_time}")
        if servings:
            details.append(f"👥 Serves: {servings}")
        if difficulty:
            details.append(f"📊 Difficulty: {difficulty}")
        if cuisine:
            details.append(f"🌍 Cuisine: {cuisine}")
        
        if details:
            embed.add_field(
                name="📋 Details",
                value=" • ".join(details),
                inline=False
            )
        
        # Add ingredients
        if ingredients:
            ingredients_text = self._format_ingredients(ingredients)
            embed.add_field(
                name="🛒 Ingredients",
                value=ingredients_text,
                inline=False
            )
        
        # Add instructions
        if instructions:
            instructions_text = self._format_instructions(instructions)
            embed.add_field(
                name="👨‍🍳 Instructions",
                value=instructions_text,
                inline=False
            )
        
        # Add footer
        embed.set_footer(
            text="ReelMeals • Turn Reel Inspiration into Real Meals",
            icon_url="https://cdn.discordapp.com/emojis/🍽️.png"
        )
        
        return embed
    
    def create_error_embed(self, error_message: str) -> discord.Embed:
        """
        Create an error embed.
        
        Args:
            error_message: Error message to display
            
        Returns:
            Discord embed with error information
        """
        embed = discord.Embed(
            title="❌ Processing Error",
            description=error_message,
            color=self.colors['error'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="💡 Suggestions",
            value="• Make sure the video contains a recipe\n• Check if the URL is valid\n• Try a different video platform",
            inline=False
        )
        
        embed.set_footer(text="ReelMeals Bot")
        
        return embed
    
    def create_processing_embed(self, video_url: str) -> discord.Embed:
        """
        Create a processing embed.
        
        Args:
            video_url: Video URL being processed
            
        Returns:
            Discord embed showing processing status
        """
        embed = discord.Embed(
            title="🔄 Processing Video",
            description="Extracting recipe from video... This may take a moment.",
            color=self.colors['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📹 Video URL",
            value=f"[Processing...]({video_url})",
            inline=False
        )
        
        embed.set_footer(text="ReelMeals Bot")
        
        return embed
    
    def _format_ingredients(self, ingredients) -> str:
        """Format ingredients list for display."""
        if isinstance(ingredients, list):
            if len(ingredients) > 10:
                # Truncate long ingredient lists
                formatted = "\n".join([f"• {ingredient}" for ingredient in ingredients[:10]])
                formatted += f"\n... and {len(ingredients) - 10} more ingredients"
            else:
                formatted = "\n".join([f"• {ingredient}" for ingredient in ingredients])
        else:
            formatted = str(ingredients)
        
        # Ensure it doesn't exceed Discord's field value limit (1024 characters)
        if len(formatted) > 1000:
            formatted = formatted[:997] + "..."
        
        return formatted
    
    def _format_instructions(self, instructions) -> str:
        """Format instructions list for display."""
        if isinstance(instructions, list):
            if len(instructions) > 8:
                # Truncate long instruction lists
                formatted = "\n".join([f"{i+1}. {instruction}" for i, instruction in enumerate(instructions[:8])])
                formatted += f"\n... and {len(instructions) - 8} more steps"
            else:
                formatted = "\n".join([f"{i+1}. {instruction}" for i, instruction in enumerate(instructions)])
        else:
            formatted = str(instructions)
        
        # Ensure it doesn't exceed Discord's field value limit (1024 characters)
        if len(formatted) > 1000:
            formatted = formatted[:997] + "..."
        
        return formatted
    
    def create_help_embed(self) -> discord.Embed:
        """Create a help embed."""
        embed = discord.Embed(
            title="🍽️ ReelMeals Bot Help",
            description="I automatically detect and process recipe videos!",
            color=self.colors['info']
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
        
        embed.set_footer(text="ReelMeals - Turn Reel Inspiration into Real Meals")
        
        return embed
