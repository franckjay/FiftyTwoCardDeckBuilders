import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class GameState:
    session_id: str
    timestamp: str
    turn_number: int
    current_player: str
    player1_name: str
    player2_name: str
    player1_hull: int
    player2_hull: int
    player1_shield: int
    player2_shield: int
    player1_hand_size: int
    player2_hand_size: int
    player1_deck_size: int
    player2_deck_size: int
    player1_discard_size: int
    player2_discard_size: int
    tech_bay_size: int
    derelict_cache_size: int
    phase: str  # 'draw', 'action', 'purchase', 'combat', 'end'

class GameLogger:
    def __init__(self, log_file: str = "game_states.json", outcome_file: str = "game_outcomes.json"):
        self.log_file = log_file
        self.outcome_file = outcome_file
        self.session_id = str(uuid.uuid4())
        self.states: List[GameState] = []
        
    def log_state(self, 
                 turn_number: int,
                 current_player: str,
                 player1_name: str,
                 player2_name: str,
                 player1_hull: int,
                 player2_hull: int,
                 player1_shield: int,
                 player2_shield: int,
                 player1_hand_size: int,
                 player2_hand_size: int,
                 player1_deck_size: int,
                 player2_deck_size: int,
                 player1_discard_size: int,
                 player2_discard_size: int,
                 tech_bay_size: int,
                 derelict_cache_size: int,
                 phase: str):
        
        state = GameState(
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            turn_number=turn_number,
            current_player=current_player,
            player1_name=player1_name,
            player2_name=player2_name,
            player1_hull=player1_hull,
            player2_hull=player2_hull,
            player1_shield=player1_shield,
            player2_shield=player2_shield,
            player1_hand_size=player1_hand_size,
            player2_hand_size=player2_hand_size,
            player1_deck_size=player1_deck_size,
            player2_deck_size=player2_deck_size,
            player1_discard_size=player1_discard_size,
            player2_discard_size=player2_discard_size,
            tech_bay_size=tech_bay_size,
            derelict_cache_size=derelict_cache_size,
            phase=phase
        )
        
        self.states.append(state)
        
    def log_outcome(self, winner: Optional[str], is_draw: bool):
        outcome = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "winner": winner,
            "is_draw": is_draw,
            "total_turns": len(self.states)
        }
        
        # Write all states to the log file
        with open(self.log_file, 'a') as f:
            for state in self.states:
                f.write(json.dumps(asdict(state)) + '\n')
        
        # Write outcome to the outcome file
        with open(self.outcome_file, 'a') as f:
            f.write(json.dumps(outcome) + '\n')
        
        # Clear states for next game
        self.states = []
        self.session_id = str(uuid.uuid4()) 