from typing import List, Optional
from card import Card
from src.common.player import Player

class GameState:
    def __init__(self, difficulty: str = "normal"):
        self.monster_discard: List[Card] = []  # Global discard pile for monsters
        self.monster_deck: List[Card] = Card.create_standard_deck()
        self.treasure_room: List[Optional[Card]] = []
        self.current_monster: Optional[Card] = None
        self._initialize_treasure_room()
        self._draw_new_monster()
        self.difficulty = difficulty

    def _initialize_treasure_room(self) -> None:
        """Initializes the Treasure Room with 5 random cards from the Monster Deck."""
        for _ in range(5):
            self.treasure_room.append(self.draw_from_monster_deck())

    def draw_from_monster_deck(self) -> Optional[Card]:
        """Draws a card from the Monster Deck, recycling discards if needed."""
        if self.monster_deck:
            return self.monster_deck.pop(0)
        else:
            if self.monster_discard:
                print("Recycling monster discards back into the Monster Deck.")
                import random
                random.shuffle(self.monster_discard)
                self.monster_deck.extend(self.monster_discard)
                self.monster_discard.clear()
                if self.monster_deck:
                    return self.monster_deck.pop(0)
            return None

    def _draw_new_monster(self) -> None:
        """Draws a new monster from the deck."""
        self.current_monster = self.draw_from_monster_deck()
        if self.current_monster:
            print(f"A new monster appears: {self.current_monster} (Health: {self.current_monster.face_value()})")

    def refill_treasure_slot(self, index: int) -> None:
        """Refills an empty Treasure Room slot with a new card from the deck."""
        new_card = self.draw_from_monster_deck()
        self.treasure_room[index] = new_card

    def get_treasure_room_size(self) -> int:
        """Returns the number of non-empty slots in the Treasure Room."""
        return len([c for c in self.treasure_room if c is not None])

    def get_monster_deck_size(self) -> int:
        """Returns the number of cards in the Monster Deck."""
        return len(self.monster_deck)

    def add_to_monster_discard(self, cards: List[Card]) -> None:
        """Adds cards to the monster discard pile."""
        self.monster_discard.extend(cards)

    def deal_monster_damage(self, player1: Player, player2: Player) -> None:
        """Deals damage from the current monster to both players."""
        if not self.current_monster:
            return

        damage = self.current_monster.face_value()
        print(f"\nThe monster deals {damage} damage to both players!")

        # Deal damage to player 1
        if player1.temp_health > 0:
            if player1.temp_health >= damage:
                player1.temp_health -= damage
                print(f"{player1.name}'s temporary health absorbs all damage. (Remaining: {player1.temp_health})")
                damage = 0
            else:
                print(f"{player1.name}'s temporary health absorbs {player1.temp_health} damage.")
                damage -= player1.temp_health
                player1.temp_health = 0

        if damage > 0:
            player1.health -= damage
            print(f"{player1.name}'s health is now {player1.health}.")

        # Deal damage to player 2
        if player2.temp_health > 0:
            if player2.temp_health >= damage:
                player2.temp_health -= damage
                print(f"{player2.name}'s temporary health absorbs all damage. (Remaining: {player2.temp_health})")
                damage = 0
            else:
                print(f"{player2.name}'s temporary health absorbs {player2.temp_health} damage.")
                damage -= player2.temp_health
                player2.temp_health = 0

        if damage > 0:
            player2.health -= damage
            print(f"{player2.name}'s health is now {player2.health}.")

    def check_monster_defeated(self) -> bool:
        """Checks if the current monster is defeated and draws a new one if needed."""
        if not self.current_monster:
            return False

        if self.current_monster.health <= 0:
            print(f"\nThe monster is defeated!")
            self.monster_discard.append(self.current_monster)
            self._draw_new_monster()
            return True
        return False

    def get_starting_health(self) -> int:
        """Returns the starting health based on difficulty level."""
        health_map = {
            "easy": 25,
            "normal": 20,
            "hard": 15
        }
        return health_map.get(self.difficulty.lower(), 20) 