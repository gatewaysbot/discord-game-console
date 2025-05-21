"""
Daily bonus implementation
"""
import random
import asyncio
import discord
import datetime
from discord.ext import commands
import config
from utils.pointsystem import PointSystem

class DailyBonus:
    def __init__(self, bot, point_system: PointSystem):
        self.bot = bot
        self.point_system = point_system
        self.cooldowns = {}  # {user_id: next_available_time}
        
    async def claim(self, ctx):
        """Claim daily bonus points"""
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user is on cooldown
        now = datetime.datetime.now()
        if user_id in self.cooldowns:
            next_available = self.cooldowns[user_id]
            if now < next_available:
                # User is on cooldown
                time_left = next_available - now
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                embed = discord.Embed(
                    title="⏳ Daily Bonus on Cooldown",
                    description=f"You've already claimed your daily bonus! Come back later.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Time until next claim",
                    value=f"{hours}h {minutes}m {seconds}s"
                )
                
                return await ctx.send(embed=embed)
        
        # Generate random bonus amount
        bonus = random.randint(config.DAILY_MIN, config.DAILY_MAX)
        
        # Add points to user
        self.point_system.add_points(user_id, username, "daily", bonus, won=True)
        
        # Set cooldown (24 hours from now)
        next_available = now + datetime.timedelta(days=1)
        self.cooldowns[user_id] = next_available
        
        # Create success embed
        embed = discord.Embed(
            title="💰 Daily Bonus Claimed!",
            description=f"You've received {bonus} points!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Current Balance",
            value=f"{self.point_system.get_points(user_id, username)} points"
        )
        embed.add_field(
            name="Next Claim",
            value=f"Available in 24 hours."
        )
        
        await ctx.send(embed=embed)