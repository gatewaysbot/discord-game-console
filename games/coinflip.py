"""
Coin flip game implementation
"""
import random
import asyncio
import discord
from discord.ext import commands
import config
from utils.point_system import PointSystem

class CoinFlip:
    def __init__(self, bot, point_system: PointSystem):
        self.bot = bot
        self.point_system = point_system
        
    async def flip_coin(self, ctx, choice: str):
        """Flip a coin - user can choose 'heads' or 'tails'"""
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Validate user choice
        if choice.lower() not in ["heads", "tails"]:
            return await ctx.send(f"{ctx.author.mention}, please choose either 'heads' or 'tails'.")
        
        # Get multiplier and points
        multiplier = self.point_system.get_multiplier(user_id, username, "coinflip")
        streak = self.point_system.get_streak(user_id, username, "coinflip")
        
        # Build suspense
        flip_message = await ctx.send(f"🪙 Flipping a coin for {ctx.author.mention}...")
        await asyncio.sleep(1.5)
        
        # Determine result
        result = random.choice(["heads", "tails"])
        
        # Check if the user won
        won = choice.lower() == result
        
        # Prepare result emoji
        result_emoji = "🦅" if result == "heads" else "🪙"
        choice_emoji = "🦅" if choice.lower() == "heads" else "🪙"
        
        # Award points or reset streak
        if won:
            points, new_multiplier = self.point_system.add_points(
                user_id, 
                username, 
                "coinflip", 
                config.COINFLIP_POINTS,
                won=True
            )
            
            new_streak = self.point_system.get_streak(user_id, username, "coinflip")
            
            embed = discord.Embed(
                title=f"{result_emoji} Coin Flip: {result.upper()}",
                description=f"You chose {choice_emoji} **{choice.upper()}** and won!",
                color=discord.Color.green()
            )
            embed.add_field(name="Points Earned", value=f"+{points} points")
            embed.add_field(name="Streak", value=f"{new_streak} wins")
            embed.add_field(name="Multiplier", value=f"{new_multiplier:.2f}x")
            
        else:
            self.point_system.add_points(user_id, username, "coinflip", 0, won=False)
            
            embed = discord.Embed(
                title=f"{result_emoji} Coin Flip: {result.upper()}",
                description=f"You chose {choice_emoji} **{choice.upper()}** and lost!",
                color=discord.Color.red()
            )
            embed.add_field(name="Streak", value="Reset to 0")
            embed.add_field(name="Multiplier", value="1.0x")
            
        # Show current points
        embed.add_field(
            name="Current Points", 
            value=f"{self.point_system.get_points(user_id, username)} points",
            inline=False
        )
        
        await flip_message.edit(content="", embed=embed)
