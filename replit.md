# Discord Games Bot Architecture Overview

## Overview

This is a Discord bot built with Python that offers several mini-games with a point system. The games include Number Guessing, Trivia, and Coin Flip. The bot tracks user points, maintains streaks, and applies multipliers to reward consistent winning.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The Discord Games Bot uses a modular architecture with separate components for each game and utility functions. The main components are:

1. **Bot Core (bot.py)**: The central component that initializes the Discord connection, loads games, and manages events.
2. **Games Module**: Contains individual game implementations, each in its own file.
3. **Utilities Module**: Contains the point system implementation.
4. **Configuration (config.py)**: Centralized settings for all bot components.

The bot is built using discord.py, a Python library that wraps the Discord API, providing an event-driven approach to handle Discord interactions.

## Key Components

### 1. Bot Core (bot.py)

This is the main entry point that:
- Initializes the Discord connection with proper intents
- Sets up logging
- Loads all game modules
- Initializes the point system
- Registers event handlers

### 2. Games

Each game is implemented as a separate class:

- **NumberGuess**: Users guess a number between a configurable range with limited attempts.
- **Trivia**: Presents multiple-choice questions with a time limit for answering.
- **CoinFlip**: Simple heads/tails game where users can double their points or lose them.

### 3. Point System (utils/point_system.py)

Manages user points, multipliers, and streaks. The system:
- Tracks points for each user
- Applies multipliers based on winning streaks
- Provides methods to add/subtract points
- Maintains user data persistently

### 4. Configuration (config.py)

Centralizes all configuration settings including:
- Bot token and command prefix
- Game-specific settings (attempts, point values, multipliers)
- Default values for new users

## Data Flow

1. **User Input**: Users interact with the bot through Discord commands.
2. **Command Processing**: The bot processes commands and routes them to the appropriate game module.
3. **Game Logic**: Game modules handle the game-specific logic and determine outcomes.
4. **Point Management**: Results are passed to the point system to update user data.
5. **Response**: The bot responds to the user with game results and updated point information.

The data flow is primarily event-driven, with the bot responding to Discord events and user commands.

## External Dependencies

The bot relies on the following external dependencies:

1. **discord.py**: The main library for Discord API integration.
2. **asyncio**: For asynchronous operation and timing functions.
3. **random**: For generating random numbers and selections.
4. **logging**: For application logging.

## Deployment Strategy

The bot is deployed using Replit's workflow system, which:

1. Installs the required dependencies (discord.py)
2. Runs the bot using the Python interpreter
3. Maintains the bot's operation through Replit's always-on feature

The deployment is configured in the .replit file, which defines workflows for running the bot.

### Environment Variables

The bot requires a `DISCORD_BOT_TOKEN` environment variable to be set with a valid Discord bot token.

### Running the Bot

To run the bot:
1. Ensure all dependencies are installed
2. Set the `DISCORD_BOT_TOKEN` environment variable
3. Run `python bot.py`

The bot will connect to Discord and respond to commands defined in the codebase.