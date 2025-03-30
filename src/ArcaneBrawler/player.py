from typing import List
from enum import Enum

from card import Card, Suit
import random

class Archetype(Enum):
    CULTIVATOR = "Cultivator"
    BERSERKER = "Berserker"
    MYSTIC = "Mystic"
    TRICKSTER = "Trickster"
    COMMANDER = "Commander"

class Player:
    def __init__(self, name: str, archetype: Archetype):
        self.name = name
        self.archetype = archetype
        self.health = 20
        self.max_health = 20
        self.mana = 0
        self.max_mana = 0
        self.hand: List[Card] = []
        self.deck: List[Card] = Card.create_standard_deck()
        self.discard: List[Card] = []
        self.field: List[Card] = []  # Cards in play
        self.tokens: List[Card] = []  # Special tokens (e.g., Growth Tokens, Squires)
        self.turn_number = 0
        
        # Archetype-specific attributes
        self.growth_tokens = 0  # Cultivator
        self.rage_counters = 0  # Berserker
        self.spell_count = 0    # Mystic
        self.disruption_count = 0  # Trickster
        self.squire_count = 0   # Commander
        
        # Shuffle the deck
        random.shuffle(self.deck)
    
    def draw_cards(self, amount: int = 1) -> None:
        """Draw cards from deck, reshuffling discard if needed."""
        for _ in range(amount):
            if not self.deck:
                if self.discard:
                    self.deck.extend(self.discard)
                    self.discard.clear()
                    random.shuffle(self.deck)
                else:
                    return  # No cards to draw
            
            self.hand.append(self.deck.pop())
    
    def discard_card(self, card: Card) -> None:
        """Move a card from hand to discard pile."""
        if card in self.hand:
            self.hand.remove(card)
            self.discard.append(card)
    
    def play_card(self, card: Card) -> bool:
        """Attempt to play a card from hand."""
        if card not in self.hand or self.mana < card.mana_cost:
            return False
            
        self.mana -= card.mana_cost
        self.hand.remove(card)
        self.field.append(card)
        return True
    
    def get_hand_size(self) -> int:
        return len(self.hand)
    
    def get_deck_size(self) -> int:
        return len(self.deck)
    
    def get_discard_size(self) -> int:
        return len(self.discard)
    
    def get_field_size(self) -> int:
        return len(self.field)
    
    def get_token_count(self) -> int:
        return len(self.tokens)
    
    def can_play_card(self, card: Card) -> bool:
        """Check if a card can be played with current mana."""
        return card in self.hand and self.mana >= card.mana_cost
    
    def start_turn(self) -> None:
        """Handle start of turn effects."""
        self.turn_number += 1
        self.max_mana = min(10, self.turn_number)
        self.mana = self.max_mana
        
        # Archetype-specific start of turn effects
        if self.archetype == Archetype.CULTIVATOR:
            self.mana += self.growth_tokens
        elif self.archetype == Archetype.BERSERKER:
            self.rage_counters = min(3, self.rage_counters + 1)
        elif self.archetype == Archetype.MYSTIC:
            self.spell_count = 0
        elif self.archetype == Archetype.TRICKSTER:
            self.disruption_count = 0
        elif self.archetype == Archetype.COMMANDER:
            # Commander gets +1/+1 to all tokens at start of turn
            for token in self.tokens:
                # Implementation would depend on how we track token stats
                pass
    
    def end_turn(self) -> None:
        """Handle end of turn effects."""
        # Discard down to 7 cards if needed
        while len(self.hand) > 7:
            self.discard_card(self.hand[0])
        
        # Clear temporary effects
        for card in self.field:
            card.tapped = False 