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

# Slots settings
SLOTS_MIN_BET = 10
SLOTS_MAX_BET = 1000
SLOTS_SYMBOLS = ["🍒", "🍋", "💎", "7️⃣", "🔔", "🎰", "⭐"]
SLOTS_PAYOUTS = {
    "🍒": 2,     # Two cherries pays 2x
    "🍋": 3,     # Three lemons pays 3x
    "💎": 10,    # Three diamonds pays 10x
    "7️⃣": 7,     # Three sevens pays 7x
    "🔔": 5,     # Three bells pays 5x
    "🎰": 15,    # Three bars pays 15x
    "⭐": 4      # Three stars pays 4x
}
SLOTS_JACKPOT = 100  # Jackpot multiplier for 3 diamonds

# Roulette settings
ROULETTE_MIN_BET = 10
ROULETTE_MAX_BET = 1000
ROULETTE_TIMEOUT = 15  # Seconds to place bets
ROULETTE_PAYOUTS = {
    "number": 35,     # Single number pays 35:1
    "red": 1,         # Red pays 1:1
    "black": 1,       # Black pays 1:1
    "even": 1,        # Even pays 1:1
    "odd": 1,         # Odd pays 1:1
    "low": 1,         # 1-18 pays 1:1
    "high": 1,        # 19-36 pays 1:1
    "dozen": 2,       # Dozen (1-12, 13-24, 25-36) pays 2:1
    "column": 2       # Column pays 2:1
}

# Blackjack settings
BLACKJACK_MIN_BET = 25
BLACKJACK_MAX_BET = 1000
BLACKJACK_TIMEOUT = 30  # Seconds to make a decision
BLACKJACK_BLACKJACK_PAYOUT = 1.5  # Blackjack pays 3:2
BLACKJACK_WIN_PAYOUT = 1  # Normal win pays 1:1

# Point system
DEFAULT_POINTS = 1000  # Starting points for new users
DEFAULT_MULTIPLIER = 1.0

# Daily bonus
DAILY_MIN = 100
DAILY_MAX = 500
