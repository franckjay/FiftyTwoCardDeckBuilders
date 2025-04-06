import pytest
import random
from main import Game, Player, Unit, Board  # Import classes from your main file
import BirdsOfPray.card_data as card_data  # Import constants and card data

# --- Fixtures ---

@pytest.fixture(scope="function") # Re-run setup for each test function
def game_instance(monkeypatch):
    """
    Provides a fully initialized Game instance for testing.
    Mocks input() to prevent tests from hanging during setup.
    """
    # Mock the input function to automatically proceed through setup prompts
    monkeypatch.setattr('builtins.input', lambda _: "") # Return empty string for any input prompt

    # Ensure predictable champion selection for some tests if needed,
    # otherwise allow random selection as per original setup.
    # For consistency, let's force specific Aces for testing placement:
    original_shuffle = random.shuffle
    def predictable_shuffle(x):
        # Make AC and AH the first two aces for predictable assignment
        if all(a in x for a in ['AC', 'AH', 'AD', 'AS']):
             x[:] = ['AC', 'AH', 'AD', 'AS'] # Force order
        else:
             original_shuffle(x) # Shuffle other lists normally
    monkeypatch.setattr(random, 'shuffle', predictable_shuffle)

    game = Game()
    game.setup_game() # Run the setup process

    # Restore original shuffle if necessary (though scope="function" handles cleanup)
    # monkeypatch.undo() # Usually handled by pytest fixture teardown

    return game

# --- Test Cases ---

def test_game_initialization(game_instance):
    """Tests if the Game object and basic structures are created."""
    assert isinstance(game_instance, Game)
    assert isinstance(game_instance.board, Board)
    assert isinstance(game_instance.players, dict)
    assert len(game_instance.players) == 2

def test_player_creation_and_champions(game_instance):
    """Tests if players are created correctly with their champions."""
    assert 1 in game_instance.players
    assert 2 in game_instance.players
    player1 = game_instance.players[1]
    player2 = game_instance.players[2]
    assert isinstance(player1, Player)
    assert isinstance(player2, Player)
    assert player1.id == 1
    assert player2.id == 2
    # Check if champions were assigned (using the predictable shuffle)
    assert player1.champion_code == 'AC' # Based on predictable_shuffle mock
    assert player2.champion_code == 'AH' # Based on predictable_shuffle mock
    assert player1.champion_code in card_data.CARD_DATA
    assert player2.champion_code in card_data.CARD_DATA
    assert card_data.get_card_data(player1.champion_code)['type'] == 'Champion'
    assert card_data.get_card_data(player2.champion_code)['type'] == 'Champion'

def test_starting_food(game_instance):
    """Tests if players start with the correct amount of food."""
    assert game_instance.players[1].food == card_data.STARTING_FOOD
    assert game_instance.players[2].food == card_data.STARTING_FOOD

def test_starting_hand_size(game_instance):
    """Tests if players draw the correct number of cards initially."""
    assert len(game_instance.players[1].hand) == card_data.STARTING_HAND_SIZE
    assert len(game_instance.players[2].hand) == card_data.STARTING_HAND_SIZE

def test_initial_deck_size(game_instance):
    """
    Tests if the total number of cards in deck + hands is correct.
    Expected: 52 total - 4 unchosen Aces - 8x'2' - 8x'3' - 4x'4' = 28 cards?
    Let's re-read rules: "Shuffle the remaining deck (Aces, 5s through Kings - 44 cards total)"
    This implies the 2 chosen Aces ARE in the deck/hands pool.
    So, 52 - 2 unchosen Aces - 8x'2' - 8x'3' - 4x'4' = 30 cards?
    Let's trust the rule description's final count: 44 cards (2 Aces + 40 number/face 5-K)
    """
    total_cards_in_play = (
        len(game_instance.deck) +
        len(game_instance.players[1].hand) +
        len(game_instance.players[2].hand)
    )
    # The 44 cards are: 2 chosen Aces, 4x Jacks, 4x Queens, 4x Kings, 6x number cards (5-10) * 4 suits = 24
    # 2 + 4 + 4 + 4 + 24 = 38 cards. Where did 44 come from?
    # Ah, 5, 6, 7, 8, 9, 10 = 6 ranks. 6 * 4 suits = 24 number cards.
    # J, Q, K = 3 ranks. 3 * 4 suits = 12 face cards.
    # 2 chosen Aces.
    # Total = 24 + 12 + 2 = 38 cards.
    # The rule description "44 cards total" might be slightly off, or my interpretation.
    # Let's test against the 38 calculated based on ranks 5-K + 2 Aces.
    expected_deck_pool_size = 38
    assert total_cards_in_play == expected_deck_pool_size
    assert len(game_instance.deck) == expected_deck_pool_size - (card_data.STARTING_HAND_SIZE * 2)

def test_champion_placement(game_instance):
    """Tests if champions are placed correctly on the board."""
    p1_start_pos = (game_instance.board.width // 2, game_instance.board.height - 1)
    p2_start_pos = (game_instance.board.width // 2, 0)

    champ1_obj = game_instance.board.get_at_pos(p1_start_pos)
    champ2_obj = game_instance.board.get_at_pos(p2_start_pos)

    assert isinstance(champ1_obj, Unit)
    assert isinstance(champ2_obj, Unit)

    assert champ1_obj.owner_id == 1
    assert champ2_obj.owner_id == 2

    # Using predictable shuffle from fixture
    assert champ1_obj.card_code == 'AC'
    assert champ2_obj.card_code == 'AH'

    assert champ1_obj.position == p1_start_pos
    assert champ2_obj.position == p2_start_pos

    # Check if they are also tracked in player's units_on_board
    assert any(unit == champ1_obj for unit in game_instance.players[1].units_on_board.values())
    assert any(unit == champ2_obj for unit in game_instance.players[2].units_on_board.values())


def test_terrain_and_cache_presence(game_instance):
    """Tests if some terrain and food caches were placed on the board."""
    board_objects = game_instance.board.grid.values()

    has_low_cover = any(obj == '2' for obj in board_objects)
    has_heavy_cover = any(obj == '3' for obj in board_objects)
    has_food_cache = any(obj == '4' for obj in board_objects)

    # Due to random placement, we only check for presence, not exact count/location
    assert has_low_cover, "Board should have at least one Low Cover ('2')"
    assert has_heavy_cover, "Board should have at least one Heavy Cover ('3')"
    assert has_food_cache, "Board should have at least one Food Cache ('4')"

    # Also check they are not placed in starting rows (simplified check)
    start_row_y_p1 = game_instance.board.height - 1
    start_row_y_p2 = 0
    for pos, obj in game_instance.board.grid.items():
        if obj in ['2', '3', '4']:
            assert pos[1] != start_row_y_p1, f"Terrain/Cache found in P1 start row at {pos}"
            assert pos[1] != start_row_y_p2, f"Terrain/Cache found in P2 start row at {pos}"


def test_no_invalid_cards_in_deck_hand(game_instance):
    """Checks if all cards in deck and hands are valid card codes."""
    all_cards = game_instance.deck + game_instance.players[1].hand + game_instance.players[2].hand
    for card_code in all_cards:
        assert card_code in card_data.CARD_DATA, f"Invalid card code '{card_code}' found in deck/hand."
        card_info = card_data.get_card_data(card_code)
        # Ensure these cards are not terrain/caches/unchosen aces
        assert card_info['rank'] not in ['2', '3', '4']
        assert card_info['type'] in ['Champion', 'Unit'] or card_info['rank'] in ['5','6','7','8','9','T']


def test_initial_unit_ids(game_instance):
    """Checks if the initial champions have unique IDs assigned."""
    p1_units = list(game_instance.players[1].units_on_board.keys())
    p2_units = list(game_instance.players[2].units_on_board.keys())
    assert len(p1_units) == 1
    assert len(p2_units) == 1
    assert p1_units[0].startswith('u') # Check prefix convention
    assert p2_units[0].startswith('u')
    assert p1_units[0] != p2_units[0] # Ensure they are different