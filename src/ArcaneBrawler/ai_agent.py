import re
from typing import List, Optional, Tuple
from player import Player, Archetype
from card import Card, Suit
from game_state import GameState, Phase
from card_lookup import format_hand_display, format_field_display

class AIAgent:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.ai_player = None
        self.health_multiplier = 1.5  # AI has 50% more health
        self.power_multiplier = 1.2   # AI deals 20% more damage
        
    def initialize_ai_player(self, archetype: Archetype) -> Player:
        """Initialize the AI player with scaled stats."""
        self.ai_player = Player("AI Opponent", archetype)
        self.ai_player.max_health = int(self.ai_player.max_health * self.health_multiplier)
        self.ai_player.health = self.ai_player.max_health
        return self.ai_player
    
    def get_ai_prompt(self) -> str:
        """Generate the prompt for the AI's turn."""
        current_phase = self.game_state.phase
        player1, player2 = self.game_state.players
        
        prompt = f"""You are playing Arcane Shuffle as the {self.ai_player.archetype.value} archetype.
Your health: {self.ai_player.health}/{self.ai_player.max_health}
Your mana: {self.ai_player.mana}/{self.ai_player.max_mana}

Opponents:
1. {player1.name} ({player1.archetype.value}) - Health: {player1.health}/{player1.max_health}
2. {player2.name} ({player2.archetype.value}) - Health: {player2.health}/{player2.max_health}

Your hand:
{chr(10).join(format_hand_display(self.ai_player.hand, self.ai_player.archetype))}

Your field:
{chr(10).join(format_field_display(self.ai_player.field, self.ai_player.archetype))}

Current phase: {current_phase.value}

Available actions:
"""
        
        if current_phase == Phase.MAIN1 or current_phase == Phase.MAIN2:
            prompt += """- Play a card: "play [card_index]"
- End phase: "end"
"""
        elif current_phase == Phase.COMBAT:
            prompt += """- Attack: "attack [attacker_index] [target_player_index] [blocker_index]"
   (target_player_index: 1 or 2, blocker_index: -1 for no blocker)
- End combat: "end"
"""
        
        prompt += """
Example response: "play 2" or "attack 0 1 -1"

What action do you take?"""
        
        return prompt
    
    def parse_ai_response(self, response: str) -> Optional[Tuple[str, List[int]]]:
        """Parse the AI's response into an action and parameters."""
        # Try to match play card action
        play_match = re.match(r"play\s+(\d+)", response.lower())
        if play_match:
            return ("play", [int(play_match.group(1))])
            
        # Try to match attack action
        attack_match = re.match(r"attack\s+(\d+)\s+(\d+)\s+(-?\d+)", response.lower())
        if attack_match:
            return ("attack", [int(x) for x in attack_match.groups()])
            
        # Try to match end action
        if "end" in response.lower():
            return ("end", [])
            
        return None
    
    def get_ai_action(self, response: str) -> Tuple[str, List[int]]:
        """Get the AI's action, with fallback to random action if parsing fails."""
        parsed = self.parse_ai_response(response)
        if parsed:
            return parsed
            
        # Fallback to random action
        if self.game_state.phase in [Phase.MAIN1, Phase.MAIN2]:
            if self.ai_player.hand:
                return ("play", [0])  # Play first card
            return ("end", [])
        elif self.game_state.phase == Phase.COMBAT:
            attacking_creatures = [i for i, card in enumerate(self.ai_player.field) 
                                 if not card.tapped and card.is_creature]
            if attacking_creatures:
                return ("attack", [attacking_creatures[0], 1, -1])  # Attack first player
            return ("end", [])
        return ("end", []) 