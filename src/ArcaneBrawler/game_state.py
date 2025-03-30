from typing import List, Optional, Tuple
from enum import Enum

from player import Player, Archetype
from card import Card, Suit
import random

class Phase(Enum):
    BEGINNING = "Beginning"
    MAIN1 = "Main1"
    COMBAT = "Combat"
    MAIN2 = "Main2"
    END = "End"

class GameState:
    def __init__(self):
        self.players: List[Player] = []
        self.current_player_index = 0
        self.phase = Phase.BEGINNING
        self.turn_number = 1
        self.game_over = False
        self.winner: Optional[Player] = None
        self.last_played_cards: List[Card] = []  # Track cards played this turn for combo effects
        
    def add_player(self, player: Player) -> None:
        """Add a player to the game."""
        if len(self.players) < 2:
            self.players.append(player)
        else:
            raise ValueError("Game can only have 2 players")
    
    def get_current_player(self) -> Player:
        """Get the current active player."""
        return self.players[self.current_player_index]
    
    def get_opponent(self) -> Player:
        """Get the opponent of the current player."""
        return self.players[1 - self.current_player_index]
    
    def start_game(self) -> None:
        """Initialize the game."""
        if len(self.players) != 2:
            raise ValueError("Game requires exactly 2 players")
            
        # Each player draws 7 cards
        for player in self.players:
            player.draw_cards(7)
    
    def advance_phase(self) -> None:
        """Advance to the next phase of the turn."""
        phases = list(Phase)
        current_index = phases.index(self.phase)
        next_index = (current_index + 1) % len(phases)
        
        self.phase = phases[next_index]
        
        # Handle phase-specific effects
        if self.phase == Phase.BEGINNING:
            self.get_current_player().start_turn()
        elif self.phase == Phase.END:
            self.get_current_player().end_turn()
            self.current_player_index = 1 - self.current_player_index
            self.turn_number += 1
    
    def check_game_over(self) -> bool:
        """Check if the game is over and determine the winner."""
        for player in self.players:
            if player.health <= 0:
                self.game_over = True
                self.winner = self.get_opponent()
                return True
        return False
    
    def resolve_combat(self, attacker: Card, blocker: Optional[Card] = None) -> None:
        """Resolve combat between cards."""
        current_player = self.get_current_player()
        opponent = self.get_opponent()
        
        if blocker:
            # Both creatures take damage equal to each other's power
            attacker_power = attacker.face_value()
            blocker_power = blocker.face_value()
            
            # Apply archetype-specific combat modifiers
            if current_player.archetype == Archetype.BERSERKER:
                attacker_power += current_player.rage_counters
            elif current_player.archetype == Archetype.COMMANDER:
                attacker_power += len(current_player.tokens)
            
            # Deal damage
            blocker.health -= attacker_power
            attacker.health -= blocker_power
            
            # Check for destroyed creatures
            if blocker.health <= 0:
                opponent.field.remove(blocker)
                opponent.discard.append(blocker)
            if attacker.health <= 0:
                current_player.field.remove(attacker)
                current_player.discard.append(attacker)
        else:
            # Direct attack to opponent
            damage = attacker.face_value()
            if current_player.archetype == Archetype.BERSERKER:
                damage += current_player.rage_counters
            opponent.health -= damage
    
    def check_poker_hand(self, cards: List[Card]) -> Tuple[str, int]:
        """Check if cards form a poker hand and return the hand type and bonus value."""
        if len(cards) < 2:
            return "None", 0
            
        values = [card.face_value() for card in cards]
        suits = [card.suit for card in cards]
        
        # Check for pairs
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
            
        # Check for straights
        sorted_values = sorted(set(values))
        is_straight = len(sorted_values) >= 5 and max(sorted_values) - min(sorted_values) == 4
        
        # Check for flushes
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        is_flush = max(suit_counts.values()) >= 5
        
        # Determine hand type and bonus
        if is_straight and is_flush:
            return "Royal Flush", 12
        elif is_straight:
            return "Straight", 5
        elif is_flush:
            return "Flush", 4
        elif 4 in value_counts.values():
            return "Four of a Kind", 8
        elif 3 in value_counts.values() and 2 in value_counts.values():
            return "Full House", 10
        elif 3 in value_counts.values():
            return "Three of a Kind", 3
        elif list(value_counts.values()).count(2) == 2:
            return "Two Pair", 2
        elif 2 in value_counts.values():
            return "Pair", 1
            
        return "None", 0
    
    def resolve_spell(self, caster: Player, spell: Card, target: Optional[Card] = None) -> None:
        """Resolve a spell effect based on the archetype."""
        self.last_played_cards.append(spell)
        hand_type, bonus = self.check_poker_hand(self.last_played_cards)
        
        # Apply bonus to spell effects
        if caster.archetype == Archetype.CULTIVATOR:
            if spell.suit == Suit.CLUBS:
                # Resource generation
                caster.growth_tokens += 1 + bonus
                print(f"{caster.name} gains {1 + bonus} Growth Token(s) (+{1 + bonus} mana next turn)")
                if hand_type == "Flush":
                    caster.growth_tokens += 2
                    print("Flush bonus: +2 additional Growth Tokens!")
            elif spell.suit == Suit.SPADES:
                # Persistent effects
                caster.max_mana += 1 + bonus
                print(f"{caster.name} increases max mana by {1 + bonus}")
                if hand_type == "Straight":
                    caster.max_mana += 1
                    print("Straight bonus: +1 additional max mana!")
            elif spell.suit == Suit.HEARTS:
                # Healing and protection
                heal_amount = spell.face_value() * (1 + bonus)
                caster.health = min(caster.max_health, caster.health + heal_amount)
                print(f"{caster.name} heals for {heal_amount}")
            elif spell.suit == Suit.DIAMONDS:
                # Card advantage
                caster.draw_cards(2 + bonus)
                print(f"{caster.name} draws {2 + bonus} cards")
                
        elif caster.archetype == Archetype.BERSERKER:
            if spell.suit == Suit.HEARTS:
                # Direct damage
                base_damage = spell.face_value()
                rage_bonus = caster.rage_counters
                total_damage = base_damage * (1 + rage_bonus + bonus)
                opponent = self.get_opponent()
                opponent.health -= total_damage
                print(f"{caster.name} deals {total_damage} damage! (Base: {base_damage}, Rage: {rage_bonus}, Combo: {bonus})")
            elif spell.suit == Suit.DIAMONDS:
                # Rage generation
                caster.rage_counters += 1 + bonus
                print(f"{caster.name} gains {1 + bonus} Rage counter(s)")
            elif spell.suit == Suit.CLUBS:
                # Self-damage for power
                self_damage = spell.face_value() // 2
                caster.health -= self_damage
                caster.rage_counters += 2 + bonus
                print(f"{caster.name} takes {self_damage} damage to gain {2 + bonus} Rage counters")
            elif spell.suit == Suit.SPADES:
                # Combat tricks
                if target:
                    target.tapped = True
                    print(f"{target} is tapped")
                
        elif caster.archetype == Archetype.MYSTIC:
            if spell.suit == Suit.DIAMONDS:
                # Spell mastery
                caster.spell_count += 1 + bonus
                if target:
                    target.tapped = True
                print(f"{caster.name} gains {1 + bonus} Spell counter(s)")
            elif spell.suit == Suit.SPADES:
                # Card manipulation
                caster.draw_cards(2 + bonus)
                if len(caster.hand) > 7:
                    discard_count = len(caster.hand) - 7
                    for _ in range(discard_count):
                        caster.discard_card(caster.hand[0])
                print(f"{caster.name} draws {2 + bonus} cards and discards excess")
            elif spell.suit == Suit.HEARTS:
                # Counter effects
                if target:
                    target.tapped = True
                    print(f"{target} is countered and tapped")
            elif spell.suit == Suit.CLUBS:
                # Hand disruption
                opponent = self.get_opponent()
                for _ in range(1 + bonus):
                    if opponent.hand:
                        card = random.choice(opponent.hand)
                        opponent.discard_card(card)
                        print(f"{opponent.name} discards {card}")
                
        elif caster.archetype == Archetype.TRICKSTER:
            if spell.suit == Suit.CLUBS:
                # Hand disruption
                opponent = self.get_opponent()
                for _ in range(1 + bonus):
                    if opponent.hand:
                        card = random.choice(opponent.hand)
                        opponent.discard_card(card)
                        caster.disruption_count += 1
                        print(f"{opponent.name} discards {card}")
            elif spell.suit == Suit.HEARTS:
                # Life manipulation
                caster.disruption_count += 1 + bonus
                opponent = self.get_opponent()
                life_swap = min(5, caster.disruption_count)
                caster.health, opponent.health = opponent.health, caster.health
                print(f"{caster.name} swaps life totals with {opponent.name}")
            elif spell.suit == Suit.DIAMONDS:
                # Mana disruption
                opponent = self.get_opponent()
                stolen_mana = min(2 + bonus, opponent.mana)
                opponent.mana -= stolen_mana
                caster.mana += stolen_mana
                print(f"{caster.name} steals {stolen_mana} mana from {opponent.name}")
            elif spell.suit == Suit.SPADES:
                # Card theft
                opponent = self.get_opponent()
                for _ in range(1 + bonus):
                    if opponent.hand:
                        card = random.choice(opponent.hand)
                        opponent.hand.remove(card)
                        caster.hand.append(card)
                        print(f"{caster.name} steals {card} from {opponent.name}")
                
        elif caster.archetype == Archetype.COMMANDER:
            if spell.suit == Suit.HEARTS:
                # Token generation
                for _ in range(1 + bonus):
                    squire = Card(Suit.HEARTS, "2")
                    caster.tokens.append(squire)
                    caster.squire_count += 1
                print(f"{caster.name} creates {1 + bonus} Squire token(s)")
            elif spell.suit == Suit.SPADES:
                # Token buffing
                buff_amount = spell.face_value() // 2 * (1 + bonus)
                for token in caster.tokens:
                    # Implementation would depend on how we track token stats
                    pass
                print(f"{caster.name} buffs all tokens by {buff_amount}")
            elif spell.suit == Suit.CLUBS:
                # Token protection
                for token in caster.tokens:
                    # Implementation would depend on how we track token stats
                    pass
                print(f"{caster.name} protects all tokens")
            elif spell.suit == Suit.DIAMONDS:
                # Token synergy
                if caster.tokens:
                    caster.draw_cards(len(caster.tokens) * (1 + bonus))
                    print(f"{caster.name} draws {len(caster.tokens) * (1 + bonus)} cards for token synergy")
        
        # Clear last played cards at end of turn
        if self.phase == Phase.END:
            self.last_played_cards.clear() 