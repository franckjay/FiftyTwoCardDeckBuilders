from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class GameState:
    turn_number: int
    current_player: str
    player1_name: str
    player2_name: str
    player1_health: int
    player2_health: int
    player1_temp_health: int
    player2_temp_health: int
    player1_hand_size: int
    player2_hand_size: int
    player1_deck_size: int
    player2_deck_size: int
    player1_discard_size: int
    player2_discard_size: int
    treasure_room_size: int
    phase: str

class GameLogger:
    def __init__(self):
        self.states: List[GameState] = []
        self.outcome: Optional[Dict[str, Any]] = None
        self.start_time = datetime.now()

    def log_state(self, **kwargs) -> None:
        """Logs the current game state."""
        state = GameState(**kwargs)
        self.states.append(state)

    def log_outcome(self, winner: Optional[str], is_draw: bool) -> None:
        """Logs the game outcome."""
        self.outcome = {
            "winner": winner,
            "is_draw": is_draw,
            "end_time": datetime.now(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "total_turns": len(self.states) // 4  # Each turn has 4 state logs
        }

    def save_game_log(self, filename: Optional[str] = None) -> None:
        """Saves the game log to a JSON file."""
        if not filename:
            filename = f"game_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        log_data = {
            "start_time": self.start_time.isoformat(),
            "states": [
                {
                    "turn_number": state.turn_number,
                    "current_player": state.current_player,
                    "player1_name": state.player1_name,
                    "player2_name": state.player2_name,
                    "player1_health": state.player1_health,
                    "player2_health": state.player2_health,
                    "player1_temp_health": state.player1_temp_health,
                    "player2_temp_health": state.player2_temp_health,
                    "player1_hand_size": state.player1_hand_size,
                    "player2_hand_size": state.player2_hand_size,
                    "player1_deck_size": state.player1_deck_size,
                    "player2_deck_size": state.player2_deck_size,
                    "player1_discard_size": state.player1_discard_size,
                    "player2_discard_size": state.player2_discard_size,
                    "treasure_room_size": state.treasure_room_size,
                    "phase": state.phase
                }
                for state in self.states
            ],
            "outcome": self.outcome
        }

        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2) 