import os
import json
from typing import List, Optional, Dict, Any
import openai
from dataclasses import dataclass
from game_logger import GameState

@dataclass
class GameAction:
    card_index: Optional[int] = None
    action_type: Optional[str] = None  # 'resource' or 'maneuver'
    tech_bay_index: Optional[int] = None
    purchase: bool = False

class AIAgent:
    def __init__(self, api_key: Optional[str] = None):
        # Initialize OpenAI API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        openai.api_key = self.api_key
        
        # Load game rules
        with open('rules.md', 'r') as f:
            self.rules = f.read()
            
        # Initialize prompt templates
        self.action_prompt_template = """
You are an AI player in the Starship Salvage card game. Based on the following game state and rules, decide what action to take.

Game Rules:
{rules}

Current Game State:
{state}

Your hand:
{hand}

Available actions:
1. Play a card as a Resource (adds points equal to card's face value)
2. Play a card as a Maneuver (performs suit-specific action)
3. End your action phase

Please respond in JSON format:
{{
    "card_index": <index of card to play, or null to end phase>,
    "action_type": "resource" or "maneuver" or null
}}
"""

        self.purchase_prompt_template = """
You are an AI player in the Starship Salvage card game. Based on the following game state and rules, decide whether to purchase a tech card.

Game Rules:
{rules}

Current Game State:
{state}

Tech Bay:
{tech_bay}

Your current Salvage Points: {salvage_points}

Please respond in JSON format:
{{
    "purchase": true or false,
    "tech_bay_index": <index of card to purchase, or null if not purchasing>
}}
"""

    def _format_game_state(self, state: GameState) -> str:
        return f"""
Turn: {state.turn_number}
Current Player: {state.current_player}
Player 1 (You):
- Hull: {state.player1_hull}
- Shield: {state.player1_shield}
- Hand Size: {state.player1_hand_size}
- Deck Size: {state.player1_deck_size}
- Discard Size: {state.player1_discard_size}

Player 2:
- Hull: {state.player2_hull}
- Shield: {state.player2_shield}
- Hand Size: {state.player2_hand_size}
- Deck Size: {state.player2_deck_size}
- Discard Size: {state.player2_discard_size}

Tech Bay Size: {state.tech_bay_size}
Derelict Cache Size: {state.derelict_cache_size}
"""

    def _format_hand(self, hand: List[Any]) -> str:
        return "\n".join(f"[{i}] {card}" for i, card in enumerate(hand))

    def _format_tech_bay(self, tech_bay: List[Any]) -> str:
        return "\n".join(f"[{i}] {card} (Cost: {card.face_value()})" for i, card in enumerate(tech_bay) if card)

    def call_llm(self, prompt: str) -> Dict[str, Any]:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a strategic card game AI. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None

    def decide_action(self, state: GameState, hand: List[Any]) -> GameAction:
        prompt = self.action_prompt_template.format(
            rules=self.rules,
            state=self._format_game_state(state),
            hand=self._format_hand(hand)
        )
        
        try:
            response = self.call_llm(prompt)
            if response:
                return GameAction(
                    card_index=response.get('card_index'),
                    action_type=response.get('action_type')
                )
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        # Fallback heuristic: Play highest value card as resource
        try:
            max_value = -1
            max_index = -1
            for i, card in enumerate(hand):
                value = card.face_value()
                if value > max_value:
                    max_value = value
                    max_index = i
            if max_index >= 0:
                return GameAction(card_index=max_index, action_type='resource')
        except Exception as e:
            print(f"Error in heuristic fallback: {e}")
        
        return GameAction()  # End phase

    def decide_purchase(self, state: GameState, tech_bay: List[Any], salvage_points: int) -> GameAction:
        prompt = self.purchase_prompt_template.format(
            rules=self.rules,
            state=self._format_game_state(state),
            tech_bay=self._format_tech_bay(tech_bay),
            salvage_points=salvage_points
        )
        
        try:
            response = self.call_llm(prompt)
            if response and response.get('purchase'):
                return GameAction(
                    purchase=True,
                    tech_bay_index=response.get('tech_bay_index')
                )
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        # Fallback heuristic: Buy cheapest card if we have enough points
        try:
            min_cost = float('inf')
            min_index = -1
            for i, card in enumerate(tech_bay):
                if card and card.face_value() < min_cost:
                    min_cost = card.face_value()
                    min_index = i
            if min_index >= 0 and min_cost <= salvage_points:
                return GameAction(purchase=True, tech_bay_index=min_index)
        except Exception as e:
            print(f"Error in heuristic fallback: {e}")
        
        return GameAction()  # Don't purchase 