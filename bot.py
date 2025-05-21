"""
Main file for the Discord bot with games and point system
"""
import os
import random
import logging
import discord
from discord.ext import commands
import asyncio

# Import config and game modules
import config
from games.number_guess import NumberGuess
from games.trivia import Trivia
from games.coinflip import CoinFlip
from utils.point_system import PointSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_games_bot')

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for command detection
intents.members = True  # Enable members intent for user information

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, help_command=None)

# Initialize the point system
point_system = PointSystem()

# Initialize games
number_guess = NumberGuess(bot, point_system)
trivia = Trivia(bot, point_system)
coinflip = CoinFlip(bot, point_system)

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord"""
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} guilds')
    
    # Set bot status
    activity = discord.Game(name=f"{config.PREFIX}help | Games & Points")
    await bot.change_presence(activity=activity)
    
    logger.info("Bot is ready!")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"⚠️ Invalid argument: {error}")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ An error occurred: {error}")

# Help command
@bot.command(name="help")
async def help_command(ctx):
    """Display help information"""
    embed = discord.Embed(
        title="🎮 Game Bot Help",
        description="A bot with various games and a point system!",
        color=discord.Color.blue()
    )
    
    # Add command sections
    embed.add_field(
        name="🔢 Number Guessing Game",
        value=f"`{config.PREFIX}guess start` - Start a new guessing game\n"
              f"`{config.PREFIX}guess [number]` - Make a guess",
        inline=False
    )
    
    embed.add_field(
        name="🧠 Trivia Game",
        value=f"`{config.PREFIX}trivia` - Get a random trivia question",
        inline=False
    )
    
    embed.add_field(
        name="🪙 Coin Flip Game",
        value=f"`{config.PREFIX}coinflip [heads/tails]` - Flip a coin and bet on the outcome",
        inline=False
    )
    
    embed.add_field(
        name="📊 Points & Stats",
        value=f"`{config.PREFIX}points` - Check your points\n"
              f"`{config.PREFIX}leaderboard` - View the top players",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Other Commands",
        value=f"`{config.PREFIX}help` - Show this help message",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Number guessing game commands
@bot.command(name="guess")
async def guess_command(ctx, guess=None):
    """Command for the number guessing game"""
    if guess is None or guess.lower() == "start":
        await number_guess.start_game(ctx)
    else:
        try:
            guess_number = int(guess)
            await number_guess.make_guess(ctx, guess_number)
        except ValueError:
            await ctx.send(f"⚠️ Please provide a valid number between {config.GUESS_MIN} and {config.GUESS_MAX}!")

# Trivia game command
@bot.command(name="trivia")
async def trivia_command(ctx):
    """Start a trivia game"""
    await trivia.start_game(ctx)

# Coin flip game command
@bot.command(name="coinflip", aliases=["coin", "flip"])
async def coinflip_command(ctx, choice=None):
    """Flip a coin with a bet on heads or tails"""
    if choice is None:
        await ctx.send(f"⚠️ Please specify 'heads' or 'tails'! Example: `{config.PREFIX}coinflip heads`")
    else:
        await coinflip.flip_coin(ctx, choice)

# Points command
@bot.command(name="points", aliases=["score"])
async def points_command(ctx, member: discord.Member = None):
    """Check a user's points"""
    if member is None:
        member = ctx.author
        
    user_id = str(member.id)
    username = member.name
    
    points = point_system.get_points(user_id, username)
    
    # Get game-specific stats
    guess_streak = point_system.get_streak(user_id, username, "guess")
    guess_multiplier = point_system.get_multiplier(user_id, username, "guess")
    
    trivia_streak = point_system.get_streak(user_id, username, "trivia")
    trivia_multiplier = point_system.get_multiplier(user_id, username, "trivia")
    
    coinflip_streak = point_system.get_streak(user_id, username, "coinflip")
    coinflip_multiplier = point_system.get_multiplier(user_id, username, "coinflip")
    
    embed = discord.Embed(
        title=f"📊 Points for {member.name}",
        description=f"**Total Points:** {points}",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="🔢 Number Guessing Stats",
        value=f"Streak: {guess_streak} wins\nMultiplier: {guess_multiplier:.2f}x",
        inline=True
    )
    
    embed.add_field(
        name="🧠 Trivia Stats",
        value=f"Streak: {trivia_streak} correct\nMultiplier: {trivia_multiplier:.2f}x",
        inline=True
    )
    
    embed.add_field(
        name="🪙 Coin Flip Stats",
        value=f"Streak: {coinflip_streak} wins\nMultiplier: {coinflip_multiplier:.2f}x",
        inline=True
    )
    
    await ctx.send(embed=embed)

# Leaderboard command
@bot.command(name="leaderboard", aliases=["top", "lb"])
async def leaderboard_command(ctx, limit: int = 10):
    """Show the point leaderboard"""
    if limit < 1:
        limit = 10
    elif limit > 25:
        limit = 25  # Cap at 25 to avoid too long messages
        
    leaderboard = point_system.get_leaderboard(limit=limit)
    
    if not leaderboard:
        return await ctx.send("No players on the leaderboard yet! Start playing games to earn points.")
    
    embed = discord.Embed(
        title="🏆 Points Leaderboard",
        description="Top players ranked by points",
        color=discord.Color.gold()
    )
    
    # Format leaderboard entries
    leaderboard_text = ""
    for entry in leaderboard:
        if entry["rank"] == 1:
            prefix = "🥇"
        elif entry["rank"] == 2:
            prefix = "🥈"
        elif entry["rank"] == 3:
            prefix = "🥉"
        else:
            prefix = f"#{entry['rank']}"
            
        leaderboard_text += f"{prefix} **{entry['username']}**: {entry['points']} points\n"
    
    embed.add_field(name="Rankings", value=leaderboard_text if leaderboard_text else "No players yet!", inline=False)
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = config.TOKEN
    if not token:
        logger.error("No bot token provided. Please set the DISCORD_BOT_TOKEN environment variable.")
        exit(1)
        
    bot.run(token)
