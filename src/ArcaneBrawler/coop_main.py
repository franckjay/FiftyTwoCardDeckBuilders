import random
from typing import List, Optional
from player import Player, Archetype
from game_state import GameState, Phase
from card import Card, Suit
from card_lookup import format_hand_display, format_field_display
from ai_agent import AIAgent

def display_game_state(game_state: GameState, ai_agent: AIAgent) -> None:
    """Display the current game state."""
    current_player = game_state.get_current_player()
    ai_player = ai_agent.ai_player
    
    print("\n" + "=" * 50)
    print(f"Turn {game_state.turn_number} - Phase: {game_state.phase.value}")
    
    if current_player == ai_player:
        print(f"Current Player: {ai_player.name} ({ai_player.archetype.value})")
    else:
        print(f"Current Player: {current_player.name} ({current_player.archetype.value})")
    
    print("\nAI Opponent:")
    print(f"Name: {ai_player.name} ({ai_player.archetype.value})")
    print(f"Health: {ai_player.health}/{ai_player.max_health}")
    print(f"Field: {len(ai_player.field)} cards")
    
    print("\nPlayers:")
    for player in game_state.players:
        print(f"\n{player.name} ({player.archetype.value}):")
        print(f"Health: {player.health}/{player.max_health}")
        print(f"Mana: {player.mana}/{player.max_mana}")
        print("Field:")
        for card_display in format_field_display(player.field, player.archetype):
            print(f"  {card_display}")
        print("Hand:")
        for card_display in format_hand_display(player.hand, player.archetype):
            print(f"  {card_display}")
    
    print("=" * 50)

def handle_ai_turn(game_state: GameState, ai_agent: AIAgent) -> None:
    """Handle the AI's turn."""
    while True:
        if game_state.phase == Phase.END:
            break
            
        prompt = ai_agent.get_ai_prompt()
        # Here you would send the prompt to your LLM and get a response
        # For now, we'll use a placeholder response
        response = "end"  # Replace with actual LLM response
        
        action, params = ai_agent.get_ai_action(response)
        
        if action == "play" and game_state.phase in [Phase.MAIN1, Phase.MAIN2]:
            card_idx = params[0]
            if 0 <= card_idx < len(ai_agent.ai_player.hand):
                card = ai_agent.ai_player.hand[card_idx]
                if ai_agent.ai_player.can_play_card(card):
                    ai_agent.ai_player.play_card(card)
                    game_state.resolve_spell(ai_agent.ai_player, card)
        elif action == "attack" and game_state.phase == Phase.COMBAT:
            attacker_idx, target_idx, blocker_idx = params
            if (0 <= attacker_idx < len(ai_agent.ai_player.field) and
                1 <= target_idx <= len(game_state.players)):
                attacker = ai_agent.ai_player.field[attacker_idx]
                target = game_state.players[target_idx - 1]
                
                if blocker_idx == -1:
                    game_state.resolve_combat(attacker)
                else:
                    if 0 <= blocker_idx < len(target.field):
                        blocker = target.field[blocker_idx]
                        game_state.resolve_combat(attacker, blocker)
                
                attacker.tapped = True
        elif action == "end":
            game_state.advance_phase()
            break

def handle_player_turn(game_state: GameState, player: Player) -> None:
    """Handle a player's turn."""
    while True:
        if game_state.phase == Phase.END:
            break
            
        display_game_state(game_state, None)  # Pass None for ai_agent since it's player's turn
        
        if game_state.phase in [Phase.MAIN1, Phase.MAIN2]:
            action = input("\nActions:\n1. Play card\n2. End phase\nChoice: ")
            if action == "2":
                game_state.advance_phase()
                break
            elif action == "1":
                if not player.hand:
                    print("No cards in hand!")
                    continue
                    
                try:
                    card_idx = int(input("Enter card index: "))
                    if 0 <= card_idx < len(player.hand):
                        card = player.hand[card_idx]
                        if player.can_play_card(card):
                            player.play_card(card)
                            game_state.resolve_spell(player, card)
                        else:
                            print("Not enough mana!")
                    else:
                        print("Invalid card index!")
                except ValueError:
                    print("Invalid input!")
                    
        elif game_state.phase == Phase.COMBAT:
            action = input("\nCombat Actions:\n1. Attack\n2. End combat\nChoice: ")
            if action == "2":
                game_state.advance_phase()
                break
            elif action == "1":
                attacking_creatures = [card for card in player.field if not card.tapped and card.is_creature]
                if not attacking_creatures:
                    print("No creatures to attack with!")
                    continue
                    
                print("\nYour attacking creatures:")
                for idx, card in enumerate(attacking_creatures):
                    print(f"  [{idx}] {format_card_display(card, player.archetype)}")
                    
                try:
                    attacker_idx = int(input("Enter attacker index (or -1 to cancel): "))
                    if attacker_idx == -1:
                        continue
                        
                    if 0 <= attacker_idx < len(attacking_creatures):
                        attacker = attacking_creatures[attacker_idx]
                        target_idx = int(input("Enter target (1 for AI, 2 for other player): "))
                        if 1 <= target_idx <= 2:
                            target = game_state.players[target_idx - 1] if target_idx == 2 else None
                            
                            if target:
                                blocking_creatures = [card for card in target.field if card.is_creature]
                                print("\nTarget's creatures:")
                                for idx, card in enumerate(blocking_creatures):
                                    print(f"  [{idx}] {format_card_display(card, target.archetype)}")
                                    
                                blocker_idx = input("Enter blocker index (or press Enter for direct attack): ")
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
                                game_state.resolve_combat(attacker)
                                attacker.tapped = True
                except ValueError:
                    print("Invalid input!")

def main():
    print("Welcome to Arcane Shuffle Co-op!")
    
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
    
    # Initialize AI
    ai_agent = AIAgent(game_state)
    ai_archetype = random.choice(list(Archetype))
    ai_player = ai_agent.initialize_ai_player(ai_archetype)
    game_state.add_player(ai_player)
    
    game_state.start_game()
    
    # Main game loop
    while not game_state.game_over:
        current_player = game_state.get_current_player()
        
        if current_player == ai_player:
            handle_ai_turn(game_state, ai_agent)
        else:
            handle_player_turn(game_state, current_player)
            
        game_state.check_game_over()
    
    # Game over
    print("\nGame Over!")
    if game_state.winner:
        if game_state.winner == ai_player:
            print("The AI wins!")
        else:
            print(f"{game_state.winner.name} wins!")
    else:
        print("It's a draw!")

if __name__ == "__main__":
    main() 