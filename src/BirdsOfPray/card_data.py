# --- Game Constants ---

GRID_SIZE = (9, 9)  # Width, Height
MAX_ROUNDS = 8
STARTING_HAND_SIZE = 3
MAX_HAND_SIZE = 4
STARTING_FOOD = 2
BASE_FOOD_INCOME = 1  # Food gained at the start of each turn automatically
SUIT_RESOURCE_VALUE = 1 # Food generated by playing a 5-10 card for its suit

# --- Terrain & Resource Cache Definitions ---

TERRAIN_EFFECTS = {
    '2': {
        'name': "Low Cover",
        'description': "Provides minor protection.",
        'defense_bonus': 1, # Add this to unit's Defense when targeted
        'blocks_line_of_sight': False,
    },
    '3': {
        'name': "Heavy Cover",
        'description': "Provides significant protection and blocks line of sight.",
        'defense_bonus': 2, # Add this to unit's Defense when targeted
        'blocks_line_of_sight': True,
    }
}

RESOURCE_EFFECTS = {
    '4': {
        'name': "Food Cache",
        'description': "Consume as an action (1 AP) for a one-time Food bonus.",
        'food_bonus': 3,
    }
}

# --- Unit Card Data ---
# Structure: 'CardCode': { details }
# CardCode: RankSuit (e.g., 'AC' = Ace of Clubs, 'KH' = King of Hearts)

# --- CLUBS (Raptors - Warriors) ---
# Focus: Melee Combat, High HP/Attack

CARD_DATA = {
    # -- Champions (Aces) --
    'AC': {
        'name': "Eagle Warlord",
        'suit': 'Clubs', 'rank': 'Ace', 'type': 'Champion',
        'cost': 0, 'hp': 12, 'attack': 4, 'defense': 12, 'movement': 3, 'range': 1,
        'abilities': [
            {'name': "Fierce Strike", 'cost': '1 AP', 'description': "Make a melee attack with +1 Attack."},
            {'name': "Commander's Presence", 'cost': 'Passive', 'description': "Friendly Club units within 2 squares gain +1 Attack."},
            {'name': "Resilient", 'cost': 'Passive', 'description': "Starts with higher HP."},
        ]
    },
    'AH': {
        'name': "Dove Matriarch",
        'suit': 'Hearts', 'rank': 'Ace', 'type': 'Champion',
        'cost': 0, 'hp': 10, 'attack': 1, 'defense': 13, 'movement': 2, 'range': 1, # Range 1 for basic peck attack
        'abilities': [
            {'name': "Greater Heal", 'cost': '2 AP', 'range': 3, 'description': "Target friendly unit within range restores 4 HP."},
            {'name': "Aura of Mending", 'cost': 'Passive', 'range': 2, 'description': "At the start of your turn, friendly units within range restore 1 HP."},
            {'name': "Sanctuary", 'cost': '1 AP', 'range': 0, 'description': "This unit gains +2 Defense until the start of your next turn."},
        ]
    },
    'AD': {
        'name': "Great Horned Oracle",
        'suit': 'Diamonds', 'rank': 'Ace', 'type': 'Champion',
        'cost': 0, 'hp': 9, 'attack': 2, 'defense': 11, 'movement': 3, 'range': 4, # Ranged attack default
        'abilities': [
            {'name': "Arcane Bolt", 'cost': '1 AP', 'range': 4, 'description': "Make a ranged attack dealing standard damage."},
            {'name': "Precognitive Dodge", 'cost': 'Passive', 'description': "The first time this unit is attacked each round, the attacker suffers -1 to their attack roll."},
            {'name': "Focused Blast", 'cost': '2 AP', 'range': 5, 'description': "Make a ranged attack with +1 Attack and ignores Low Cover."},
        ]
    },
    'AS': {
        'name': "Quail Trailblazer",
        'suit': 'Spades', 'rank': 'Ace', 'type': 'Champion',
        'cost': 0, 'hp': 8, 'attack': 2, 'defense': 10, 'movement': 4, 'range': 1,
        'abilities': [
            {'name': "Resourceful Leader", 'cost': 'Passive', 'description': "Gain +1 base Food income each turn while this unit is on the board."},
            {'name': "Scout Ahead", 'cost': '1 AP', 'description': "Draw 1 card. Can only be used once per turn."},
            {'name': "Skirmish", 'cost': '1 AP', 'description': "Move up to 2 squares. Can be used after attacking."},
        ]
    },

    # -- Clubs Units (Face Cards) --
    'KC': {
        'name': "Gryphon Knight",
        'suit': 'Clubs', 'rank': 'King', 'type': 'Unit',
        'cost': 5, 'hp': 10, 'attack': 5, 'defense': 11, 'movement': 4, 'range': 1,
        'abilities': [
            {'name': "Devastating Charge", 'cost': 'Passive', 'description': "If this unit moved at least 3 squares before attacking this activation, gain +2 Attack for that attack."},
            {'name': "Flying", 'cost': 'Passive', 'description': "Ignores terrain and units for movement (but must land on empty square). Cannot benefit from ground cover."},
        ]
    },
    'QC': {
        'name': "Falcon Sentinel",
        'suit': 'Clubs', 'rank': 'Queen', 'type': 'Unit',
        'cost': 4, 'hp': 7, 'attack': 4, 'defense': 10, 'movement': 3, 'range': 1,
        'abilities': [
            {'name': "First Strike", 'cost': 'Passive', 'description': "When attacked in melee, if this unit survives, it may immediately attack the attacker back (once per round)."},
            {'name': "Precision Attack", 'cost': '1 AP', 'description': "Make a melee attack. On a hit, ignore 1 point of the target's cover bonus."},
        ]
    },
    'JC': {
        'name': "Hawk Squire",
        'suit': 'Clubs', 'rank': 'Jack', 'type': 'Unit',
        'cost': 3, 'hp': 6, 'attack': 3, 'defense': 9, 'movement': 3, 'range': 1,
        'abilities': [
            {'name': "Basic Melee", 'cost': '1 AP', 'description': "Perform a standard melee attack."},
        ]
    },

    # -- Hearts Units (Face Cards) --
    'KH': {
        'name': "Peacock Paladin",
        'suit': 'Hearts', 'rank': 'King', 'type': 'Unit',
        'cost': 5, 'hp': 9, 'attack': 2, 'defense': 13, 'movement': 2, 'range': 1,
        'abilities': [
            {'name': "Protective Ward", 'cost': '1 AP', 'range': 2, 'description': "Target friendly unit gains +2 Defense until the start of your next turn."},
            {'name': "Valiant Sacrifice", 'cost': 'Passive', 'description': "When this unit is defeated, choose another friendly unit within 3 squares to heal 4 HP."},
        ]
    },
    'QH': {
        'name': "Pigeon Cleric",
        'suit': 'Hearts', 'rank': 'Queen', 'type': 'Unit',
        'cost': 4, 'hp': 6, 'attack': 1, 'defense': 11, 'movement': 3, 'range': 1,
        'abilities': [
            {'name': "Heal", 'cost': '1 AP', 'range': 3, 'description': "Target friendly unit restores 3 HP."},
            {'name': "Purify", 'cost': '1 AP', 'range': 3, 'description': "Remove one negative status effect (e.g., Stun, Attack reduction) from target friendly unit."},
        ]
    },
    'JH': {
        'name': "Dove Acolyte",
        'suit': 'Hearts', 'rank': 'Jack', 'type': 'Unit',
        'cost': 3, 'hp': 5, 'attack': 1, 'defense': 10, 'movement': 3, 'range': 1,
        'abilities': [
            {'name': "Minor Heal", 'cost': '1 AP', 'range': 2, 'description': "Target friendly unit restores 2 HP."},
            {'name': "Sacrifice Fodder", 'cost': 'Passive', 'description': "When sacrificed for Food, yields +1 Food."},
        ]
    },

    # -- Diamonds Units (Face Cards) --
    'KD': {
        'name': "Vulture Necromancer",
        'suit': 'Diamonds', 'rank': 'King', 'type': 'Unit',
        'cost': 6, 'hp': 7, 'attack': 2, 'defense': 10, 'movement': 3, 'range': 3,
        'abilities': [
            {'name': "Raise Dead", 'cost': '2 AP', 'range': 1, 'description': "Target a non-Champion unit card in your discard pile with cost 3 or less. Place it onto an adjacent empty square with 1 HP."},
            {'name': "Withering Touch", 'cost': '1 AP', 'range': 3, 'description': "Make a ranged attack. If it hits, the target gets -1 Attack until the end of the next round."},
        ]
    },
    'QD': {
        'name': "Raven Shadowcaster",
        'suit': 'Diamonds', 'rank': 'Queen', 'type': 'Unit',
        'cost': 4, 'hp': 6, 'attack': 2, 'defense': 9, 'movement': 3, 'range': 4,
        'abilities': [
            {'name': "Shadow Bolt", 'cost': '1 AP', 'range': 4, 'description': "Make a standard ranged attack."},
            {'name': "Obscuring Mist", 'cost': '2 AP', 'range': 3, 'description': "Target an empty square within range. Place a temporary 'Mist' token there. It acts as Heavy Cover (blocks LoS, +2 Def) until the end of the next round."},
        ]
    },
    'JD': {
        'name': "Owl Scout",
        'suit': 'Diamonds', 'rank': 'Jack', 'type': 'Unit',
        'cost': 3, 'hp': 5, 'attack': 2, 'defense': 8, 'movement': 3, 'range': 4,
        'abilities': [
            {'name': "Ranged Shot", 'cost': '1 AP', 'range': 4, 'description': "Make a standard ranged attack."},
            {'name': "Keen Eyes", 'cost': 'Passive', 'description': "Ignores Low Cover when attacking."},
        ]
    },

    # -- Spades Units (Face Cards) --
    'KS': {
        'name': "Woodpecker Foreman",
        'suit': 'Spades', 'rank': 'King', 'type': 'Unit',
        'cost': 5, 'hp': 7, 'attack': 3, 'defense': 10, 'movement': 3, 'range': 1,
        'abilities': [
            {'name': "Resource Surge", 'cost': '2 AP', 'description': "Gain 3 Food immediately. Can only be used once per turn."},
            {'name': "Hardy Worker", 'cost': 'Passive', 'description': "Generates +1 Food at the start of your turn (stacks with base Spade generation)."},
        ]
    },
    'QS': {
        'name': "Hummingbird Courier",
        'suit': 'Spades', 'rank': 'Queen', 'type': 'Unit',
        'cost': 4, 'hp': 4, 'attack': 1, 'defense': 9, 'movement': 5, 'range': 1,
        'abilities': [
            {'name': "Swift Delivery", 'cost': '1 AP', 'range': 3, 'description': "Target friendly unit may immediately move 1 square."},
            {'name': "Evasive", 'cost': 'Passive', 'description': "Gains +1 Defense against ranged attacks."},
            {'name': "Generates Food", 'cost': 'Passive', 'description': "Generates +1 Food at the start of your turn."},
        ]
    },
    'JS': {
        'name': "Quail Forager",
        'suit': 'Spades', 'rank': 'Jack', 'type': 'Unit',
        'cost': 2, 'hp': 4, 'attack': 1, 'defense': 8, 'movement': 3, 'range': 1,
        'abilities': [
            {'name': "Generates Food", 'cost': 'Passive', 'description': "Generates +1 Food at the start of your turn."},
            {'name': "Sacrifice Fodder", 'cost': 'Passive', 'description': "When sacrificed for Food, yields +1 Food."},
        ]
    },

    # --- Numbered Cards (5-10) ---
    # These don't have stats in the same way. Their primary function is defined
    # by SUIT_RESOURCE_VALUE. We don't need individual entries unless they
    # gain unique secondary effects later. For now, the game logic will just
    # check the suit and rank (5-10) when played as a resource.

} # End of CARD_DATA

# --- Helper function (optional, but can be useful) ---
def get_card_data(card_code):
    """Retrieves data for a specific card code."""
    return CARD_DATA.get(card_code, None)

# Example Usage (if run directly)
if __name__ == "__main__":
    print(f"--- Game Constants ---")
    print(f"Grid Size: {GRID_SIZE}")
    print(f"Max Rounds: {MAX_ROUNDS}")
    print(f"Max Hand Size: {MAX_HAND_SIZE}")
    print(f"Base Food Income: {BASE_FOOD_INCOME}")
    print(f"Suit Resource Value: {SUIT_RESOURCE_VALUE}")

    print("\n--- Terrain Examples ---")
    print(f"Low Cover (2): {TERRAIN_EFFECTS['2']}")
    print(f"Heavy Cover (3): {TERRAIN_EFFECTS['3']}")
    print(f"Food Cache (4): {RESOURCE_EFFECTS['4']}")

    print("\n--- Unit Card Examples ---")
    ace_clubs = get_card_data('AC')
    if ace_clubs:
        print(f"\nAce of Clubs ({ace_clubs['name']}):")
        for key, value in ace_clubs.items():
            print(f"  {key}: {value}")

    king_hearts = get_card_data('KH')
    if king_hearts:
        print(f"\nKing of Hearts ({king_hearts['name']}):")
        for key, value in king_hearts.items():
            print(f"  {key}: {value}")

    jack_spades = get_card_data('JS')
    if jack_spades:
        print(f"\nJack of Spades ({jack_spades['name']}):")
        for key, value in jack_spades.items():
            print(f"  {key}: {value}")

    # Test getting non-existent card
    # print("\nTesting non-existent card:")
    # print(get_card_data('XX')) # Should print None
"""

Constants: Defines core game parameters like grid size, round limit, hand size, starting resources, etc.

Terrain/Resource Effects: Dictionaries defining the impact of the 2s, 3s, and 4s when placed on the board.

CARD_DATA Dictionary: This is the main data structure.

Keys: Uses a simple code (Rank + Suit Initial, e.g., 'AC', 'KH', 'QD', 'JS') for easy lookup.

Values: Each value is another dictionary containing all the relevant stats and info for that specific card:

name: Flavorful name.

suit, rank, type: Basic card identifiers.

cost: Food cost to play (0 for starting Champions).

hp, attack, defense, movement, range: Core combat and movement stats.

abilities: A list of dictionaries, where each dictionary describes an ability. This allows for multiple abilities per card and includes details like cost (Passive, 1 AP, 2 AP, etc.), range (if applicable), and a description.

Card Design Choices (Examples):

Costs: Generally increase from Jack -> Queen -> King. Champions have 0 cost as they start in play. Specialist Kings (like Necromancer) might cost more.

Stats: Tried to align stats with the faction roles (Clubs = high Atk/HP, Hearts = high Def/HP, Diamonds = Range/moderate stats, Spades = high Mov/low stats). Champion stats are significantly higher.

Abilities: Implemented core concepts from the rules (Healing, Food Gen, Ranged Attacks, Cover interaction, Necromancy, Buffs, Movement tricks). Passive abilities are noted. Action Point costs are specified for activated abilities.

Numbered Cards (5-10): Explicitly noted that these don't need individual entries yet. Their function is primarily handled by the SUIT_RESOURCE_VALUE constant.

"""
