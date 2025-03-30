from typing import List, Optional
from player import Player, Archetype
from game_state import GameState, Phase
from card import Card, Suit
from card_lookup import format_hand_display, format_field_display

def display_game_state(game_state: GameState) -> None:
    """Display the current game state."""
    current_player = game_state.get_current_player()
    opponent = game_state.get_opponent()
    
    print("\n" + "=" * 50)
    print(f"Turn {game_state.turn_number} - Phase: {game_state.phase.value}")
    print(f"Current Player: {current_player.name} ({current_player.archetype.value})")
    print(f"Health: {current_player.health}/{current_player.max_health}")
    print(f"Mana: {current_player.mana}/{current_player.max_mana}")
    print("\nOpponent:")
    print(f"Name: {opponent.name} ({opponent.archetype.value})")
    print(f"Health: {opponent.health}/{opponent.max_health}")
    print(f"Field: {len(opponent.field)} cards")
    print("\nYour Field:")
    for card_display in format_field_display(current_player.field, current_player.archetype):
        print(f"  {card_display}")
    print("\nYour Hand:")
    for card_display in format_hand_display(current_player.hand, current_player.archetype):
        print(f"  {card_display}")
    print("=" * 50)

def get_player_input(prompt: str) -> str:
    """Get input from the player."""
    return input(prompt).strip().lower()

def handle_main_phase(game_state: GameState) -> None:
    """Handle the main phase actions."""
    current_player = game_state.get_current_player()
    
    while True:
        action = get_player_input("\nActions:\n1. Play card\n2. End phase\nChoice: ")
        
        if action == "2":
            break
        elif action == "1":
            if not current_player.hand:
                print("No cards in hand!")
                break
                
            try:
                card_idx = int(get_player_input("Enter card index: "))
                if 0 <= card_idx < len(current_player.hand):
                    card = current_player.hand[card_idx]
                    if current_player.can_play_card(card):
                        if current_player.play_card(card):
                            print(f"Played {card}")
                            # Handle card effects based on archetype
                            game_state.resolve_spell(current_player, card)
                        else:
                            print("Not enough mana!")
                    else:
                        print("Cannot play this card!")
                else:
                    print("Invalid card index!")
            except ValueError:
                print("Invalid input!")

def handle_combat_phase(game_state: GameState) -> None:
    """Handle the combat phase."""
    current_player = game_state.get_current_player()
    opponent = game_state.get_opponent()
    
    while True:
        action = get_player_input("\nCombat Actions:\n1. Attack\n2. End combat\nChoice: ")
        
        if action == "2":
            break
        elif action == "1":
            # Only show creatures that can attack
            attacking_creatures = [card for card in current_player.field if not card.tapped and card.is_creature]
            if not attacking_creatures:
                print("No creatures to attack with!")
                break
                
            print("\nYour attacking creatures:")
            for idx, card in enumerate(attacking_creatures):
                print(f"  [{idx}] {format_card_display(card, current_player.archetype)}")
                    
            try:
                attacker_idx = int(get_player_input("Enter attacker index (or -1 to cancel): "))
                if attacker_idx == -1:
                    break
                    
                if 0 <= attacker_idx < len(attacking_creatures):
                    attacker = attacking_creatures[attacker_idx]
                    if attacker.tapped:
                        print("Card is tapped!")
                        continue
                        
                    # Only show creatures that can block
                    blocking_creatures = [card for card in opponent.field if card.is_creature]
                    print("\nOpponent's creatures:")
                    for idx, card in enumerate(blocking_creatures):
                        print(f"  [{idx}] {format_card_display(card, opponent.archetype)}")
                        
                    blocker_idx = get_player_input("Enter blocker index (or press Enter for direct attack): ")
                    if blocker_idx:
                        try:
                            blocker_idx = int(blocker_idx)
                            if 0 <= blocker_idx < len(blocking_creatures):
                                blocker = blocking_creatures[blocker_idx]
                                game_state.resolve_combat(attacker, blocker)
                                attacker.tapped = True
                        except ValueError:
                            print("Invalid blocker index!")
                    else:
                        game_state.resolve_combat(attacker)
                        attacker.tapped = True
                else:
                    print("Invalid attacker index!")
            except ValueError:
                print("Invalid input!")

def main():
    print("Welcome to Arcane Shuffle!")
    
    # Get player names and archetypes
    p1_name = input("Player 1, enter your name: ").strip() or "Player 1"
    p2_name = input("Player 2, enter your name: ").strip() or "Player 2"
    
    print("\nChoose your archetype:")
    for idx, archetype in enumerate(Archetype):
        print(f"{idx + 1}. {archetype.value}")
    
    p1_archetype_idx = int(input(f"{p1_name}, choose your archetype (1-5): ").strip()) - 1
    p2_archetype_idx = int(input(f"{p2_name}, choose your archetype (1-5): ").strip()) - 1
    
    player1 = Player(p1_name, list(Archetype)[p1_archetype_idx])
    player2 = Player(p2_name, list(Archetype)[p2_archetype_idx])
    
    # Initialize game
    game_state = GameState()
    game_state.add_player(player1)
    game_state.add_player(player2)
    game_state.start_game()
    
    # Main game loop
    while not game_state.game_over:
        display_game_state(game_state)
        
        if game_state.phase == Phase.MAIN1:
            handle_main_phase(game_state)
        elif game_state.phase == Phase.COMBAT:
            handle_combat_phase(game_state)
        elif game_state.phase == Phase.MAIN2:
            handle_main_phase(game_state)
            
        game_state.advance_phase()
        game_state.check_game_over()
    
    # Game over
    print("\nGame Over!")
    if game_state.winner:
        print(f"{game_state.winner.name} wins!")
    else:
        print("It's a draw!")

if __name__ == "__main__":
    main() 