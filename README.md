> **Note:**  
> This repository contains a simple Discord casino bot implemented in Python using `discord.py`.  
> **Slash commands, advanced features, and side games described below are not implemented in this version.**  
> Only classic prefix commands (e.g. `!blackjack`, `!slots`, etc.) are supported.  
> See the bottom of this file for a list of supported commands.

# Discord Game Console 🎮

A feature-rich Discord bot that turns your server into a virtual casino with multiple games and a point system.

## 🎲 Features

- **Multiple Games**
  - Number Guessing
  - Trivia
  - Coin Flip
  - Slots
  - Roulette
  - Blackjack

- **Point System**
  - Daily Bonuses
  - Multipliers
  - Global Leaderboard

## 🚀 Quick Start

1. **Prerequisites**
   - Python 3.8+
   - Discord Bot Token

2. **Installation**
   ```bash
   git clone https://github.com/yourusername/discord-game-console.git
   cd discord-game-console
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Copy `.env.example` to `.env`
   - Add your Discord bot token
   - Customize settings in `config.py`

4. **Run**
   ```bash
   python bot.py
   ```

## 🎯 Commands

All commands use the prefix `!`

### 🎮 Games
- `!guess` - Number guessing game
- `!trivia` - Trivia game
- `!coinflip` - Coin flip betting
- `!slots` - Slot machine
- `!roulette` - Roulette table
- `!blackjack` - Blackjack game

### 💰 Economy
- `!daily` - Daily bonus
- `!points` - Check balance
- `!leaderboard` - Top players

## ⚙️ Configuration

Edit `config.py` to customize:
- Starting points
- Game rules
- Betting limits
- Payout rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📝 License

MIT License - See LICENSE file

---

## Supported Commands (This Version)

The following commands are available with the default prefix `!`:

- `!help` — Show help message
- `!guess start` / `!guess [number]` — Number guessing game
- `!trivia` — Trivia game
- `!coinflip [heads/tails] [bet]` — Coin flip game
- `!slots [bet]` — Slot machine
- `!roulette [prediction] [bet]` — Roulette game
- `!blackjack [bet] [easy|hard]` — Blackjack game
- `!hit` — Take another card in blackjack
- `!stand` — Stand in blackjack
- `!double` — Double down in blackjack
- `!daily` — Claim daily bonus
- `!points` — Check your points
- `!leaderboard` — View the top players

> For all commands, use the prefix `!` (or change it in `config.py`).
>  
> There are **no slash commands** or advanced features in this version.

---

Play games, win cash, and climb the leaderboards with Piglet Gambling Bot!