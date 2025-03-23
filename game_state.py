from typing import List, Optional
from card import Card
from player import Player

class GameState:
    def __init__(self):
        self.cache_discard: List[Card] = []  # Global discard pile for tech search
        self.derelict_cache: List[Card] = Card.create_standard_deck()
        self.tech_bay: List[Optional[Card]] = []
        self._initialize_tech_bay()

    def _initialize_tech_bay(self) -> None:
        """Initializes the Tech Bay with 5 random cards from the Derelict Cache."""
        for _ in range(5):
            self.tech_bay.append(self.draw_from_cache())

    def draw_from_cache(self) -> Optional[Card]:
        """Draws a card from the Derelict Cache, recycling discards if needed."""
        if self.derelict_cache:
            return self.derelict_cache.pop(0)
        else:
            if self.cache_discard:
                print("Recycling tech search discards back into the Derelict Cache.")
                import random
                random.shuffle(self.cache_discard)
                self.derelict_cache.extend(self.cache_discard)
                self.cache_discard.clear()
                if self.derelict_cache:
                    return self.derelict_cache.pop(0)
            return None

    def refill_tech_bay_slot(self, index: int) -> None:
        """Refills an empty Tech Bay slot with a new card from the cache."""
        new_card = self.draw_from_cache()
        self.tech_bay[index] = new_card

    def get_tech_bay_size(self) -> int:
        """Returns the number of non-empty slots in the Tech Bay."""
        return len([c for c in self.tech_bay if c is not None])

    def get_derelict_cache_size(self) -> int:
        """Returns the number of cards in the Derelict Cache."""
        return len(self.derelict_cache)

    def add_to_cache_discard(self, cards: List[Card]) -> None:
        """Adds cards to the cache discard pile."""
        self.cache_discard.extend(cards)

    def calculate_attack_damage(self, spades_count: int) -> int:
        """Calculates the total damage from Marine maneuvers."""
        return (spades_count * (spades_count + 1)) // 2

    def calculate_repair_amount(self, hearts_count: int) -> int:
        """Calculates the total repair amount from Medic maneuvers."""
        if hearts_count == 0:
            return 0
        return 1 + (hearts_count - 1) * 2

    def apply_damage(self, attacker: Player, defender: Player, damage: int) -> None:
        """Applies damage to a player, considering shields."""
        if damage <= 0:
            return

        if defender.shield > 0:
            if defender.shield >= damage:
                defender.shield -= damage
                print(f"{defender.name}'s shield absorbed all the damage. (Remaining shield: {defender.shield})")
                damage = 0
            else:
                print(f"{defender.name}'s shield absorbed {defender.shield} damage.")
                damage -= defender.shield
                defender.shield = 0

        if damage > 0:
            defender.hull -= damage
            print(f"{defender.name}'s hull is now {defender.hull}.") 