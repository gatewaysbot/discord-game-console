"""
Discord Game Console Bot - Main Entry Point
Handles bot initialization and command routing
"""
import logging
import discord
from discord.ext import commands
from config import BotConfig, GameSettings, ErrorMessages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord-game-console')

class GameConsoleBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=BotConfig.PREFIX,
            intents=intents,
            help_command=None
        )
        
        # Initialize game components
        self._init_games()
        
    async def setup_hook(self):
        """Initialize async components"""
        # Load game cogs here
        pass
        
    def _init_games(self):
        """Initialize game components"""
        # Initialize game instances here
        pass
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'Bot is ready as {self.user.name}')
        
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
            
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
            return
            
        logger.error(f'Error in {ctx.command}: {error}')
        await ctx.send(f"An error occurred: {str(error)}")

def main():
    """Main entry point"""
    if not BotConfig.TOKEN or BotConfig.TOKEN.strip() == "":
        logger.error("Bot token is not configured! Please set a valid token in your configuration.")
        return
        
    bot = GameConsoleBot()
    
    @bot.command(name='help')
    async def help_cmd(ctx):
        """Show help message"""
        embed = discord.Embed(
            title="🎮 Game Commands",
            description="Available commands:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Games",
            value=f"`{BotConfig.PREFIX}guess start` - Number guessing game\n"
                  f"`{BotConfig.PREFIX}trivia` - Trivia game\n"
                  f"`{BotConfig.PREFIX}coinflip <heads/tails>` - Flip a coin\n"
                  f"`{BotConfig.PREFIX}slots <bet>` - Play slots\n"
                  f"`{BotConfig.PREFIX}roulette <prediction> <bet>` - Play roulette\n"
                  f"`{BotConfig.PREFIX}blackjack <bet>` - Play blackjack",
            inline=False
        )
        
        embed.add_field(
            name="Points",
            value=f"`{BotConfig.PREFIX}daily` - Claim daily bonus\n"
                  f"`{BotConfig.PREFIX}points` - Check your points\n"
                  f"`{BotConfig.PREFIX}leaderboard` - View top players",
            inline=False
        )
        
        await ctx.send(embed=embed)

    try:
        bot.run(BotConfig.TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Failed to login: Invalid bot token. Please check your configuration.")
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")

if __name__ == '__main__':
    main()
