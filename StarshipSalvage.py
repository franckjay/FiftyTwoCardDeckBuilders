import random
from game_logger import GameLogger
from ai_agent import AIAgent

# Global discard pile for cards discarded during tech search from the Derelict Cache.
cache_discard = []


class Card:
    def __init__(self, suit, rank):
        self.suit = suit  # "Clubs", "Diamonds", "Hearts", "Spades"
        self.rank = rank  # "2"-"10", "J", "Q", "K", "A"

    def face_value(self):
        if self.rank.isdigit():
            return int(self.rank)
        else:
            mapping = {"J": 5, "Q": 6, "K": 7, "A": 8}
            return mapping.get(self.rank, 0)

    def __str__(self):
        suit_symbols = {"Clubs": "♣", "Diamonds": "♦", "Hearts": "♥", "Spades": "♠"}
        return f"{self.rank}{suit_symbols.get(self.suit, self.suit)}"


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


class Player:
    def __init__(self, name):
        self.name = name
        self.deck = create_starter_deck()  # personal deck (starter deck)
        self.discard_pile = []
        self.hand = []
        self.hull = 15
        self.shield = 0  # shield points carried over from previous turn

    def draw_cards(self, num):
        for _ in range(num):
            if not self.deck:
                if self.discard_pile:
                    print(f"{self.name} is reshuffling the discard pile into the deck.")
                    self.deck = self.discard_pile
                    self.discard_pile = []
                    random.shuffle(self.deck)
                else:
                    print(f"{self.name} has no cards left to draw!")
                    return
            self.hand.append(self.deck.pop(0))


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


def player_turn(player, opponent, tech_bay, cache, logger, turn_number, phase, ai_agent=None):
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
        player1_hand_size=len(player.hand),
        player2_hand_size=len(opponent.hand),
        player1_deck_size=len(player.deck),
        player2_deck_size=len(opponent.deck),
        player1_discard_size=len(player.discard_pile),
        player2_discard_size=len(opponent.discard_pile),
        tech_bay_size=len([c for c in tech_bay if c is not None]),
        derelict_cache_size=len(cache),
        phase=phase
    )

    # At start of turn, shield resets (it only lasts until you face an opponent's attack)
    player.shield = 0

    # Draw Phase: draw 5 cards.
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
        player1_hand_size=len(player.hand),
        player2_hand_size=len(opponent.hand),
        player1_deck_size=len(player.deck),
        player2_deck_size=len(opponent.deck),
        player1_discard_size=len(player.discard_pile),
        player2_discard_size=len(opponent.discard_pile),
        tech_bay_size=len([c for c in tech_bay if c is not None]),
        derelict_cache_size=len(cache),
        phase='action'
    )

    salvage_points = 0
    spades_count = 0   # for Marine maneuvers (attack)
    hearts_count = 0   # for Medic maneuvers (repair)

    # Action Phase: let player play cards one at a time.
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
                            c = draw_from_cache(cache)
                            if c:
                                search_cards.append(c)
                        if search_cards:
                            # AI chooses first card as fallback
                            chosen = search_cards.pop(0)
                            player.hand.append(chosen)
                            print(f"AI added {chosen} to hand.")
                            if search_cards:
                                global cache_discard
                                cache_discard.extend(search_cards)
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
                # Resource Mode: add salvage points equal to card's face value.
                val = card.face_value()
                salvage_points += val
                print(f"Used {card} for resources (+{val} salvage).")
            elif mode.startswith("m"):
                # Maneuver Mode: perform suit-specific action.
                if card.suit == "Clubs":
                    # Engineer: draw 1 card immediately.
                    print("Engineer maneuver: Drawing 1 card.")
                    player.draw_cards(1)
                elif card.suit == "Diamonds":
                    # Scientist: tech search (look at top 3 cards of Derelict Cache)
                    print("Scientist maneuver: Looking at top 3 cards of the Derelict Cache.")
                    search_cards = []
                    for _ in range(3):
                        c = draw_from_cache(cache)
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
                        # Discard the rest.
                        if search_cards:
                            print("Discarding the remaining cards from tech search.")
                            global cache_discard
                            cache_discard.extend(search_cards)
                elif card.suit == "Hearts":
                    # Medic: schedule a hull repair.
                    hearts_count += 1
                    print("Medic maneuver: Scheduled hull repair.")
                elif card.suit == "Spades":
                    # Marine: schedule an attack.
                    spades_count += 1
                    print("Marine maneuver: Scheduled attack.")
                else:
                    print("Unknown card suit!")
            else:
                print("Invalid mode; returning card to hand.")
                player.hand.insert(idx, card)

    print(f"\nAction phase complete. Salvage Points: {salvage_points}")

    # Purchase Phase: use salvage points to buy one tech card from the Tech Bay.
    print("\n--- Tech Bay ---")
    for idx, tech in enumerate(tech_bay):
        if tech:
            cost = tech.face_value()
            print(f"  [{idx}] {tech} (Cost: {cost})")
        else:
            print(f"  [{idx}] Empty")
            
    if ai_agent and player.name == "AI":
        # Get AI's purchase decision
        action = ai_agent.decide_purchase(logger.states[-1], tech_bay, salvage_points)
        if action.purchase and action.tech_bay_index is not None:
            try:
                tech_card = tech_bay[action.tech_bay_index]
                cost = tech_card.face_value()
                if salvage_points >= cost:
                    salvage_points -= cost
                    player.discard_pile.append(tech_card)
                    print(f"AI purchased {tech_card} for {cost} salvage points.")
                    new_card = draw_from_cache(cache)
                    tech_bay[action.tech_bay_index] = new_card
            except Exception as e:
                print(f"Error executing AI purchase: {e}")
        else:
            print("AI chose not to purchase.")
    else:
        purchase_choice = input("Enter the index of a Tech Bay card to purchase (or 'none' to skip): ").strip().lower()
        if purchase_choice != "none":
            try:
                t_idx = int(purchase_choice)
                if t_idx < 0 or t_idx >= len(tech_bay) or tech_bay[t_idx] is None:
                    print("Invalid selection; skipping purchase.")
                else:
                    tech_card = tech_bay[t_idx]
                    cost = tech_card.face_value()
                    if salvage_points >= cost:
                        salvage_points -= cost
                        player.discard_pile.append(tech_card)
                        print(f"Purchased {tech_card} for {cost} salvage points. It goes to your discard pile.")
                        # Refill the Tech Bay slot.
                        new_card = draw_from_cache(cache)
                        tech_bay[t_idx] = new_card
                    else:
                        print("Not enough salvage points to purchase that card.")
            except ValueError:
                print("Invalid input; skipping purchase.")
        else:
            print("No purchase made.")

    # Any leftover salvage points are banked as a temporary shield (lasting until your next turn).
    if salvage_points > 0:
        player.shield += salvage_points
        print(f"{salvage_points} salvage points converted into shield for your next turn.")

    # Combat & End Phase:
    # First, resolve attack. (Combo: first spade =1 damage, second =2, etc.)
    attack_damage = (spades_count * (spades_count + 1)) // 2
    print(f"\n{player.name} launches an attack with combo damage = {attack_damage} (from {spades_count} Marine maneuver(s)).")
    if attack_damage > 0:
        # Opponent's shield absorbs damage first.
        if opponent.shield > 0:
            if opponent.shield >= attack_damage:
                opponent.shield -= attack_damage
                print(f"{opponent.name}'s shield absorbed all the damage. (Remaining shield: {opponent.shield})")
                attack_damage = 0
            else:
                print(f"{opponent.name}'s shield absorbed {opponent.shield} damage.")
                attack_damage -= opponent.shield
                opponent.shield = 0
        opponent.hull -= attack_damage
        print(f"{opponent.name}'s hull is now {opponent.hull}.")

    # Then, resolve repair from Medic maneuvers.
    if hearts_count > 0:
        # One heart repairs 1; each additional heart repairs +1 extra.
        if hearts_count == 1:
            repair = 1
        else:
            repair = 1 + (hearts_count - 1) * 2
        player.hull += repair
        print(f"{player.name} repairs {repair} hull. New hull: {player.hull}")

    # Finally, discard all remaining cards from hand.
    if player.hand:
        player.discard_pile.extend(player.hand)
        player.hand.clear()
    print(f"{player.name} discards any remaining cards. End of turn.\n")

    # Log state before combat
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name=opponent.name,
        player1_hull=player.hull,
        player2_hull=opponent.hull,
        player1_shield=player.shield,
        player2_shield=opponent.shield,
        player1_hand_size=len(player.hand),
        player2_hand_size=len(opponent.hand),
        player1_deck_size=len(player.deck),
        player2_deck_size=len(opponent.deck),
        player1_discard_size=len(player.discard_pile),
        player2_discard_size=len(opponent.discard_pile),
        tech_bay_size=len([c for c in tech_bay if c is not None]),
        derelict_cache_size=len(cache),
        phase='combat'
    )

    # Log state at end of turn
    logger.log_state(
        turn_number=turn_number,
        current_player=player.name,
        player1_name=player.name,
        player2_name=opponent.name,
        player1_hull=player.hull,
        player2_hull=opponent.hull,
        player1_shield=player.shield,
        player2_shield=opponent.shield,
        player1_hand_size=len(player.hand),
        player2_hand_size=len(opponent.hand),
        player1_deck_size=len(player.deck),
        player2_deck_size=len(opponent.deck),
        player1_discard_size=len(player.discard_pile),
        player2_discard_size=len(opponent.discard_pile),
        tech_bay_size=len([c for c in tech_bay if c is not None]),
        derelict_cache_size=len(cache),
        phase='end'
    )


def main():
    print("Welcome to Starship Salvage: Cosmic Run!")
    # Get player names.
    p1_name = input("Player 1, enter your name: ").strip() or "Player 1"
    p2_name = input("Player 2, enter your name: ").strip() or "Player 2"
    player1 = Player(p1_name)
    player2 = Player(p2_name)

    # Initialize game logger
    logger = GameLogger()

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

    # Set up the Derelict Cache (the common pool) and Tech Bay.
    cache = create_standard_deck()  # standard 52-card deck
    tech_bay = []
    for _ in range(5):
        tech_bay.append(draw_from_cache(cache))

    turn_counter = 1
    while player1.hull > 0 and player2.hull > 0:
        print("\n" + "#" * 40)
        print(f"Turn {turn_counter}")
        # Player 1's turn.
        player_turn(player1, player2, tech_bay, cache, logger, turn_counter, 'start', ai_agent)
        if player2.hull <= 0:
            break
        # Player 2's turn.
        player_turn(player2, player1, tech_bay, cache, logger, turn_counter, 'start', ai_agent)
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
