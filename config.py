"""
Configuration file for the Discord Game Console Bot.
All game settings and constants are defined here.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Core Bot Settings
class BotConfig:
    TOKEN = os.getenv("DISCORD_TOKEN", "")  # Default to empty string if not found
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is not set")
    PREFIX = "!"
    DEFAULT_POINTS = 1000
    LEADERBOARD_SIZE = 10

# Game Settings
class GameSettings:
    class Daily:
        MIN_BONUS = 100
        MAX_BONUS = 500
        COOLDOWN_HOURS = 24

    class NumberGuess:
        MIN_NUMBER = 1
        MAX_NUMBER = 100
        MAX_ATTEMPTS = 5
        BASE_POINTS = 100
        MAX_MULTIPLIER = 2.0
        MULTIPLIER_INCREMENT = 0.1

    class Trivia:
        TIMEOUT_SECONDS = 20
        BASE_POINTS = 50
        MAX_MULTIPLIER = 1.5
        MULTIPLIER_INCREMENT = 0.05

    class Slots:
        MIN_BET = 10
        MAX_BET = 1000
        SYMBOLS = ["🍒", "🍋", "💎", "7️⃣", "🔔", "🎰", "⭐"]
        PAYOUTS = {
            "🍒": 2,
            "🍋": 3,
            "💎": 10,
            "7️⃣": 7,
            "🔔": 5,
            "🎰": 15,
            "⭐": 4
        }
        JACKPOT_MULTIPLIER = 100

    class Roulette:
        MIN_BET = 10
        MAX_BET = 1000
        PAYOUTS = {
            "number": 35,
            "red": 1,
            "black": 1,
            "even": 1,
            "odd": 1,
            "low": 1,
            "high": 1,
            "dozen": 2,
            "column": 2
        }

    class Blackjack:
        MIN_BET = 25
        MAX_BET = 1000
        BLACKJACK_PAYOUT = 1.5
        NORMAL_PAYOUT = 1.0
        DECK_COUNT = 6

# Error Messages
class ErrorMessages:
    INVALID_BET = "Please enter a valid bet amount between {min} and {max}!"
    INSUFFICIENT_POINTS = "You don't have enough points!"
    GAME_IN_PROGRESS = "You already have a game in progress!"
    COOLDOWN_ACTIVE = "Please wait before using this command again"
    INVALID_TOKEN = "Bot token is not configured. Please set DISCORD_TOKEN in .env file"
    PERMISSION_ERROR = "You don't have permission to use this command"
