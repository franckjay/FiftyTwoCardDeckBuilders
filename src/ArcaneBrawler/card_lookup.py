from typing import Dict, List
from player import Archetype
from card import Card, Suit

def get_card_effect_description(card: Card, archetype: Archetype) -> str:
    """Get a description of what a card does for a specific archetype."""
    base_value = card.face_value()
    
    effects = {
        Archetype.CULTIVATOR: {
            Suit.HEARTS: f"Heal for {base_value}",
            Suit.DIAMONDS: "Draw 2 cards",
            Suit.CLUBS: "Gain 1 Growth Token (+1 mana next turn)",
            Suit.SPADES: "Increase max mana by 1"
        },
        Archetype.BERSERKER: {
            Suit.HEARTS: f"Deal {base_value} × (1 + rage) damage",
            Suit.DIAMONDS: "Gain 1 Rage counter",
            Suit.CLUBS: f"Take {base_value//2} damage, gain 2 Rage counters",
            Suit.SPADES: "Tap target creature"
        },
        Archetype.MYSTIC: {
            Suit.HEARTS: "Counter and tap target creature",
            Suit.DIAMONDS: "Gain 1 Spell counter, tap target",
            Suit.CLUBS: "Force opponent to discard a card",
            Suit.SPADES: "Draw 2 cards (discard excess)"
        },
        Archetype.TRICKSTER: {
            Suit.HEARTS: "Swap life totals (up to 5 difference)",
            Suit.DIAMONDS: "Steal up to 2 mana from opponent",
            Suit.CLUBS: "Force opponent to discard a card",
            Suit.SPADES: "Steal a random card from opponent"
        },
        Archetype.COMMANDER: {
            Suit.HEARTS: "Create a Squire token (2/2)",
            Suit.DIAMONDS: "Draw cards equal to number of tokens",
            Suit.CLUBS: "Protect all tokens from effects",
            Suit.SPADES: f"Buff all tokens by {base_value//2}"
        }
    }
    
    effect = effects[archetype][card.suit]
    if card.is_creature:
        effect += f" | Creature ({base_value}/{base_value})"
    return effect

def format_card_display(card: Card, archetype: Archetype) -> str:
    """Format a card for display with its effect."""
    effect = get_card_effect_description(card, archetype)
    return f"{card} - {effect}"

def format_hand_display(cards: List[Card], archetype: Archetype) -> List[str]:
    """Format a list of cards for hand display."""
    return [f"[{idx}] {format_card_display(card, archetype)}" 
            for idx, card in enumerate(cards)]

def format_field_display(cards: List[Card], archetype: Archetype) -> List[str]:
    """Format a list of cards for field display."""
    return [f"{format_card_display(card, archetype)} (Tapped: {card.tapped})" 
            for card in cards] 