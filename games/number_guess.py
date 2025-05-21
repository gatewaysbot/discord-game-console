"""
Number guessing game implementation
"""
import random
import asyncio
import discord
from discord.ext import commands
import config
from utils.point_system import PointSystem

class NumberGuess:
    def __init__(self, bot, point_system: PointSystem):
        self.bot = bot
        self.point_system = point_system
        self.active_games = {}  # {channel_id: {user_id: {number: int, attempts: int}}}
        
    async def start_game(self, ctx):
        """Start a new number guessing game for a user"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user already has an active game
        if channel_id in self.active_games and user_id in self.active_games[channel_id]:
            return await ctx.send(f"{ctx.author.mention}, you already have an active guessing game! "
                                  f"Use `!guess [number]` to make a guess.")
        
        # Initialize channel if needed
        if channel_id not in self.active_games:
            self.active_games[channel_id] = {}
            
        # Generate random number and setup game
        target_number = random.randint(config.GUESS_MIN, config.GUESS_MAX)
        self.active_games[channel_id][user_id] = {
            "number": target_number,
            "attempts": 0
        }
        
        # Get current multiplier
        multiplier = self.point_system.get_multiplier(user_id, username, "guess")
        streak = self.point_system.get_streak(user_id, username, "guess")
        
        embed = discord.Embed(
            title="🔢 Number Guessing Game",
            description=f"I'm thinking of a number between {config.GUESS_MIN} and {config.GUESS_MAX}.\n"
                        f"You have {config.GUESS_ATTEMPTS} attempts to guess it!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Current Streak", value=f"{streak} wins")
        embed.add_field(name="Current Multiplier", value=f"{multiplier:.2f}x")
        embed.add_field(name="Possible Points", value=f"{int(config.GUESS_POINTS * multiplier)}")
        embed.add_field(name="Command", value=f"Use `!guess [number]` to make a guess", inline=False)
        
        await ctx.send(embed=embed)
        
    async def make_guess(self, ctx, number: int):
        """Process a guess for the number guessing game"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user has an active game
        if channel_id not in self.active_games or user_id not in self.active_games[channel_id]:
            return await ctx.send(f"{ctx.author.mention}, you don't have an active guessing game! "
                                  f"Use `!guess start` to start a new game.")
        
        game = self.active_games[channel_id][user_id]
        target = game["number"]
        game["attempts"] += 1
        
        # Check if the guess is correct
        if number == target:
            # Award points
            points, multiplier = self.point_system.add_points(
                user_id, 
                username, 
                "guess", 
                config.GUESS_POINTS,
                won=True
            )
            
            new_streak = self.point_system.get_streak(user_id, username, "guess")
            new_multiplier = self.point_system.get_multiplier(user_id, username, "guess")
            
            embed = discord.Embed(
                title="🎉 Correct Guess!",
                description=f"Congratulations! {target} is the correct number!",
                color=discord.Color.green()
            )
            embed.add_field(name="Attempts Used", value=f"{game['attempts']}/{config.GUESS_ATTEMPTS}")
            embed.add_field(name="Points Earned", value=f"+{points} points")
            embed.add_field(name="New Streak", value=f"{new_streak} wins")
            embed.add_field(name="Next Multiplier", value=f"{new_multiplier:.2f}x")
            
            await ctx.send(embed=embed)
            
            # Remove the game
            del self.active_games[channel_id][user_id]
            return
            
        # Check if the player has used all attempts
        if game["attempts"] >= config.GUESS_ATTEMPTS:
            # Game over, no points
            self.point_system.add_points(
                user_id, 
                username, 
                "guess", 
                0,  # No points awarded
                won=False
            )
            
            embed = discord.Embed(
                title="❌ Game Over",
                description=f"Sorry, you've used all your attempts! The number was {target}.",
                color=discord.Color.red()
            )
            embed.add_field(name="Streak Reset", value="Your streak has been reset to 0")
            embed.add_field(name="Next Multiplier", value="1.0x")
            
            await ctx.send(embed=embed)
            
            # Remove the game
            del self.active_games[channel_id][user_id]
            return
            
        # Provide a hint
        hint = "higher" if target > number else "lower"
        remaining = config.GUESS_ATTEMPTS - game["attempts"]
        
        await ctx.send(f"{ctx.author.mention}, the number is {hint} than {number}. "
                       f"You have {remaining} attempts remaining.")
