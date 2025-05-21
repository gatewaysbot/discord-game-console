"""
Roulette game implementation
"""
import random
import asyncio
import discord
from discord.ext import commands
import config
from utils.pointsystem import PointSystem

class Roulette:
    def __init__(self, bot, point_system: PointSystem):
        self.bot = bot
        self.point_system = point_system
        self.wheel = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        self.payouts = config.ROULETTE_PAYOUTS

    async def play(self, ctx, prediction, bet_str):
        """Play roulette with a bet on a specific outcome"""
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Parse and validate bet
        bet = self._parse_bet_amount(bet_str, user_id, username)
        if bet is None:
            return await ctx.send(f"{ctx.author.mention}, please provide a valid bet amount between "
                                f"{config.ROULETTE_MIN_BET} and {config.ROULETTE_MAX_BET}.")
        
        # Check if user has enough points
        user_points = self.point_system.get_points(user_id, username)
        if bet > user_points:
            return await ctx.send(f"{ctx.author.mention}, you don't have enough points for that bet! "
                                f"You have {user_points} points.")
                                
        # Validate and process prediction
        valid_prediction, prediction_type, formatted_prediction = self._validate_prediction(prediction)
        if not valid_prediction:
            return await ctx.send(f"{ctx.author.mention}, invalid prediction! Please use a valid number (0-36), "
                               f"color (red/black), or other valid bet type (even/odd, high/low).")
        
        # Create initial spinning message
        embed = discord.Embed(
            title="🎲 Roulette Wheel Spinning...",
            description="The ball is rolling...",
            color=discord.Color.gold()
        )
        embed.add_field(name="Your Bet", value=f"{bet} points on {formatted_prediction}")
        message = await ctx.send(embed=embed)
        
        # Simulate wheel spinning
        await self._animate_wheel_spin(message)
        
        # Generate result
        result = random.choice(self.wheel)
        
        # Determine if player won
        win, multiplier = self._check_win(result, prediction_type, prediction)
        
        # Format result data for display
        result_color = "🔴" if result in self.red_numbers else "⚫" if result in self.black_numbers else "🟢"
        result_text = f"{result_color} {result}"
        
        # Update points
        if win:
            win_amount = bet * (multiplier + 1)  # Include original bet
            self.point_system.add_points(user_id, username, "roulette", win_amount - bet, won=True)
            result_message = f"🎉 You won {win_amount - bet} points! ({multiplier}:1)"
            color = discord.Color.green()
        else:
            self.point_system.add_points(user_id, username, "roulette", -bet, won=False)
            result_message = "❌ You lost your bet!"
            color = discord.Color.red()
        
        # Create final result embed
        embed = discord.Embed(
            title="🎲 Roulette Results",
            description=f"The ball landed on: {result_text}",
            color=color
        )
        embed.add_field(name="Your Bet", value=f"{bet} points on {formatted_prediction}", inline=False)
        embed.add_field(name="Result", value=result_message, inline=False)
        embed.add_field(name="Current Points", value=f"{self.point_system.get_points(user_id, username)} points")
        
        await message.edit(embed=embed)
    
    def _parse_bet_amount(self, bet_str, user_id, username):
        """Parse the bet amount from string input"""
        # Check for 'max' or 'm' bet
        if bet_str.lower() in ['max', 'm', 'all', 'a']:
            bet = min(self.point_system.get_points(user_id, username), config.ROULETTE_MAX_BET)
            return bet
            
        # Try to convert to integer
        try:
            bet = int(bet_str)
            
            # Check if bet is within allowed range
            if bet < config.ROULETTE_MIN_BET:
                return None
            if bet > config.ROULETTE_MAX_BET:
                bet = config.ROULETTE_MAX_BET
                
            return bet
        except ValueError:
            return None
    
    def _validate_prediction(self, prediction):
        """Validate the user's prediction and return formatted prediction"""
        # Handle number bets (0-36)
        try:
            num = int(prediction)
            if 0 <= num <= 36:
                return True, "number", f"Number {num}"
        except ValueError:
            pass
            
        # Handle color bets
        prediction = prediction.lower()
        if prediction in ["red", "r"]:
            return True, "red", "Red"
        elif prediction in ["black", "b"]:
            return True, "black", "Black"
            
        # Handle even/odd bets
        elif prediction in ["even", "e"]:
            return True, "even", "Even"
        elif prediction in ["odd", "o"]:
            return True, "odd", "Odd"
            
        # Handle high/low bets
        elif prediction in ["high", "h"]:
            return True, "high", "High (19-36)"
        elif prediction in ["low", "l"]:
            return True, "low", "Low (1-18)"
            
        # Handle dozen bets
        elif prediction in ["1st dozen", "1st", "first dozen", "1-12"]:
            return True, "dozen1", "1st Dozen (1-12)"
        elif prediction in ["2nd dozen", "2nd", "second dozen", "13-24"]:
            return True, "dozen2", "2nd Dozen (13-24)"
        elif prediction in ["3rd dozen", "3rd", "third dozen", "25-36"]:
            return True, "dozen3", "3rd Dozen (25-36)"
            
        # Invalid prediction
        return False, None, None
            
    async def _animate_wheel_spin(self, message):
        """Animate the roulette wheel spinning"""
        for _ in range(3):  # Spin animation stages
            # Randomly select numbers for animation
            spin_result = random.choice(self.wheel)
            color = "🔴" if spin_result in self.red_numbers else "⚫" if spin_result in self.black_numbers else "🟢"
            
            # Update the embed
            embed = message.embeds[0]
            embed.description = f"The ball is rolling... {color} {spin_result}"
            await message.edit(embed=embed)
            
            # Delay between animations
            await asyncio.sleep(1)
    
    def _check_win(self, result, prediction_type, prediction):
        """Check if the player won based on their prediction"""
        if prediction_type == "number":
            # Direct number bet
            if int(prediction) == result:
                return True, self.payouts["number"]
                
        elif prediction_type == "red":
            # Red bet
            if result in self.red_numbers:
                return True, self.payouts["red"]
                
        elif prediction_type == "black":
            # Black bet
            if result in self.black_numbers:
                return True, self.payouts["black"]
                
        elif prediction_type == "even":
            # Even bet (0 is neither even nor odd)
            if result != 0 and result % 2 == 0:
                return True, self.payouts["even"]
                
        elif prediction_type == "odd":
            # Odd bet
            if result != 0 and result % 2 == 1:
                return True, self.payouts["odd"]
                
        elif prediction_type == "high":
            # High bet (19-36)
            if 19 <= result <= 36:
                return True, self.payouts["high"]
                
        elif prediction_type == "low":
            # Low bet (1-18)
            if 1 <= result <= 18:
                return True, self.payouts["low"]
                
        elif prediction_type == "dozen1":
            # First dozen (1-12)
            if 1 <= result <= 12:
                return True, self.payouts["dozen"]
                
        elif prediction_type == "dozen2":
            # Second dozen (13-24)
            if 13 <= result <= 24:
                return True, self.payouts["dozen"]
                
        elif prediction_type == "dozen3":
            # Third dozen (25-36)
            if 25 <= result <= 36:
                return True, self.payouts["dozen"]
        
        # Player lost
        return False, 0