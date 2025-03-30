from enum import Enum
from typing import Optional

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Card:
    def __init__(self, suit: Suit, value: str):
        self.suit = suit
        self.value = value
        self.tapped = False
        self.mana_cost = self._get_mana_cost()
        self.health = self.face_value()  # Creatures have health equal to their face value
        self.is_creature = suit in [Suit.SPADES, Suit.HEARTS]  # Only Spades and Hearts are creatures
        
    def _get_mana_cost(self) -> int:
        """Convert card value to mana cost."""
        if self.value in ['J', 'Q', 'K']:
            return 10
        elif self.value == 'A':
            return 0  # Ace has variable cost
        return int(self.value)
    
    def face_value(self) -> int:
        """Get the numeric value of the card."""
        if self.value == 'A':
            return 11
        elif self.value in ['J', 'Q', 'K']:
            return 10
        return int(self.value)
    
    def __str__(self) -> str:
        return f"{self.value}{self.suit.value[0]}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @staticmethod
    def create_standard_deck() -> list['Card']:
        """Create a standard 52-card deck."""
        deck = []
        for suit in Suit:
            for value in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                deck.append(Card(suit, value))
        return deck 