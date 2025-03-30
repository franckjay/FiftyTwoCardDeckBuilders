from typing import Optional
from game_logger import GameLogger
from game_state import GameState
from player import Player

def player_turn(player: Player, game_state: GameState, logger: GameLogger, 
                turn_number: int, phase: str) -> None:
    print("\n" + "=" * 40)
    print(f"{player.name}'s turn | Health: {player.health} | Temp Health: {player.temp_health}")
    print(f"Current Monster: {game_state.current_monster}")
    
    # Log state at start of turn
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name="Monster",
        player1_health=player.health,
        player2_health=game_state.current_monster.face_value() if game_state.current_monster else 0,
        player1_temp_health=player.temp_health,
        player2_temp_health=0,
        player1_hand_size=player.get_hand_size(),
        player2_hand_size=0,
        player1_deck_size=player.get_deck_size(),
        player2_deck_size=game_state.get_monster_deck_size(),
        player1_discard_size=player.get_discard_size(),
        player2_discard_size=len(game_state.monster_discard),
        treasure_room_size=game_state.get_treasure_room_size(),
        phase=phase
    )

    # Draw Phase
    player.draw_cards(5)
    print(f"{player.name} draws 5 cards.")
    
    # Log state after draw
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name="Monster",
        player1_health=player.health,
        player2_health=game_state.current_monster.face_value() if game_state.current_monster else 0,
        player1_temp_health=player.temp_health,
        player2_temp_health=0,
        player1_hand_size=player.get_hand_size(),
        player2_hand_size=0,
        player1_deck_size=player.get_deck_size(),
        player2_deck_size=game_state.get_monster_deck_size(),
        player1_discard_size=player.get_discard_size(),
        player2_discard_size=len(game_state.monster_discard),
        treasure_room_size=game_state.get_treasure_room_size(),
        phase='action'
    )

    # Action Phase
    while True:
        if not player.hand:
            print("No cards left in hand.")
            break
            
        print("\nYour hand:")
        for idx, card in enumerate(player.hand):
            print(f"  [{idx}] {card}")
        choice = input("Enter the index of a card to play (or type 'done' to finish actions): ").strip()
        if choice.lower() == "done":
            break
        try:
            idx = int(choice)
            if idx < 0 or idx >= len(player.hand):
                print("Invalid index.")
                continue
        except ValueError:
            print("Invalid input.")
            continue

        card = player.hand.pop(idx)
        mode = input(f"Play {card} as (R)esource or (A)ction? ").strip().lower()
        if mode.startswith("r"):
            val = card.face_value()
            player.gold += val
            print(f"Used {card} for resources (+{val} gold).")
        elif mode.startswith("a"):
            if card.suit == "Spades":  # Weapon
                if game_state.current_monster:
                    damage = card.face_value()
                    game_state.current_monster.health -= damage
                    print(f"Dealt {damage} damage to the monster!")
                    if player.use_special_ability(card):
                        print("Special Ability: Discarding Weapon to draw 2 cards!")
                        player.draw_cards(2)
            elif card.suit == "Hearts":  # Shield
                if game_state.current_monster:
                    block = card.face_value()
                    game_state.current_monster.health -= block // 2
                    print(f"Blocked {block} damage and dealt {block // 2} to the monster!")
            elif card.suit == "Clubs":  # Dagger
                if game_state.current_monster:
                    damage = card.face_value() // 2
                    game_state.current_monster.health -= damage
                    print(f"Quick strike! Dealt {damage} damage to the monster!")
            elif card.suit == "Diamonds":  # Potion
                heal_amount = card.face_value()
                target = input("Heal (S)elf or (A)lly? ").strip().lower()
                if target.startswith("s"):
                    player.heal(heal_amount)
                elif target.startswith("a"):
                    # In a real game, you'd select which ally to heal
                    # For now, we'll just heal self
                    player.heal(heal_amount)
                if player.use_special_ability(card):
                    print("Special Ability: Looking at top 3 cards of Monster Deck!")
                    # In a real game, you'd show the top 3 cards
                    # For now, we'll just acknowledge it
            else:
                print("Unknown card suit!")
        else:
            print("Invalid mode; returning card to hand.")
            player.hand.insert(idx, card)

    print(f"\nAction phase complete. Gold: {player.gold}")

    # Treasure Phase
    print("\n--- Treasure Room ---")
    for idx, treasure in enumerate(game_state.treasure_room):
        if treasure:
            cost = treasure.face_value()
            print(f"  [{idx}] {treasure} (Cost: {cost})")
        else:
            print(f"  [{idx}] Empty")
            
    purchase_choice = input("Enter the index of a Treasure Room card to purchase (or 'none' to skip): ").strip().lower()
    if purchase_choice != "none":
        try:
            t_idx = int(purchase_choice)
            if t_idx < 0 or t_idx >= len(game_state.treasure_room) or game_state.treasure_room[t_idx] is None:
                print("Invalid selection; skipping purchase.")
            else:
                treasure = game_state.treasure_room[t_idx]
                cost = treasure.face_value()
                if player.gold >= cost:
                    player.gold -= cost
                    player.add_to_discard(treasure)
                    print(f"Purchased {treasure} for {cost} gold. It goes to your discard pile.")
                    game_state.refill_treasure_slot(t_idx)
                else:
                    print("Not enough gold to purchase that card.")
        except ValueError:
            print("Invalid input; skipping purchase.")
    else:
        print("No purchase made.")

    # Convert remaining gold to temporary health
    if player.gold > 0:
        player.add_temp_health(min(player.gold, 5))
        print(f"Remaining gold converted to temporary health.")

    # End Phase
    player.discard_hand()
    print(f"{player.name} discards any remaining cards. End of turn.\n")

    # Log final state
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name="Monster",
        player1_health=player.health,
        player2_health=game_state.current_monster.face_value() if game_state.current_monster else 0,
        player1_temp_health=player.temp_health,
        player2_temp_health=0,
        player1_hand_size=player.get_hand_size(),
        player2_hand_size=0,
        player1_deck_size=player.get_deck_size(),
        player2_deck_size=game_state.get_monster_deck_size(),
        player1_discard_size=player.get_discard_size(),
        player2_discard_size=len(game_state.monster_discard),
        treasure_room_size=game_state.get_treasure_room_size(),
        phase='end'
    )

def main():
    print("Welcome to Dungeon Crawler: Card Quest!")
    
    # Get player names and classes
    p1_name = input("Player 1, enter your name: ").strip() or "Player 1"
    p2_name = input("Player 2, enter your name: ").strip() or "Player 2"
    
    print("\nChoose your character class:")
    print("1. Warrior - Specializes in direct combat and defense")
    print("2. Rogue - Specializes in quick strikes and utility")
    
    p1_class = input(f"{p1_name}, choose your class (1/2): ").strip()
    p2_class = input(f"{p2_name}, choose your class (1/2): ").strip()
    
    p1_class = "Warrior" if p1_class == "1" else "Rogue"
    p2_class = "Warrior" if p2_class == "1" else "Rogue"
    
    player1 = Player(p1_name, p1_class)
    player2 = Player(p2_name, p2_class)

    # Get difficulty level
    print("\nChoose difficulty level:")
    print("1. Easy (25 Health)")
    print("2. Normal (20 Health)")
    print("3. Hard (15 Health)")
    difficulty = input("Enter your choice (1/2/3): ").strip()
    difficulty_map = {"1": "easy", "2": "normal", "3": "hard"}
    difficulty = difficulty_map.get(difficulty, "normal")

    # Initialize game components
    logger = GameLogger()
    game_state = GameState(difficulty)
    
    # Set starting health based on difficulty
    starting_health = game_state.get_starting_health()
    player1.health = starting_health
    player2.health = starting_health

    # Main game loop
    turn_counter = 1
    while player1.health > 0 and player2.health > 0:
        print("\n" + "#" * 40)
        print(f"Turn {turn_counter}")
        
        # Player 1's turn
        player_turn(player1, game_state, logger, turn_counter, 'start')
        if player1.health <= 0 or player2.health <= 0:
            break
            
        # Monster deals damage
        game_state.deal_monster_damage(player1, player2)
        if player1.health <= 0 or player2.health <= 0:
            break
            
        # Player 2's turn
        player_turn(player2, game_state, logger, turn_counter, 'start')
        if player1.health <= 0 or player2.health <= 0:
            break
            
        # Monster deals damage
        game_state.deal_monster_damage(player1, player2)
        if player1.health <= 0 or player2.health <= 0:
            break
            
        turn_counter += 1

    # Determine outcome
    if player1.health <= 0 and player2.health <= 0:
        print("\nGame Over! Both players have fallen!")
        logger.log_outcome(None, True)
    elif player1.health <= 0 or player2.health <= 0:
        print("\nGame Over! One player has fallen!")
        logger.log_outcome(None, True)
    elif game_state.current_monster and game_state.current_monster.rank == "A" and game_state.current_monster.suit == "Spades":
        print("\nVictory! You have defeated the Boss!")
        logger.log_outcome("Players", False)
    else:
        print("\nGame Over! The dungeon proved too challenging!")
        logger.log_outcome(None, True)

if __name__ == "__main__":
    main() 