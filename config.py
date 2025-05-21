"""
Configuration file for the Discord bot.
"""
import os

# Bot configuration
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")  # Discord bot token
PREFIX = "!"  # Command prefix

# Game settings
GUESS_MIN = 1
GUESS_MAX = 100
GUESS_ATTEMPTS = 5
GUESS_POINTS = 100
GUESS_MULTIPLIER = 1.5  # Multiplier for consecutive wins

TRIVIA_TIMEOUT = 20  # Seconds to answer trivia questions
TRIVIA_POINTS = 50
TRIVIA_MULTIPLIER = 1.2  # Multiplier for consecutive right answers

COINFLIP_POINTS = 25
COINFLIP_MULTIPLIER = 2  # Double or nothing

# Point system
DEFAULT_POINTS = 0
DEFAULT_MULTIPLIER = 1.0
