import unittest
from game_state import GameState, Phase
from player import Player, Archetype
from card import Card, Suit

class TestArcaneBrawler(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        self.player1 = Player("Player1", Archetype.CULTIVATOR)
        self.player2 = Player("Player2", Archetype.BERSERKER)
        self.game_state.add_player(self.player1)
        self.game_state.add_player(self.player2)
        self.game_state.start_game()

    def test_game_initialization(self):
        """Test that the game initializes correctly."""
        self.assertEqual(len(self.game_state.players), 2)
        self.assertEqual(self.game_state.current_player_index, 0)
        self.assertEqual(self.game_state.phase, Phase.BEGINNING)
        self.assertEqual(self.game_state.turn_number, 1)
        self.assertFalse(self.game_state.game_over)
        self.assertIsNone(self.game_state.winner)
        
        # Check initial player states
        self.assertEqual(self.player1.get_hand_size(), 7)
        self.assertEqual(self.player2.get_hand_size(), 7)
        self.assertEqual(self.player1.health, 20)
        self.assertEqual(self.player2.health, 20)

    def test_cultivator_effects(self):
        """Test Cultivator archetype effects."""
        # Test resource generation
        clubs_card = Card(Suit.CLUBS, "2")
        self.player1.hand.append(clubs_card)
        self.game_state.resolve_spell(self.player1, clubs_card)
        self.assertEqual(self.player1.growth_tokens, 1)
        
        # Test healing
        hearts_card = Card(Suit.HEARTS, "5")
        self.player1.health = 15
        self.player1.hand.append(hearts_card)
        self.game_state.resolve_spell(self.player1, hearts_card)
        self.assertEqual(self.player1.health, 20)
        
        # Test mana increase
        spades_card = Card(Suit.SPADES, "3")
        self.player1.hand.append(spades_card)
        self.game_state.resolve_spell(self.player1, spades_card)
        self.assertEqual(self.player1.max_mana, 1)

    def test_berserker_effects(self):
        """Test Berserker archetype effects."""
        # Test rage generation
        diamonds_card = Card(Suit.DIAMONDS, "4")
        self.player2.hand.append(diamonds_card)
        self.game_state.resolve_spell(self.player2, diamonds_card)
        self.assertEqual(self.player2.rage_counters, 1)
        
        # Test direct damage
        hearts_card = Card(Suit.HEARTS, "5")
        self.player2.hand.append(hearts_card)
        self.game_state.resolve_spell(self.player2, hearts_card)
        self.assertEqual(self.player1.health, 15)  # 20 - (5 * 1)
        
        # Test self-damage for power
        clubs_card = Card(Suit.CLUBS, "6")
        self.player2.hand.append(clubs_card)
        self.game_state.resolve_spell(self.player2, clubs_card)
        self.assertEqual(self.player2.health, 17)  # 20 - (6/2)
        self.assertEqual(self.player2.rage_counters, 3)  # 1 + 2

    def test_mystic_effects(self):
        """Test Mystic archetype effects."""
        mystic = Player("Mystic", Archetype.MYSTIC)
        self.game_state.players[0] = mystic
        
        # Test spell counter
        diamonds_card = Card(Suit.DIAMONDS, "3")
        mystic.hand.append(diamonds_card)
        self.game_state.resolve_spell(mystic, diamonds_card)
        self.assertEqual(mystic.spell_count, 1)
        
        # Test card draw
        spades_card = Card(Suit.SPADES, "4")
        mystic.hand.append(spades_card)
        initial_hand_size = mystic.get_hand_size()
        self.game_state.resolve_spell(mystic, spades_card)
        self.assertEqual(mystic.get_hand_size(), min(initial_hand_size + 1, 7))

    def test_trickster_effects(self):
        """Test Trickster archetype effects."""
        trickster = Player("Trickster", Archetype.TRICKSTER)
        self.game_state.players[0] = trickster
        
        # Test hand disruption
        clubs_card = Card(Suit.CLUBS, "2")
        self.player2.hand.append(clubs_card)
        trickster.hand.append(clubs_card)
        initial_hand_size = self.player2.get_hand_size()
        self.game_state.resolve_spell(trickster, clubs_card)
        self.assertEqual(self.player2.get_hand_size(), initial_hand_size - 1)
        self.assertEqual(trickster.disruption_count, 1)
        
        # Test life swap
        hearts_card = Card(Suit.HEARTS, "3")
        trickster.health = 10
        self.player2.health = 20
        trickster.hand.append(hearts_card)
        self.game_state.resolve_spell(trickster, hearts_card)
        self.assertEqual(trickster.health, 20)
        self.assertEqual(self.player2.health, 10)

    def test_commander_effects(self):
        """Test Commander archetype effects."""
        commander = Player("Commander", Archetype.COMMANDER)
        self.game_state.players[0] = commander
        
        # Test token generation
        hearts_card = Card(Suit.HEARTS, "2")
        commander.hand.append(hearts_card)
        self.game_state.resolve_spell(commander, hearts_card)
        self.assertEqual(len(commander.tokens), 1)
        self.assertEqual(commander.squire_count, 1)
        
        # Test token synergy
        diamonds_card = Card(Suit.DIAMONDS, "4")
        commander.hand.append(diamonds_card)
        initial_hand_size = commander.get_hand_size()
        self.game_state.resolve_spell(commander, diamonds_card)
        self.assertEqual(commander.get_hand_size(), initial_hand_size + 1)

    def test_poker_hand_detection(self):
        """Test poker hand detection and bonuses."""
        # Test pair
        cards = [Card(Suit.HEARTS, "2"), Card(Suit.DIAMONDS, "2")]
        hand_type, bonus = self.game_state.check_poker_hand(cards)
        self.assertEqual(hand_type, "Pair")
        self.assertEqual(bonus, 3)
        
        # Test straight
        cards = [Card(Suit.HEARTS, "2"), Card(Suit.DIAMONDS, "3"), 
                Card(Suit.CLUBS, "4"), Card(Suit.SPADES, "5"), 
                Card(Suit.HEARTS, "6")]
        hand_type, bonus = self.game_state.check_poker_hand(cards)
        self.assertEqual(hand_type, "Straight")
        self.assertEqual(bonus, 20)
        
        # Test flush
        cards = [Card(Suit.HEARTS, "2"), Card(Suit.HEARTS, "4"), 
                Card(Suit.HEARTS, "6"), Card(Suit.HEARTS, "8"), 
                Card(Suit.HEARTS, "10")]
        hand_type, bonus = self.game_state.check_poker_hand(cards)
        self.assertEqual(hand_type, "Flush")
        self.assertEqual(bonus, 15)

    def test_combat_resolution(self):
        """Test combat resolution between cards."""
        # Create test cards
        attacker = Card(Suit.HEARTS, "5")
        blocker = Card(Suit.DIAMONDS, "3")
        
        # Test combat with blocker
        self.game_state.resolve_combat(attacker, blocker)
        self.assertEqual(attacker.health, 2)  # 5 - 3
        self.assertEqual(blocker.health, 0)   # 3 - 5
        
        # Test direct attack
        self.player2.health = 20
        self.game_state.resolve_combat(attacker)
        self.assertEqual(self.player2.health, 15)  # 20 - 5

    def test_game_over_conditions(self):
        """Test game over conditions."""
        # Test player death
        self.player1.health = 0
        self.assertTrue(self.game_state.check_game_over())
        self.assertEqual(self.game_state.winner, self.player2)
        
        # Test game state
        self.assertTrue(self.game_state.game_over)
        self.assertEqual(self.game_state.winner, self.player2)

    def test_phase_advancement(self):
        """Test turn phase advancement."""
        # Test phase progression
        initial_phase = self.game_state.phase
        self.game_state.advance_phase()
        self.assertNotEqual(self.game_state.phase, initial_phase)
        
        # Test turn advancement
        self.game_state.phase = Phase.END
        self.game_state.advance_phase()
        self.assertEqual(self.game_state.phase, Phase.BEGINNING)
        self.assertEqual(self.game_state.current_player_index, 1)
        self.assertEqual(self.game_state.turn_number, 2)

if __name__ == '__main__':
    unittest.main() 