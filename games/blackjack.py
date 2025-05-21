"""
Blackjack game implementation
"""
import random
import asyncio
import discord
from discord.ext import commands
import config
from utils.point_system import PointSystem

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        
    def __str__(self):
        return f"{self.value}{self.suit}"
        
    def get_value(self):
        if self.value in ["J", "Q", "K"]:
            return 10
        elif self.value == "A":
            return 11  # Aces are 11 by default, special handling in hand calculation
        else:
            return int(self.value)

class Deck:
    def __init__(self, num_decks=6):
        suits = ["♠️", "♥️", "♦️", "♣️"]
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cards = []
        
        # Generate deck with specified number of decks
        for _ in range(num_decks):
            for suit in suits:
                for value in values:
                    self.cards.append(Card(suit, value))
                    
        # Shuffle the deck
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            # If deck is empty, create a new shuffled deck
            self.__init__()
            return self.cards.pop()

class BlackjackGame:
    def __init__(self, bot, point_system: PointSystem):
        self.bot = bot
        self.point_system = point_system
        self.deck = Deck()
        self.active_games = {}  # {channel_id: {user_id: game_data}}
        
    async def start_game(self, ctx, bet_str, mode="easy"):
        """Start a new blackjack game"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user already has an active game
        if channel_id in self.active_games and user_id in self.active_games[channel_id]:
            return await ctx.send(f"{ctx.author.mention}, you already have an active blackjack game!")
        
        # Parse and validate bet
        bet = self._parse_bet_amount(bet_str, user_id, username)
        if bet is None:
            return await ctx.send(f"{ctx.author.mention}, please provide a valid bet amount between "
                                f"{config.BLACKJACK_MIN_BET} and {config.BLACKJACK_MAX_BET}.")
        
        # Check if user has enough points
        user_points = self.point_system.get_points(user_id, username)
        if bet > user_points:
            return await ctx.send(f"{ctx.author.mention}, you don't have enough points for that bet! "
                                f"You have {user_points} points.")
        
        # Initialize channel if needed
        if channel_id not in self.active_games:
            self.active_games[channel_id] = {}
        
        # Deal initial cards
        player_hand = [self.deck.deal(), self.deck.deal()]
        dealer_hand = [self.deck.deal(), self.deck.deal()]
        
        # Store game data
        self.active_games[channel_id][user_id] = {
            "player_hand": player_hand,
            "dealer_hand": dealer_hand,
            "bet": bet,
            "mode": mode,
            "status": "playing",  # playing, stand, bust, blackjack, dealer_blackjack
            "message": None
        }
        
        # Check for blackjack
        player_value = self._calculate_hand_value(player_hand)
        dealer_value = self._calculate_hand_value(dealer_hand)
        
        game_data = self.active_games[channel_id][user_id]
        
        # Check for player or dealer blackjack
        if player_value == 21 and len(player_hand) == 2:
            game_data["status"] = "blackjack"
        if dealer_value == 21 and len(dealer_hand) == 2:
            game_data["status"] = "dealer_blackjack"
        
        # Create and send initial game state
        embed = await self._create_game_embed(ctx.author, game_data)
        game_data["message"] = await ctx.send(embed=embed)
        
        # Add action buttons
        if game_data["status"] in ["playing"]:
            await self._add_game_buttons(game_data["message"])
            
            # Process game if player has blackjack or dealer has blackjack
            if game_data["status"] in ["blackjack", "dealer_blackjack"]:
                await self._process_game_end(ctx, user_id, username, channel_id)
            
    async def hit(self, ctx):
        """Player takes another card"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user has an active game
        if channel_id not in self.active_games or user_id not in self.active_games[channel_id]:
            return await ctx.send(f"{ctx.author.mention}, you don't have an active blackjack game! "
                                f"Start a new game with `{config.PREFIX}blackjack [bet]`.")
        
        game_data = self.active_games[channel_id][user_id]
        
        # Check if game is still in playing state
        if game_data["status"] != "playing":
            return await ctx.send(f"{ctx.author.mention}, you can't hit anymore in this game. "
                               f"Game status: {game_data['status']}")
        
        # Deal a new card to player
        game_data["player_hand"].append(self.deck.deal())
        
        # Check if player busted
        player_value = self._calculate_hand_value(game_data["player_hand"])
        if player_value > 21:
            game_data["status"] = "bust"
            
            # Process game end
            await self._process_game_end(ctx, user_id, username, channel_id)
        
        # Update game display
        embed = await self._create_game_embed(ctx.author, game_data)
        await game_data["message"].edit(embed=embed)
        
    async def stand(self, ctx):
        """Player stands, dealer plays"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user has an active game
        if channel_id not in self.active_games or user_id not in self.active_games[channel_id]:
            return await ctx.send(f"{ctx.author.mention}, you don't have an active blackjack game! "
                                f"Start a new game with `{config.PREFIX}blackjack [bet]`.")
        
        game_data = self.active_games[channel_id][user_id]
        
        # Check if game is still in playing state
        if game_data["status"] != "playing":
            return await ctx.send(f"{ctx.author.mention}, you can't stand anymore in this game. "
                               f"Game status: {game_data['status']}")
        
        # Set status to stand
        game_data["status"] = "stand"
        
        # Process dealer's turn and game end
        await self._process_game_end(ctx, user_id, username, channel_id)
        
    async def double_down(self, ctx):
        """Player doubles bet, takes one card, and stands"""
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if user has an active game
        if channel_id not in self.active_games or user_id not in self.active_games[channel_id]:
            return await ctx.send(f"{ctx.author.mention}, you don't have an active blackjack game! "
                                f"Start a new game with `{config.PREFIX}blackjack [bet]`.")
        
        game_data = self.active_games[channel_id][user_id]
        
        # Check if game is still in playing state
        if game_data["status"] != "playing":
            return await ctx.send(f"{ctx.author.mention}, you can't double down anymore in this game. "
                               f"Game status: {game_data['status']}")
                               
        # Check if player has only 2 cards (double down only allowed on initial hand)
        if len(game_data["player_hand"]) != 2:
            return await ctx.send(f"{ctx.author.mention}, you can only double down on your initial hand!")
        
        # Check if player has enough points to double down
        user_points = self.point_system.get_points(user_id, username)
        if user_points < game_data["bet"] * 2:
            return await ctx.send(f"{ctx.author.mention}, you don't have enough points to double down! "
                                f"You have {user_points} points.")
        
        # Double the bet
        game_data["bet"] *= 2
        
        # Deal one more card to player
        game_data["player_hand"].append(self.deck.deal())
        
        # Check if player busted
        player_value = self._calculate_hand_value(game_data["player_hand"])
        if player_value > 21:
            game_data["status"] = "bust"
        else:
            game_data["status"] = "stand"  # Player automatically stands after doubling down
        
        # Process dealer's turn and game end
        await self._process_game_end(ctx, user_id, username, channel_id)
    
    def _parse_bet_amount(self, bet_str, user_id, username):
        """Parse the bet amount from string input"""
        # Check for 'max' or 'm' bet
        if bet_str.lower() in ['max', 'm', 'all', 'a']:
            bet = min(self.point_system.get_points(user_id, username), config.BLACKJACK_MAX_BET)
            return bet
            
        # Try to convert to integer
        try:
            bet = int(bet_str)
            
            # Check if bet is within allowed range
            if bet < config.BLACKJACK_MIN_BET:
                return None
            if bet > config.BLACKJACK_MAX_BET:
                bet = config.BLACKJACK_MAX_BET
                
            return bet
        except ValueError:
            return None
    
    def _calculate_hand_value(self, hand):
        """Calculate the value of a hand, handling aces appropriately"""
        value = 0
        aces = 0
        
        for card in hand:
            if card.value == "A":
                aces += 1
                value += 11
            else:
                value += card.get_value()
        
        # Adjust for aces if busting
        while value > 21 and aces > 0:
            value -= 10  # Count an ace as 1 instead of 11
            aces -= 1
            
        return value
    
    def _format_hand(self, hand, mode="easy", hide_first=False):
        """Format a hand for display"""
        cards_str = ""
        total = 0
        
        if hide_first:
            cards_str = "🂠 "  # Hidden card
            # Calculate value without first card
            total = self._calculate_hand_value(hand[1:])
            for card in hand[1:]:
                cards_str += f"{card} "
        else:
            total = self._calculate_hand_value(hand)
            for card in hand:
                cards_str += f"{card} "
        
        # For easy mode, display the hand total
        if mode == "easy" and not hide_first:
            # Check for soft hand (ace counted as 11)
            has_ace = any(card.value == "A" for card in hand)
            soft_value = 0
            
            if has_ace:
                # Calculate alternate value with an ace as 1
                soft_value = total - 10
                if soft_value < total and soft_value <= 21:
                    return f"{cards_str} ({soft_value}/{total})"
                    
            return f"{cards_str} ({total})"
        else:
            return cards_str
    
    async def _create_game_embed(self, author, game_data):
        """Create a game status embed"""
        status = game_data["status"]
        mode = game_data["mode"]
        
        # Determine embed color based on game status
        if status == "blackjack":
            color = discord.Color.gold()
            title = "🎰 Blackjack! You Win!"
        elif status == "dealer_blackjack":
            color = discord.Color.red()
            title = "🎰 Dealer has Blackjack! You Lose!"
        elif status == "bust":
            color = discord.Color.red()
            title = "🎰 Bust! You Lose!"
        elif status == "win":
            color = discord.Color.green()
            title = "🎰 You Win!"
        elif status == "lose":
            color = discord.Color.red()
            title = "🎰 You Lose!"
        elif status == "push":
            color = discord.Color.blue()
            title = "🎰 Push! It's a Tie!"
        else:
            color = discord.Color.blue()
            title = "🎰 Blackjack"
        
        embed = discord.Embed(
            title=title,
            color=color
        )
        
        # Show dealer's hand (hide first card if game is still in progress)
        hide_dealer_card = (status == "playing")
        dealer_hand_str = self._format_hand(game_data["dealer_hand"], mode, hide_dealer_card)
        
        # Show player's hand
        player_hand_str = self._format_hand(game_data["player_hand"], mode)
        
        embed.add_field(name="Dealer's Hand", value=dealer_hand_str, inline=False)
        embed.add_field(name="Your Hand", value=player_hand_str, inline=False)
        embed.add_field(name="Bet", value=f"{game_data['bet']} points", inline=True)
        
        # Add player options if game is in progress
        if status == "playing":
            embed.add_field(
                name="Options", 
                value="Hit - Draw another card\n"
                      "Stand - End your turn\n"
                      "Double Down - Double your bet, take 1 card, and stand",
                inline=False
            )
        
        embed.set_footer(text=f"Player: {author.name}")
        return embed
    
    async def _add_game_buttons(self, message):
        """Add buttons for player actions"""
        # This method would normally add reaction buttons for hit, stand, etc.
        # Since the discord.py library handles button creation differently based on version,
        # we're simplifying for this implementation
        
        # In a full implementation, this would add buttons that the player could click
        # For now, we'll rely on text commands (!hit, !stand, etc.)
        # Instead, we'll just add a note to the message that buttons would appear here
        
        await message.channel.send("Use `!hit`, `!stand`, or `!double` to take your turn.")
    
    async def _process_game_end(self, ctx, user_id, username, channel_id):
        """Process the end of a game"""
        game_data = self.active_games[channel_id][user_id]
        
        # If player busted, dealer wins automatically
        if game_data["status"] == "bust":
            # Player loses bet
            self.point_system.add_points(user_id, username, "blackjack", -game_data["bet"], won=False)
            
            # Update game display
            embed = await self._create_game_embed(ctx.author, game_data)
            await game_data["message"].edit(embed=embed)
            
            # Clean up game data
            del self.active_games[channel_id][user_id]
            return
        
        # If player has blackjack
        if game_data["status"] == "blackjack":
            # Check if dealer also has blackjack
            dealer_value = self._calculate_hand_value(game_data["dealer_hand"])
            if dealer_value == 21 and len(game_data["dealer_hand"]) == 2:
                game_data["status"] = "push"  # It's a tie (push)
                # Return bet
                self.point_system.add_points(user_id, username, "blackjack", 0, won=True)
            else:
                # Player wins with blackjack (pays 3:2)
                win_amount = int(game_data["bet"] * config.BLACKJACK_BLACKJACK_PAYOUT)
                self.point_system.add_points(user_id, username, "blackjack", win_amount, won=True)
                
            # Update game display
            embed = await self._create_game_embed(ctx.author, game_data)
            await game_data["message"].edit(embed=embed)
            
            # Clean up game data
            del self.active_games[channel_id][user_id]
            return
        
        # If dealer has blackjack
        if game_data["status"] == "dealer_blackjack":
            # Player loses bet
            self.point_system.add_points(user_id, username, "blackjack", -game_data["bet"], won=False)
            
            # Update game display
            embed = await self._create_game_embed(ctx.author, game_data)
            await game_data["message"].edit(embed=embed)
            
            # Clean up game data
            del self.active_games[channel_id][user_id]
            return
        
        # Dealer plays their hand (if player stands or doubles down)
        # Dealer must hit until they have at least 17
        if game_data["status"] == "stand":
            # Show dealer animation
            for _ in range(2):
                embed = await self._create_game_embed(ctx.author, game_data)
                await game_data["message"].edit(embed=embed)
                await asyncio.sleep(1)
                
            dealer_value = self._calculate_hand_value(game_data["dealer_hand"])
            
            # Dealer hits until they have at least 17
            while dealer_value < 17:
                game_data["dealer_hand"].append(self.deck.deal())
                dealer_value = self._calculate_hand_value(game_data["dealer_hand"])
                
                # Show dealer drawing cards
                embed = await self._create_game_embed(ctx.author, game_data)
                await game_data["message"].edit(embed=embed)
                await asyncio.sleep(1)
            
            player_value = self._calculate_hand_value(game_data["player_hand"])
            
            # Determine winner
            if dealer_value > 21:
                # Dealer busts, player wins
                game_data["status"] = "win"
                win_amount = int(game_data["bet"] * config.BLACKJACK_WIN_PAYOUT)
                self.point_system.add_points(user_id, username, "blackjack", win_amount, won=True)
            elif dealer_value > player_value:
                # Dealer wins
                game_data["status"] = "lose"
                self.point_system.add_points(user_id, username, "blackjack", -game_data["bet"], won=False)
            elif dealer_value < player_value:
                # Player wins
                game_data["status"] = "win"
                win_amount = int(game_data["bet"] * config.BLACKJACK_WIN_PAYOUT)
                self.point_system.add_points(user_id, username, "blackjack", win_amount, won=True)
            else:
                # Push (tie)
                game_data["status"] = "push"
                self.point_system.add_points(user_id, username, "blackjack", 0, won=True)
            
            # Update game display
            embed = await self._create_game_embed(ctx.author, game_data)
            await game_data["message"].edit(embed=embed)
            
            # Clean up game data
            del self.active_games[channel_id][user_id]