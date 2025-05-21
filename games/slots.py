"""
Slot machine game implementation
"""
import random
import asyncio
import discord
from discord.ext import commands
import config
from utils.pointsystem import PointSystem

class SlotMachine:
    def __init__(self, bot, point_system: PointSystem):
        self.bot = bot
        self.point_system = point_system
        self.symbols = config.SLOTS_SYMBOLS
        self.payouts = config.SLOTS_PAYOUTS
        self.jackpot = config.SLOTS_JACKPOT
        
    async def play(self, ctx, bet_str):
        """Play the slot machine with a bet"""
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Convert bet string (handle 'max' and numeric values)
        bet = self._parse_bet_amount(bet_str, user_id, username)
        if bet is None:
            return await ctx.send(f"{ctx.author.mention}, please provide a valid bet amount between "
                                f"{config.SLOTS_MIN_BET} and {config.SLOTS_MAX_BET}.")
        
        # Check if user has enough points
        user_points = self.point_system.get_points(user_id, username)
        if bet > user_points:
            return await ctx.send(f"{ctx.author.mention}, you don't have enough points for that bet! "
                                f"You have {user_points} points.")
        
        # Create initial message with slot machine animation
        embed = discord.Embed(
            title="🎰 Spinning the Slot Machine...",
            description="Good luck!",
            color=discord.Color.gold()
        )
        embed.add_field(name="Bet", value=f"{bet} points")
        message = await ctx.send(embed=embed)
        
        # Slot machine animation
        await self._animate_slots(message)
        
        # Generate result
        result = self._generate_result()
        
        # Check win condition
        win_amount, payout_multiplier = self._calculate_win(result, bet)
        
        # Update user points
        if win_amount > 0:
            # Win
            won = True
            self.point_system.add_points(user_id, username, "slots", win_amount, won=True)
            color = discord.Color.green()
            result_text = f"🎉 You won {win_amount} points! ({payout_multiplier}x)"
        else:
            # Loss
            won = False
            self.point_system.add_points(user_id, username, "slots", -bet, won=False)
            color = discord.Color.red()
            result_text = "❌ You lost your bet!"
        
        # Create result embed
        embed = discord.Embed(
            title="🎰 Slot Machine Results",
            description=f"[ {result[0]} | {result[1]} | {result[2]} ]",
            color=color
        )
        embed.add_field(name="Result", value=result_text, inline=False)
        embed.add_field(name="Bet", value=f"{bet} points")
        embed.add_field(name="Current Points", value=f"{self.point_system.get_points(user_id, username)} points")
        
        # Update message with final result
        await message.edit(embed=embed)
    
    def _parse_bet_amount(self, bet_str, user_id, username):
        """Parse the bet amount from string input"""
        # Check for 'max' or 'm' bet
        if bet_str.lower() in ['max', 'm', 'all', 'a']:
            bet = min(self.point_system.get_points(user_id, username), config.SLOTS_MAX_BET)
            return bet
            
        # Try to convert to integer
        try:
            bet = int(bet_str)
            
            # Check if bet is within allowed range
            if bet < config.SLOTS_MIN_BET:
                return None
            if bet > config.SLOTS_MAX_BET:
                bet = config.SLOTS_MAX_BET
                
            return bet
        except ValueError:
            return None
    
    async def _animate_slots(self, message):
        """Create a slot machine spinning animation"""
        for _ in range(3):  # Spin 3 times
            # Generate random symbols for animation
            symbols = [random.choice(self.symbols) for _ in range(3)]
            
            # Update embed with spinning animation
            embed = message.embeds[0]
            embed.description = f"[ {symbols[0]} | {symbols[1]} | {symbols[2]} ]"
            await message.edit(embed=embed)
            
            # Short delay between animations
            await asyncio.sleep(0.7)
    
    def _generate_result(self):
        """Generate the final slot machine result"""
        return [random.choice(self.symbols) for _ in range(3)]
    
    def _calculate_win(self, result, bet):
        """Calculate win amount based on result"""
        # Check for three of a kind
        if result[0] == result[1] == result[2]:
            symbol = result[0]
            multiplier = self.payouts.get(symbol, 1)
            
            # Check for jackpot (three diamonds)
            if symbol == "💎":
                multiplier = self.jackpot
                
            win_amount = bet * multiplier
            return win_amount, multiplier
            
        # Check for two cherries (special case)
        if result.count("🍒") >= 2:
            win_amount = bet * self.payouts["🍒"]
            return win_amount, self.payouts["🍒"]
            
        # No win
        return 0, 0