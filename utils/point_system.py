"""
Handles the point system, multipliers, and leaderboard functionality
"""
import json
from typing import Dict, List, Tuple
import logging

# User data storage format:
# {
#   user_id: {
#       "points": int,
#       "multipliers": {
#           "guess": float,
#           "trivia": float,
#           "coinflip": float
#       },
#       "streak": {
#           "guess": int,
#           "trivia": int,
#           "coinflip": int
#       },
#       "username": str
#   }
# }

class PointSystem:
    def __init__(self):
        self.user_data = {}
        logging.info("Point system initialized")
        
    def get_user_data(self, user_id: str, username: str) -> Dict:
        """
        Get user data, create if doesn't exist
        """
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "points": 0,
                "multipliers": {
                    "guess": 1.0,
                    "trivia": 1.0,
                    "coinflip": 1.0
                },
                "streak": {
                    "guess": 0,
                    "trivia": 0,
                    "coinflip": 0
                },
                "username": username
            }
        # Update username in case it changed
        else:
            self.user_data[user_id]["username"] = username
            
        return self.user_data[user_id]
    
    def add_points(self, user_id: str, username: str, game: str, base_points: int, won: bool = True) -> Tuple[int, float]:
        """
        Add points to a user based on the game and apply multipliers
        Returns the points awarded and the multiplier used
        """
        user_data = self.get_user_data(user_id, username)
        
        # Update streak
        if won:
            user_data["streak"][game] += 1
        else:
            user_data["streak"][game] = 0
            
        # Calculate multiplier based on streak
        if game == "guess":
            user_data["multipliers"][game] = 1.0 + (user_data["streak"][game] * 0.1)
            if user_data["multipliers"][game] > 2.0:  # Cap multiplier
                user_data["multipliers"][game] = 2.0
        elif game == "trivia":
            user_data["multipliers"][game] = 1.0 + (user_data["streak"][game] * 0.05)
            if user_data["multipliers"][game] > 1.5:  # Cap multiplier
                user_data["multipliers"][game] = 1.5
        elif game == "coinflip":
            # Coinflip has a fixed multiplier of 2.0 for wins
            if not won:
                user_data["multipliers"][game] = 1.0
            else:
                user_data["multipliers"][game] = 2.0
        
        # Award points only if won
        points_awarded = 0
        if won:
            multiplier = user_data["multipliers"][game]
            points_awarded = int(base_points * multiplier)
            user_data["points"] += points_awarded
            
        return points_awarded, user_data["multipliers"][game]
    
    def get_points(self, user_id: str, username: str) -> int:
        """Get current points for a user"""
        user_data = self.get_user_data(user_id, username)
        return user_data["points"]
    
    def get_multiplier(self, user_id: str, username: str, game: str) -> float:
        """Get current multiplier for a user in a specific game"""
        user_data = self.get_user_data(user_id, username)
        return user_data["multipliers"].get(game, 1.0)
    
    def get_streak(self, user_id: str, username: str, game: str) -> int:
        """Get current streak for a user in a specific game"""
        user_data = self.get_user_data(user_id, username)
        return user_data["streak"].get(game, 0)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Get the top users by points
        """
        # Sort users by points
        sorted_users = sorted(
            self.user_data.items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )
        
        # Format for display
        leaderboard = []
        for i, (user_id, data) in enumerate(sorted_users[:limit], 1):
            leaderboard.append({
                "rank": i,
                "username": data["username"],
                "points": data["points"]
            })
            
        return leaderboard
