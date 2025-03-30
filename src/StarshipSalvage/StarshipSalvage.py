from typing import Optional
from game_logger import GameLogger
from ai_agent import AIAgent
from common.card import Card
from src.common.player import Player
from game_state import GameState

# Global discard pile for cards discarded during tech search from the Derelict Cache.
cache_discard = []


def create_standard_deck():
    suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
    ranks = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]
    deck = [Card(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck


def create_starter_deck():
    # Starter deck: 7 Engineers (2♣) and 3 Marines (2♠)
    starter = [Card("Clubs", "2") for _ in range(7)] + [Card("Spades", "2") for _ in range(3)]
    random.shuffle(starter)
    return starter


def draw_from_cache(cache):
    if cache:
        return cache.pop(0)
    else:
        global cache_discard
        if cache_discard:
            print("Recycling tech search discards back into the Derelict Cache.")
            random.shuffle(cache_discard)
            cache.extend(cache_discard)
            cache_discard.clear()
            if cache:
                return cache.pop(0)
        return None


def player_turn(player: Player, opponent: Player, game_state: GameState, logger: GameLogger, 
                turn_number: int, phase: str, ai_agent: Optional[AIAgent] = None) -> None:
    print("\n" + "=" * 40)
    print(f"{player.name}'s turn | Hull: {player.hull} | Shield: {player.shield}")
    
    # Log state at start of turn
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name=opponent.name,
        player1_hull=player.hull,
        player2_hull=opponent.hull,
        player1_shield=player.shield,
        player2_shield=opponent.shield,
        player1_hand_size=player.get_hand_size(),
        player2_hand_size=opponent.get_hand_size(),
        player1_deck_size=player.get_deck_size(),
        player2_deck_size=opponent.get_deck_size(),
        player1_discard_size=player.get_discard_size(),
        player2_discard_size=opponent.get_discard_size(),
        tech_bay_size=game_state.get_tech_bay_size(),
        derelict_cache_size=game_state.get_derelict_cache_size(),
        phase=phase
    )

    # At start of turn, shield resets
    player.shield = 0

    # Draw Phase
    player.draw_cards(5)
    print(f"{player.name} draws 5 cards.")
    
    # Log state after draw
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name=opponent.name,
        player1_hull=player.hull,
        player2_hull=opponent.hull,
        player1_shield=player.shield,
        player2_shield=opponent.shield,
        player1_hand_size=player.get_hand_size(),
        player2_hand_size=opponent.get_hand_size(),
        player1_deck_size=player.get_deck_size(),
        player2_deck_size=opponent.get_deck_size(),
        player1_discard_size=player.get_discard_size(),
        player2_discard_size=opponent.get_discard_size(),
        tech_bay_size=game_state.get_tech_bay_size(),
        derelict_cache_size=game_state.get_derelict_cache_size(),
        phase='action'
    )

    salvage_points = 0
    spades_count = 0   # for Marine maneuvers (attack)
    hearts_count = 0   # for Medic maneuvers (repair)

    # Action Phase
    while True:
        if not player.hand:
            print("No cards left in hand.")
            break
            
        if ai_agent and player.name == "AI":
            # Get AI's decision
            action = ai_agent.decide_action(logger.states[-1], player.hand)
            if action.card_index is None:
                print("AI ends action phase.")
                break
                
            try:
                card = player.hand.pop(action.card_index)
                if action.action_type == 'resource':
                    val = card.face_value()
                    salvage_points += val
                    print(f"AI used {card} for resources (+{val} salvage).")
                elif action.action_type == 'maneuver':
                    if card.suit == "Clubs":
                        print("AI Engineer maneuver: Drawing 1 card.")
                        player.draw_cards(1)
                    elif card.suit == "Diamonds":
                        print("AI Scientist maneuver: Looking at top 3 cards of the Derelict Cache.")
                        search_cards = []
                        for _ in range(3):
                            c = game_state.draw_from_cache()
                            if c:
                                search_cards.append(c)
                        if search_cards:
                            # AI chooses first card as fallback
                            chosen = search_cards.pop(0)
                            player.hand.append(chosen)
                            print(f"AI added {chosen} to hand.")
                            if search_cards:
                                game_state.add_to_cache_discard(search_cards)
                    elif card.suit == "Hearts":
                        hearts_count += 1
                        print("AI Medic maneuver: Scheduled hull repair.")
                    elif card.suit == "Spades":
                        spades_count += 1
                        print("AI Marine maneuver: Scheduled attack.")
            except Exception as e:
                print(f"Error executing AI action: {e}")
                break
        else:
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
            mode = input(f"Play {card} as (R)esource or (M)aneuver? ").strip().lower()
            if mode.startswith("r"):
                val = card.face_value()
                salvage_points += val
                print(f"Used {card} for resources (+{val} salvage).")
            elif mode.startswith("m"):
                if card.suit == "Clubs":
                    print("Engineer maneuver: Drawing 1 card.")
                    player.draw_cards(1)
                elif card.suit == "Diamonds":
                    print("Scientist maneuver: Looking at top 3 cards of the Derelict Cache.")
                    search_cards = []
                    for _ in range(3):
                        c = game_state.draw_from_cache()
                        if c:
                            search_cards.append(c)
                    if not search_cards:
                        print("No cards available in the Derelict Cache for tech search.")
                    else:
                        print("Choose one card to add to your hand:")
                        for i, c in enumerate(search_cards):
                            print(f"  [{i}] {c}")
                        while True:
                            sel = input("Enter the index of the card to add: ").strip()
                            try:
                                sel_idx = int(sel)
                                if sel_idx < 0 or sel_idx >= len(search_cards):
                                    print("Invalid index.")
                                    continue
                                chosen = search_cards.pop(sel_idx)
                                player.hand.append(chosen)
                                print(f"Added {chosen} to your hand.")
                                break
                            except ValueError:
                                print("Invalid input.")
                        if search_cards:
                            print("Discarding the remaining cards from tech search.")
                            game_state.add_to_cache_discard(search_cards)
                elif card.suit == "Hearts":
                    hearts_count += 1
                    print("Medic maneuver: Scheduled hull repair.")
                elif card.suit == "Spades":
                    spades_count += 1
                    print("Marine maneuver: Scheduled attack.")
                else:
                    print("Unknown card suit!")
            else:
                print("Invalid mode; returning card to hand.")
                player.hand.insert(idx, card)

    print(f"\nAction phase complete. Salvage Points: {salvage_points}")

    # Purchase Phase
    print("\n--- Tech Bay ---")
    for idx, tech in enumerate(game_state.tech_bay):
        if tech:
            cost = tech.face_value()
            print(f"  [{idx}] {tech} (Cost: {cost})")
        else:
            print(f"  [{idx}] Empty")
            
    if ai_agent and player.name == "AI":
        # Get AI's purchase decision
        action = ai_agent.decide_purchase(logger.states[-1], game_state.tech_bay, salvage_points)
        if action.purchase and action.tech_bay_index is not None:
            try:
                tech_card = game_state.tech_bay[action.tech_bay_index]
                cost = tech_card.face_value()
                if salvage_points >= cost:
                    salvage_points -= cost
                    player.add_to_discard(tech_card)
                    print(f"AI purchased {tech_card} for {cost} salvage points.")
                    game_state.refill_tech_bay_slot(action.tech_bay_index)
            except Exception as e:
                print(f"Error executing AI purchase: {e}")
        else:
            print("AI chose not to purchase.")
    else:
        purchase_choice = input("Enter the index of a Tech Bay card to purchase (or 'none' to skip): ").strip().lower()
        if purchase_choice != "none":
            try:
                t_idx = int(purchase_choice)
                if t_idx < 0 or t_idx >= len(game_state.tech_bay) or game_state.tech_bay[t_idx] is None:
                    print("Invalid selection; skipping purchase.")
                else:
                    tech_card = game_state.tech_bay[t_idx]
                    cost = tech_card.face_value()
                    if salvage_points >= cost:
                        salvage_points -= cost
                        player.add_to_discard(tech_card)
                        print(f"Purchased {tech_card} for {cost} salvage points. It goes to your discard pile.")
                        game_state.refill_tech_bay_slot(t_idx)
                    else:
                        print("Not enough salvage points to purchase that card.")
            except ValueError:
                print("Invalid input; skipping purchase.")
        else:
            print("No purchase made.")

    # Convert remaining salvage points to shield
    if salvage_points > 0:
        player.shield += salvage_points
        print(f"{salvage_points} salvage points converted into shield for your next turn.")

    # Combat Phase
    attack_damage = game_state.calculate_attack_damage(spades_count)
    print(f"\n{player.name} launches an attack with combo damage = {attack_damage} (from {spades_count} Marine maneuver(s)).")
    if attack_damage > 0:
        game_state.apply_damage(player, opponent, attack_damage)

    # Repair Phase
    if hearts_count > 0:
        repair = game_state.calculate_repair_amount(hearts_count)
        player.hull += repair
        print(f"{player.name} repairs {repair} hull. New hull: {player.hull}")

    # End Phase
    player.discard_hand()
    print(f"{player.name} discards any remaining cards. End of turn.\n")

    # Log final state
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name=opponent.name,
        player1_hull=player.hull,
        player2_hull=opponent.hull,
        player1_shield=player.shield,
        player2_shield=opponent.shield,
        player1_hand_size=player.get_hand_size(),
        player2_hand_size=opponent.get_hand_size(),
        player1_deck_size=player.get_deck_size(),
        player2_deck_size=opponent.get_deck_size(),
        player1_discard_size=player.get_discard_size(),
        player2_discard_size=opponent.get_discard_size(),
        tech_bay_size=game_state.get_tech_bay_size(),
        derelict_cache_size=game_state.get_derelict_cache_size(),
        phase='end'
    )


def main():
    print("Welcome to Starship Salvage: Cosmic Run!")
    
    # Get player names
    p1_name = input("Player 1, enter your name: ").strip() or "Player 1"
    p2_name = input("Player 2, enter your name: ").strip() or "Player 2"
    player1 = Player(p1_name)
    player2 = Player(p2_name)

    # Initialize game components
    logger = GameLogger()
    game_state = GameState()
    
    # Initialize AI agent if Player 2 is AI
    ai_agent = None
    if p2_name == "AI":
        try:
            ai_agent = AIAgent()
            print("AI agent initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize AI agent: {e}")
            print("Player 1 will play for both players.")
            return

    # Main game loop
    turn_counter = 1
    while player1.hull > 0 and player2.hull > 0:
        print("\n" + "#" * 40)
        print(f"Turn {turn_counter}")
        
        # Player 1's turn
        player_turn(player1, player2, game_state, logger, turn_counter, 'start', ai_agent)
        if player2.hull <= 0:
            break
            
        # Player 2's turn
        player_turn(player2, player1, game_state, logger, turn_counter, 'start', ai_agent)
        if player1.hull <= 0:
            break
            
        turn_counter += 1

    # Determine winner and log outcome
    if player1.hull <= 0 and player2.hull <= 0:
        print("It's a draw!")
        logger.log_outcome(None, True)
    elif player1.hull <= 0:
        print(f"{player2.name} wins!")
        logger.log_outcome(player2.name, False)
    else:
        print(f"{player1.name} wins!")
        logger.log_outcome(player1.name, False)


if __name__ == "__main__":
    main()
