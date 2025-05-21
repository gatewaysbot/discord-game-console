"""
Trivia game implementation
"""
import random
import asyncio
import discord
from discord.ext import commands
import config
from utils.point_system import PointSystem

# Sample trivia questions - in a real implementation, you'd use an API or larger question set
TRIVIA_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": "Paris",
        "category": "Geography"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Pablo Picasso", "Vincent van Gogh", "Leonardo da Vinci", "Michelangelo"],
        "answer": "Leonardo da Vinci",
        "category": "Art"
    },
    {
        "question": "What is the largest planet in our solar system?",
        "options": ["Earth", "Jupiter", "Saturn", "Mars"],
        "answer": "Jupiter",
        "category": "Astronomy"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "answer": "William Shakespeare",
        "category": "Literature"
    },
    {
        "question": "What is the chemical symbol for gold?",
        "options": ["Go", "Gd", "Au", "Ag"],
        "answer": "Au",
        "category": "Chemistry"
    },
    {
        "question": "What is the tallest mountain in the world?",
        "options": ["Mount Everest", "K2", "Kangchenjunga", "Makalu"],
        "answer": "Mount Everest",
        "category": "Geography"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Jupiter", "Mars", "Mercury"],
        "answer": "Mars",
        "category": "Astronomy"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
        "answer": "Pacific Ocean",
        "category": "Geography"
    },
    {
        "question": "Who is the author of 'Harry Potter' series?",
        "options": ["J.R.R. Tolkien", "J.K. Rowling", "Stephen King", "George R.R. Martin"],
        "answer": "J.K. Rowling",
        "category": "Literature"
    },
    {
        "question": "What is the hardest natural substance on Earth?",
        "options": ["Gold", "Iron", "Diamond", "Platinum"],
        "answer": "Diamond",
        "category": "Science"
    }
]

class Trivia:
    def __init__(self, bot, point_system: PointSystem):
        self.bot = bot
        self.point_system = point_system
        self.active_games = {}  # {channel_id: {user_id: question_data}}
        
    async def start_game(self, ctx):
        """Start a new trivia game for a user"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user already has an active game
        if channel_id in self.active_games and user_id in self.active_games[channel_id]:
            return await ctx.send(f"{ctx.author.mention}, you already have an active trivia game!")
        
        # Initialize channel if needed
        if channel_id not in self.active_games:
            self.active_games[channel_id] = {}
            
        # Select a random question
        question_data = random.choice(TRIVIA_QUESTIONS)
        self.active_games[channel_id][user_id] = question_data
        
        # Get current multiplier and streak
        multiplier = self.point_system.get_multiplier(user_id, username, "trivia")
        streak = self.point_system.get_streak(user_id, username, "trivia")
        
        # Create an embed for the question
        embed = discord.Embed(
            title=f"🧠 Trivia Question ({question_data['category']})",
            description=question_data["question"],
            color=discord.Color.blue()
        )
        
        # Add options
        for i, option in enumerate(question_data["options"]):
            embed.add_field(name=f"Option {chr(65+i)}", value=option, inline=True)
            
        embed.add_field(name="Current Streak", value=f"{streak} correct", inline=True)
        embed.add_field(name="Current Multiplier", value=f"{multiplier:.2f}x", inline=True)
        embed.add_field(name="Possible Points", value=f"{int(config.TRIVIA_POINTS * multiplier)}", inline=True)
        embed.add_field(
            name="How to Answer", 
            value=f"Type A, B, C, or D to select your answer within {config.TRIVIA_TIMEOUT} seconds!",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Check for the answer
        def check(message):
            return (
                message.author.id == ctx.author.id and 
                message.channel.id == ctx.channel.id and
                message.content.upper() in ["A", "B", "C", "D"]
            )
        
        try:
            # Wait for the answer
            response = await self.bot.wait_for("message", check=check, timeout=config.TRIVIA_TIMEOUT)
            
            # Process the answer
            await self.process_answer(ctx, response)
        except asyncio.TimeoutError:
            # If the user doesn't answer in time
            if channel_id in self.active_games and user_id in self.active_games[channel_id]:
                # Reset streak
                self.point_system.add_points(user_id, username, "trivia", 0, won=False)
                
                await ctx.send(f"{ctx.author.mention}, time's up! The correct answer was "
                              f"**{question_data['answer']}**. Your streak has been reset.")
                
                # Remove the game
                del self.active_games[channel_id][user_id]
    
    async def process_answer(self, ctx, response):
        """Process the user's answer to a trivia question"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if the game still exists
        if channel_id not in self.active_games or user_id not in self.active_games[channel_id]:
            return
            
        question_data = self.active_games[channel_id][user_id]
        options = question_data["options"]
        
        # Convert A, B, C, D to index
        option_idx = ord(response.content.upper()) - ord('A')
        
        # Check if the answer is correct
        is_correct = False
        if 0 <= option_idx < len(options) and options[option_idx] == question_data["answer"]:
            is_correct = True
            
        if is_correct:
            # Award points
            points, multiplier = self.point_system.add_points(
                user_id, 
                username, 
                "trivia", 
                config.TRIVIA_POINTS,
                won=True
            )
            
            new_streak = self.point_system.get_streak(user_id, username, "trivia")
            new_multiplier = self.point_system.get_multiplier(user_id, username, "trivia")
            
            embed = discord.Embed(
                title="✅ Correct Answer!",
                description=f"Well done! **{question_data['answer']}** is the correct answer!",
                color=discord.Color.green()
            )
            embed.add_field(name="Points Earned", value=f"+{points} points")
            embed.add_field(name="New Streak", value=f"{new_streak} correct")
            embed.add_field(name="Next Multiplier", value=f"{new_multiplier:.2f}x")
            
            await ctx.send(embed=embed)
        else:
            # Reset streak
            self.point_system.add_points(user_id, username, "trivia", 0, won=False)
            
            embed = discord.Embed(
                title="❌ Incorrect Answer",
                description=f"Sorry, that's wrong. The correct answer was **{question_data['answer']}**.",
                color=discord.Color.red()
            )
            embed.add_field(name="Streak Reset", value="Your streak has been reset to 0")
            embed.add_field(name="Next Multiplier", value="1.0x")
            
            await ctx.send(embed=embed)
            
        # Remove the game
        del self.active_games[channel_id][user_id]
