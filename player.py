from typing import List
from card import Card

class Player:
    def __init__(self, name: str):
        self.name = name
        self.deck = Card.create_starter_deck()
        self.discard_pile: List[Card] = []
        self.hand: List[Card] = []
        self.hull = 15
        self.shield = 0  # shield points carried over from previous turn

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