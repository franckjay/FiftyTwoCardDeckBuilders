from dataclasses import dataclass
from typing import Dict

@dataclass
class Card:
    suit: str  # "Clubs", "Diamonds", "Hearts", "Spades"
    rank: str  # "2"-"10", "J", "Q", "K", "A"
    
    # Class-level constants
    SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
    RANKS = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]
    FACE_VALUES = {str(n): n for n in range(2, 11)}
    FACE_VALUES.update({"J": 5, "Q": 6, "K": 7, "A": 8})
    SUIT_SYMBOLS = {"Clubs": "♣", "Diamonds": "♦", "Hearts": "♥", "Spades": "♠"}
    
    def face_value(self) -> int:
        """Returns the face value of the card."""
        return self.FACE_VALUES.get(self.rank, 0)
    
    def __str__(self) -> str:
        """Returns a string representation of the card."""
        return f"{self.rank}{self.SUIT_SYMBOLS.get(self.suit, self.suit)}"
    
    @classmethod
    def create_standard_deck(cls) -> list['Card']:
        """Creates and returns a shuffled standard 52-card deck."""
        import random
        deck = [cls(suit, rank) for suit in cls.SUITS for rank in cls.RANKS]
        random.shuffle(deck)
        return deck
    
    @classmethod
    def create_starter_deck(cls) -> list['Card']:
        """Creates and returns a shuffled starter deck (7 Engineers, 3 Marines)."""
        import random
        starter = ([cls("Clubs", "2") for _ in range(7)] + 
                  [cls("Spades", "2") for _ in range(3)])
        random.shuffle(starter)
        return starter 