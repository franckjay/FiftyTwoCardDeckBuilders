from typing import List, Optional
from card import Card

class Player:
    def __init__(self, name: str, character_class: str):
        self.name = name
        self.character_class = character_class
        self.deck = self._create_starter_deck()
        self.discard_pile: List[Card] = []
        self.hand: List[Card] = []
        self.health = 20  # Will be set by game state
        self.temp_health = 0  # Temporary health that resets each turn
        self.gold = 0
        self.special_ability_used = False

    def _create_starter_deck(self) -> List[Card]:
        """Creates the starter deck based on character class."""
        if self.character_class.lower() == "warrior":
            # 7 Weapons (2♠) and 3 Shields (2♥)
            starter = ([Card("Spades", "2") for _ in range(7)] + 
                      [Card("Hearts", "2") for _ in range(3)])
        else:  # Rogue
            # 7 Daggers (2♣) and 3 Potions (2♦)
            starter = ([Card("Clubs", "2") for _ in range(7)] + 
                      [Card("Diamonds", "2") for _ in range(3)])
        
        import random
        random.shuffle(starter)
        return starter

    def draw_cards(self, num: int) -> None:
        """Draws the specified number of cards from the deck."""
        for _ in range(num):
            if not self.deck:
                if self.discard_pile:
                    print(f"{self.name} is reshuffling the discard pile into the deck.")
                    self.deck = self.discard_pile
                    self.discard_pile = []
                    import random
                    random.shuffle(self.deck)
                else:
                    print(f"{self.name} has no cards left to draw!")
                    return
            self.hand.append(self.deck.pop(0))

    def discard_hand(self) -> None:
        """Discards all cards from hand to discard pile."""
        if self.hand:
            self.discard_pile.extend(self.hand)
            self.hand.clear()

    def add_to_discard(self, card: Card) -> None:
        """Adds a card to the discard pile."""
        self.discard_pile.append(card)

    def get_hand_size(self) -> int:
        """Returns the number of cards in hand."""
        return len(self.hand)

    def get_deck_size(self) -> int:
        """Returns the number of cards in deck."""
        return len(self.deck)

    def get_discard_size(self) -> int:
        """Returns the number of cards in discard pile."""
        return len(self.discard_pile)

    def use_special_ability(self, card: Card) -> bool:
        """Uses the character's special ability if available."""
        if self.special_ability_used:
            return False

        if self.character_class.lower() == "warrior":
            if card.suit == "Spades":  # Weapon
                self.special_ability_used = True
                return True
        else:  # Rogue
            if card.suit == "Diamonds":  # Potion
                self.special_ability_used = True
                return True
        
        return False

    def reset_turn(self) -> None:
        """Resets turn-specific values."""
        self.temp_health = 0
        self.gold = 0
        self.special_ability_used = False

    def heal(self, amount: int) -> None:
        """Heals the player by the specified amount."""
        self.health = min(self.health + amount, 20)  # Max health is 20
        print(f"{self.name} heals for {amount}. Health is now {self.health}.")

    def add_temp_health(self, amount: int) -> None:
        """Adds temporary health (max 5)."""
        self.temp_health = min(self.temp_health + amount, 5)
        print(f"{self.name} gains {amount} temporary health. Total: {self.temp_health}") 