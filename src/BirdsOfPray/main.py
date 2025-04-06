# main.py

import random
import math
from copy import deepcopy
import BirdsOfPray.card_data as card_data # Import our card definitions and constants

# --- Helper Functions ---

def clear_console():
    # Simple way to clear console for better readability (might not work in all IDEs)
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def get_distance(pos1, pos2):
    """Calculates Manhattan distance between two points (tuples)."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_points_on_line(pos1, pos2):
    """Very basic line generation (includes endpoints). Not perfect for LoS."""
    points = set()
    x1, y1 = pos1
    x2, y2 = pos2
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.add((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return points

# --- Game Classes ---

class Unit:
    """Represents a unit on the board."""
    def __init__(self, card_code, owner_id, position):
        self.base_data = deepcopy(card_data.get_card_data(card_code))
        if not self.base_data:
            raise ValueError(f"Invalid card code for Unit: {card_code}")

        self.card_code = card_code
        self.owner_id = owner_id
        self.position = position # (x, y) tuple
        self.current_hp = self.base_data['hp']
        self.activated_this_turn = False
        self.can_attack_this_activation = True # Usually true, some abilities might disable
        self.ap = 0 # Action points for current activation

    def get_stat(self, stat_name):
        # Placeholder for future buffs/debuffs
        return self.base_data.get(stat_name, 0)

    def take_damage(self, amount):
        self.current_hp -= amount
        print(f"{self.base_data['name']} takes {amount} damage ({self.current_hp}/{self.base_data['hp']} HP remaining).")
        if self.current_hp <= 0:
            print(f"{self.base_data['name']} has been defeated!")
            return True # Indicates defeat
        return False

    def heal(self, amount):
        healed_amount = min(amount, self.base_data['hp'] - self.current_hp)
        self.current_hp += healed_amount
        if healed_amount > 0:
            print(f"{self.base_data['name']} heals {healed_amount} HP ({self.current_hp}/{self.base_data['hp']} HP).")
        return healed_amount > 0

    def move_to(self, new_position):
        # Assumes validation happened before calling
        self.position = new_position

    def __str__(self):
        return f"{self.base_data['name']} ({self.owner_id}) @ {self.position} [{self.current_hp} HP]"

class Player:
    """Represents a player."""
    def __init__(self, player_id, champion_code):
        self.id = player_id
        self.champion_code = champion_code
        self.food = card_data.STARTING_FOOD
        self.deck = [] # List of card codes
        self.hand = [] # List of card codes
        self.discard = [] # List of card codes
        self.units_on_board = {} # {unit_id: Unit object} - unit_id can be simple counter or unique hash

    def draw_card(self, game_deck_ref, game_discard_ref):
        if not game_deck_ref:
            if not game_discard_ref:
                print("Deck and Discard are empty! Cannot draw.")
                return False
            print("Deck empty. Shuffling discard pile into deck.")
            random.shuffle(game_discard_ref)
            game_deck_ref.extend(game_discard_ref)
            game_discard_ref.clear()

        if game_deck_ref:
            card = game_deck_ref.pop(0)
            self.hand.append(card)
            print(f"Player {self.id} drew {card_data.get_card_data(card)['name']} ({card}).")
            return True
        return False

    def gain_food(self, amount):
        self.food += amount
        print(f"Player {self.id} gains {amount} Food (Total: {self.food}).")

    def spend_food(self, amount):
        if self.food >= amount:
            self.food -= amount
            print(f"Player {self.id} spends {amount} Food (Remaining: {self.food}).")
            return True
        else:
            print(f"Player {self.id} does not have enough Food (Needs {amount}, Has {self.food}).")
            return False

    def discard_from_hand(self, card_code):
        if card_code in self.hand:
            self.hand.remove(card_code)
            self.discard.append(card_code)
            return True
        return False

    def add_unit(self, unit_object, unit_id):
        self.units_on_board[unit_id] = unit_object

    def remove_unit(self, unit_id):
        if unit_id in self.units_on_board:
            defeated_unit = self.units_on_board.pop(unit_id)
            # Put non-champion defeated units into discard
            if defeated_unit.base_data['type'] != 'Champion':
                 self.discard.append(defeated_unit.card_code)
                 print(f"{defeated_unit.base_data['name']} added to Player {self.id}'s discard pile.")
            return defeated_unit # Return the unit object in case needed (e.g., for VP)
        return None


class Board:
    """Represents the game board state."""
    def __init__(self, size=card_data.GRID_SIZE):
        self.width, self.height = size
        # Store board elements in a dictionary for sparse population: {(x, y): object}
        # object can be a Unit instance or a terrain/resource code ('2', '3', '4')
        self.grid = {}
        self.unit_positions = {} # {unit_id: (x, y)} for quick lookup

    def is_valid_pos(self, pos):
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def get_at_pos(self, pos):
        return self.grid.get(pos, None)

    def place_object(self, obj, pos):
        if not self.is_valid_pos(pos):
            print(f"Error: Position {pos} is outside board boundaries.")
            return False
        # Allow placing terrain/resource over empty space
        # Allow placing unit over empty space
        current_obj = self.get_at_pos(pos)
        if isinstance(obj, Unit):
            if current_obj is not None:
                 print(f"Error: Cannot place unit at {pos}, position occupied by {current_obj}.")
                 return False
            self.grid[pos] = obj
            self.unit_positions[obj.card_code + str(obj.owner_id)] = pos # Simple unique ID
            return True
        elif obj in ['2', '3', '4']: # Terrain or Resource
             if current_obj is not None:
                 print(f"Error: Cannot place terrain/resource at {pos}, position occupied by {current_obj}.")
                 return False
             self.grid[pos] = obj
             return True
        else:
            print(f"Error: Cannot place unknown object type: {obj}")
            return False

    def remove_object(self, pos):
        obj = self.grid.pop(pos, None)
        if isinstance(obj, Unit):
            # Also remove from unit_positions lookup
            unit_id_to_remove = None
            for uid, unit_pos in self.unit_positions.items():
                if unit_pos == pos:
                    unit_id_to_remove = uid
                    break
            if unit_id_to_remove:
                del self.unit_positions[unit_id_to_remove]
        return obj # Return the removed object

    def move_unit(self, unit, new_pos):
        if not isinstance(unit, Unit): return False
        old_pos = unit.position
        if self.is_valid_pos(new_pos) and self.get_at_pos(new_pos) is None:
            self.remove_object(old_pos)
            self.place_object(unit, new_pos)
            unit.move_to(new_pos) # Update unit's internal position
            return True
        return False

    def get_unit_by_id(self, unit_id):
        # Need to search grid if using simple ID, or have a better lookup
        for obj in self.grid.values():
            if isinstance(obj, Unit) and (obj.card_code + str(obj.owner_id)) == unit_id:
                return obj
        return None

    def get_units_for_player(self, player_id):
        units = []
        for obj in self.grid.values():
            if isinstance(obj, Unit) and obj.owner_id == player_id:
                units.append(obj)
        return units

    def display(self):
        print("\n--- BOARD STATE ---")
        header = "   " + " ".join(f"{i:<2}" for i in range(self.width))
        print(header)
        print("  +" + "--+" * self.width)
        for y in range(self.height):
            row_str = f"{y:<2}|"
            for x in range(self.width):
                obj = self.get_at_pos((x, y))
                if isinstance(obj, Unit):
                    # Simple representation: First letter of rank + Suit initial + Owner ID
                    rank_char = obj.base_data['rank'][0] if obj.base_data['rank'] != '10' else 'T'
                    suit_char = obj.base_data['suit'][0]
                    display = f"{rank_char}{suit_char}{obj.owner_id}"
                elif obj in ['2', '3', '4']:
                    display = f" {obj} " # Terrain/Resource
                else:
                    display = " . " # Empty
                row_str += f"{display[0:3]:<3}|" # Ensure fixed width
            print(row_str)
            print("  +" + "--+" * self.width)
        print("-" * len(header))

    def has_line_of_sight(self, pos1, pos2):
        """Simplified LoS check: Checks for Heavy Cover ('3') on the line between points."""
        if pos1 == pos2: return True # Can always see self

        line_points = get_points_on_line(pos1, pos2)
        # Exclude start and end points from the check
        points_between = line_points - {pos1, pos2}

        for point in points_between:
            obj = self.get_at_pos(point)
            if obj == '3': # Heavy Cover blocks LoS
                # Check if the object is actually terrain data
                terrain_data = card_data.TERRAIN_EFFECTS.get('3')
                if terrain_data and terrain_data['blocks_line_of_sight']:
                    print(f"LoS blocked by Heavy Cover at {point}")
                    return False
        return True

    def get_cover_bonus(self, target_pos):
        """Checks adjacent squares for cover relative to attacker (simplified)."""
        # This is highly simplified. Real cover depends on attacker position.
        # For now, just check if the target is *on* a cover square.
        obj = self.get_at_pos(target_pos)
        if obj in ['2', '3']:
            return card_data.TERRAIN_EFFECTS[obj]['defense_bonus']
        return 0


class Game:
    """Main game engine."""
    def __init__(self):
        self.board = Board()
        self.players = {
            1: None, # Player(1, champion_code)
            2: None, # Player(2, champion_code)
        }
        self.deck = [] # The main draw pile card codes
        self.discard_pile = [] # Global discard for terrain/caches? No, player discards used.
        self.current_player_id = 1
        self.current_round = 1
        self.game_over = False
        self.winner = None
        self._unit_id_counter = 0 # Simple way to give units unique IDs

    def _get_next_unit_id(self):
        self._unit_id_counter += 1
        return f"u{self._unit_id_counter}"

    def setup_game(self):
        print("--- AVIA ASCENDANCY SETUP ---")

        # 1. Choose Champions (Simplified: Assign first two Aces)
        available_aces = ['AC', 'AH', 'AD', 'AS']
        random.shuffle(available_aces)
        p1_champ = available_aces.pop(0)
        p2_champ = available_aces.pop(0)
        print(f"Player 1 chooses Champion: {card_data.get_card_data(p1_champ)['name']}")
        print(f"Player 2 chooses Champion: {card_data.get_card_data(p2_champ)['name']}")
        self.players[1] = Player(1, p1_champ)
        self.players[2] = Player(2, p2_champ)

        # Place Champions
        p1_start_pos = (self.board.width // 2, self.board.height - 1)
        p2_start_pos = (self.board.width // 2, 0)
        champ1_unit = Unit(p1_champ, 1, p1_start_pos)
        champ2_unit = Unit(p2_champ, 2, p2_start_pos)
        champ1_id = self._get_next_unit_id()
        champ2_id = self._get_next_unit_id()
        self.board.place_object(champ1_unit, p1_start_pos)
        self.board.place_object(champ2_unit, p2_start_pos)
        self.players[1].add_unit(champ1_unit, champ1_id)
        self.players[2].add_unit(champ2_unit, champ2_id)


        # 2. Prepare Deck (Remove Aces, 2s, 3s, 4s)
        full_deck = [r + s for s in ['C', 'H', 'D', 'S'] for r in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']]
        terrain_cards = [c for c in full_deck if c[0] in ['2', '3']]
        resource_cards = [c for c in full_deck if c[0] == '4']
        used_aces = [p1_champ, p2_champ]
        self.deck = [c for c in full_deck if c[0] not in ['A', '2', '3', '4'] or c in used_aces] # Keep chosen aces in potential pool? No, rules say discard others.
        self.deck = [c for c in full_deck if c[0] not in ['2', '3', '4'] and c not in available_aces and c not in used_aces] # Correct deck
        random.shuffle(self.deck)

        # 3. Place Terrain & Resources (Simplified Random Placement)
        num_low_cover = len([c for c in terrain_cards if c[0] == '2']) // 2 # Approx
        num_heavy_cover = len([c for c in terrain_cards if c[0] == '3']) // 2
        num_caches = len(resource_cards) // 2

        placed_count = 0
        max_attempts = self.board.width * self.board.height * 2
        attempts = 0
        while placed_count < num_low_cover and attempts < max_attempts:
            x, y = random.randint(0, self.board.width - 1), random.randint(1, self.board.height - 2) # Avoid start rows
            if self.board.get_at_pos((x,y)) is None:
                self.board.place_object('2', (x,y))
                placed_count += 1
            attempts += 1
        # Repeat for Heavy Cover and Caches
        placed_count = 0
        attempts = 0
        while placed_count < num_heavy_cover and attempts < max_attempts:
            x, y = random.randint(0, self.board.width - 1), random.randint(1, self.board.height - 2)
            if self.board.get_at_pos((x,y)) is None:
                 # Avoid placing adjacent initially (simple check)
                 is_adjacent_clear = True
                 for dx in [-1, 0, 1]:
                     for dy in [-1, 0, 1]:
                         if dx == 0 and dy == 0: continue
                         if self.board.get_at_pos((x+dx, y+dy)) in ['2', '3']:
                             is_adjacent_clear = False
                             break
                     if not is_adjacent_clear: break
                 if is_adjacent_clear:
                    self.board.place_object('3', (x,y))
                    placed_count += 1
            attempts += 1

        placed_count = 0
        attempts = 0
        while placed_count < num_caches and attempts < max_attempts:
             x, y = random.randint(0, self.board.width - 1), random.randint(1, self.board.height - 2)
             if self.board.get_at_pos((x,y)) is None:
                 self.board.place_object('4', (x,y))
                 placed_count += 1
             attempts += 1

        print(f"Placed terrain and {placed_count} food caches.")

        # 4. Starting Hand & Food (Food already set)
        print("Drawing starting hands...")
        for _ in range(card_data.STARTING_HAND_SIZE):
            self.players[1].draw_card(self.deck, self.players[1].discard)
            self.players[2].draw_card(self.deck, self.players[2].discard)

        print("Setup Complete!")
        input("Press Enter to start Round 1...")


    def switch_player(self):
        self.current_player_id = 3 - self.current_player_id # Switches between 1 and 2

    def display_game_state(self):
        clear_console()
        print(f"--- ROUND {self.current_round}/{card_data.MAX_ROUNDS} --- PLAYER {self.current_player_id}'s TURN ---")
        self.board.display()
        print("\n--- Player States ---")
        for pid, player in self.players.items():
            print(f"Player {pid}: Food={player.food}")
            print(f"  Hand: {[f'{card_data.get_card_data(c)['name']} ({c})' for c in player.hand]}")
            # print(f"  Discard: {len(player.discard)} cards")
            # print(f"  Deck: {len(self.deck)} cards remaining") # Global deck
            print(f"  Units: {[str(u) for u in self.board.get_units_for_player(pid)]}")
        print("-" * 20)

    def check_win_condition(self):
        p1_champ_alive = False
        p2_champ_alive = False
        for unit in self.board.grid.values():
            if isinstance(unit, Unit) and unit.base_data['type'] == 'Champion':
                if unit.owner_id == 1:
                    p1_champ_alive = True
                elif unit.owner_id == 2:
                    p2_champ_alive = True

        if not p1_champ_alive:
            self.game_over = True
            self.winner = 2
            print("Player 1's Champion defeated! Player 2 Wins!")
            return True
        if not p2_champ_alive:
            self.game_over = True
            self.winner = 1
            print("Player 2's Champion defeated! Player 1 Wins!")
            return True

        if self.current_round > card_data.MAX_ROUNDS:
            self.game_over = True
            # TODO: Implement VP scoring for tie-breaker
            print(f"Round limit ({card_data.MAX_ROUNDS}) reached. Game is a draw (VP scoring not implemented).")
            self.winner = 0 # Draw
            return True

        return False

    def resolve_combat(self, attacker_unit, defender_unit):
        print(f"\nCombat: {attacker_unit.base_data['name']} (P{attacker_unit.owner_id}) attacks {defender_unit.base_data['name']} (P{defender_unit.owner_id})")

        # Check Line of Sight
        if not self.board.has_line_of_sight(attacker_unit.position, defender_unit.position):
            print("Attack failed: Line of sight blocked!")
            return

        # Check Range
        distance = get_distance(attacker_unit.position, defender_unit.position)
        attack_range = attacker_unit.get_stat('range')
        if distance > attack_range:
            print(f"Attack failed: Target out of range ({distance} > {attack_range})")
            return

        # Roll to Hit
        roll = random.randint(1, 6)
        attack_bonus = attacker_unit.get_stat('attack')
        # TODO: Add other modifiers (abilities, etc.)
        attack_total = roll + attack_bonus
        print(f"Attacker rolls {roll} + {attack_bonus} (Attack) = {attack_total}")

        # Calculate Defense
        defense_base = defender_unit.get_stat('defense')
        cover_bonus = self.board.get_cover_bonus(defender_unit.position)
        # TODO: Add other modifiers (abilities, etc.)
        defense_total = defense_base + cover_bonus
        print(f"Defender has {defense_base} (Defense) + {cover_bonus} (Cover) = {defense_total}")

        # Compare
        if attack_total >= defense_total:
            print("Hit!")
            damage = attacker_unit.get_stat('damage') # Assuming 'damage' stat exists, otherwise use 'attack'? Let's assume base damage = attack stat for now.
            if 'damage' not in attacker_unit.base_data: # Use attack if no specific damage stat
                 damage = attacker_unit.get_stat('attack')
                 print(f"(Using Attack stat for base damage: {damage})")
            else:
                 damage = attacker_unit.get_stat('damage')
                 print(f"(Base damage: {damage})")

            # TODO: Damage modifiers

            defeated = defender_unit.take_damage(damage)
            if defeated:
                # Remove unit from board and player's control
                defender_owner = self.players[defender_unit.owner_id]
                self.board.remove_object(defender_unit.position)
                # Find the unit_id to remove from player
                unit_id_to_remove = None
                for uid, unit_obj in defender_owner.units_on_board.items():
                    if unit_obj == defender_unit:
                        unit_id_to_remove = uid
                        break
                if unit_id_to_remove:
                    defender_owner.remove_unit(unit_id_to_remove)
                # Check win condition immediately if a champion fell
                self.check_win_condition()
        else:
            print("Miss!")

    def execute_ability(self, caster_unit, ability_name):
        # Find the ability data
        ability_data = None
        for ab in caster_unit.base_data.get('abilities', []):
            if ab['name'] == ability_name:
                ability_data = ab
                break

        if not ability_data:
            print(f"Error: Ability '{ability_name}' not found for {caster_unit.base_data['name']}.")
            return False

        print(f"{caster_unit.base_data['name']} uses '{ability_name}'...")
        caster_player = self.players[caster_unit.owner_id]
        target = None # Required for many abilities

        # --- Implement Ability Logic ---
        # This needs to be expanded significantly for all abilities
        # Use ability_data['description'] and other fields as guide

        if ability_name == "Minor Heal" or ability_name == "Heal" or ability_name == "Greater Heal":
            heal_amount = {'Minor Heal': 2, 'Heal': 3, 'Greater Heal': 4}[ability_name]
            target_range = ability_data.get('range', 1)

            # Get potential targets
            potential_targets = []
            for unit in self.board.get_units_for_player(caster_unit.owner_id):
                 if get_distance(caster_unit.position, unit.position) <= target_range:
                     potential_targets.append(unit)

            if not potential_targets:
                 print("No valid targets in range.")
                 return False

            print("Select target unit to heal:")
            for i, unit in enumerate(potential_targets):
                 print(f"  {i}: {unit}")
            try:
                 choice = int(input("Enter target number: "))
                 if 0 <= choice < len(potential_targets):
                     target = potential_targets[choice]
                     target.heal(heal_amount)
                     return True
                 else:
                     print("Invalid choice.")
                     return False
            except ValueError:
                 print("Invalid input.")
                 return False

        elif ability_name == "Resourceful Leader": # Passive handled at start of turn
             print("(Passive ability, effect applied at start of turn)")
             return False # Cannot actively use a passive

        elif ability_name == "Scout Ahead":
             if caster_player.draw_card(self.deck, caster_player.discard):
                 # Maybe limit uses per turn if needed
                 return True
             else:
                 print("Could not draw card.")
                 return False

        elif ability_name == "Generates Food": # Passive handled at start of turn
             print("(Passive ability, effect applied at start of turn)")
             return False

        elif ability_name == "Ranged Shot" or ability_name == "Shadow Bolt" or ability_name == "Arcane Bolt":
             target_range = caster_unit.get_stat('range')
             potential_targets = []
             opponent_id = 3 - caster_unit.owner_id
             for unit in self.board.get_units_for_player(opponent_id):
                  dist = get_distance(caster_unit.position, unit.position)
                  if dist <= target_range and self.board.has_line_of_sight(caster_unit.position, unit.position):
                      potential_targets.append(unit)

             if not potential_targets:
                  print("No valid targets in range/LoS.")
                  return False

             print("Select target unit to attack:")
             for i, unit in enumerate(potential_targets):
                  print(f"  {i}: {unit}")
             try:
                  choice = int(input("Enter target number: "))
                  if 0 <= choice < len(potential_targets):
                      target = potential_targets[choice]
                      # Use standard combat resolution for damage spells for now
                      self.resolve_combat(caster_unit, target)
                      return True
                  else:
                      print("Invalid choice.")
                      return False
             except ValueError:
                  print("Invalid input.")
                  return False

        # --- Add more ability implementations here ---
        # e.g., Fierce Strike, Commander's Presence (passive check during combat),
        # Sanctuary, Precognitive Dodge (passive check during combat), Focused Blast,
        # Skirmish, Devastating Charge (check movement before attack), Flying (ignore terrain),
        # First Strike (reaction logic needed), Precision Attack (modify combat), etc.
        # Necromancy would need access to discard piles.
        # Obscuring Mist needs temporary terrain placement.

        else:
            print(f"Ability '{ability_name}' logic not implemented yet.")
            return False


    def handle_unit_activation(self, unit):
        player = self.players[unit.owner_id]
        unit.ap = 2 # Reset AP for activation
        unit.activated_this_turn = True
        unit.can_attack_this_activation = True # Reset attack flag

        while unit.ap > 0:
            self.display_game_state()
            print(f"\n--- Activating: {unit.base_data['name']} (P{unit.owner_id}) ---")
            print(f"Remaining AP: {unit.ap}")
            print("Available Actions:")
            print("  1: Move")
            print("  2: Attack")
            print("  3: Use Ability")
            print("  4: Consume Food Cache (if on one)")
            print("  5: Sacrifice Self (Hearts/Spades only)")
            print("  0: End Activation")

            action_choice = input("Choose action (0-5): ")

            if action_choice == '1': # Move
                if unit.ap < 1: print("Not enough AP."); continue
                move_speed = unit.get_stat('movement')
                print(f"Movement Speed: {move_speed}")
                try:
                    target_x = int(input("Enter target X coordinate: "))
                    target_y = int(input("Enter target Y coordinate: "))
                    target_pos = (target_x, target_y)

                    if not self.board.is_valid_pos(target_pos):
                        print("Invalid coordinates.")
                        continue

                    distance = get_distance(unit.position, target_pos)
                    if distance == 0:
                        print("Already at target position.")
                        continue
                    if distance > move_speed:
                        print(f"Target out of range ({distance} > {move_speed}).")
                        continue

                    # Pathfinding needed for complex movement (blocking terrain/units)
                    # Simplified: Check direct path for blockers (Heavy Cover or Units)
                    # TODO: Implement Flying logic (ignore terrain/units)
                    can_move = True
                    line_points = get_points_on_line(unit.position, target_pos)
                    points_between = line_points - {unit.position, target_pos}
                    for point in points_between:
                        obj = self.board.get_at_pos(point)
                        if isinstance(obj, Unit) or obj == '3': # Blocked by unit or heavy cover
                            print(f"Movement path blocked by object at {point}.")
                            can_move = False
                            break
                    if not can_move: continue

                    # Final check: is destination square empty?
                    if self.board.get_at_pos(target_pos) is not None:
                        print("Destination square is occupied.")
                        continue

                    # Execute move
                    if self.board.move_unit(unit, target_pos):
                        print(f"{unit.base_data['name']} moved to {target_pos}.")
                        unit.ap -= 1
                    else:
                        print("Move failed.")

                except ValueError:
                    print("Invalid coordinate input.")

            elif action_choice == '2': # Attack
                if unit.ap < 1: print("Not enough AP."); continue
                if not unit.can_attack_this_activation: print("Cannot attack again this activation."); continue

                attack_range = unit.get_stat('range')
                potential_targets = []
                opponent_id = 3 - unit.owner_id
                for target_unit in self.board.get_units_for_player(opponent_id):
                    dist = get_distance(unit.position, target_unit.position)
                    # Check range and LoS
                    if dist <= attack_range and self.board.has_line_of_sight(unit.position, target_unit.position):
                        potential_targets.append(target_unit)

                if not potential_targets:
                    print("No valid targets in range/LoS.")
                    continue

                print("Select target unit to attack:")
                for i, t_unit in enumerate(potential_targets):
                    print(f"  {i}: {t_unit}")
                try:
                    choice = int(input("Enter target number: "))
                    if 0 <= choice < len(potential_targets):
                        target = potential_targets[choice]
                        self.resolve_combat(unit, target)
                        unit.ap -= 1
                        # unit.can_attack_this_activation = False # Typically only one attack action per activation unless ability allows more
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Invalid input.")

            elif action_choice == '3': # Use Ability
                 abilities = unit.base_data.get('abilities', [])
                 active_abilities = [ab for ab in abilities if ab.get('cost', '').endswith('AP')] # Find abilities costing AP
                 if not active_abilities:
                     print("This unit has no activatable abilities.")
                     continue

                 print("Select ability to use:")
                 for i, ab in enumerate(active_abilities):
                     print(f"  {i}: {ab['name']} ({ab['cost']}) - {ab['description']}")

                 try:
                     choice = int(input("Enter ability number: "))
                     if 0 <= choice < len(active_abilities):
                         selected_ability = active_abilities[choice]
                         ability_cost_str = selected_ability.get('cost', '1 AP').split(' ')[0]
                         ability_cost = int(ability_cost_str) if ability_cost_str.isdigit() else 1

                         if unit.ap >= ability_cost:
                             if self.execute_ability(unit, selected_ability['name']):
                                 unit.ap -= ability_cost
                             else:
                                 print("Ability execution failed or was cancelled.")
                         else:
                             print(f"Not enough AP (Needs {ability_cost}, Has {unit.ap}).")
                     else:
                         print("Invalid choice.")
                 except ValueError:
                     print("Invalid input.")


            elif action_choice == '4': # Consume Food Cache
                if unit.ap < 1: print("Not enough AP."); continue
                obj_at_pos = self.board.get_at_pos(unit.position)
                if obj_at_pos == '4':
                    food_bonus = card_data.RESOURCE_EFFECTS['4']['food_bonus']
                    player.gain_food(food_bonus)
                    self.board.remove_object(unit.position) # Remove the cache
                    print(f"Consumed Food Cache for +{food_bonus} Food.")
                    unit.ap -= 1
                else:
                    print("Not standing on a Food Cache ('4').")

            elif action_choice == '5': # Sacrifice
                 if unit.ap < 1: print("Not enough AP."); continue
                 unit_suit = unit.base_data['suit']
                 if unit_suit == 'Hearts' or unit_suit == 'Spades':
                     # Determine food gain (e.g., base cost or fixed amount)
                     food_gain = unit.base_data.get('cost', 1) # Gain food equal to cost? Or fixed? Let's use cost.
                     # Check for Sacrifice Fodder ability
                     if any(ab['name'] == "Sacrifice Fodder" for ab in unit.base_data.get('abilities',[])):
                         food_gain += 1
                         print("(+1 Food from Sacrifice Fodder)")

                     print(f"Sacrificing {unit.base_data['name']} for {food_gain} Food.")
                     player.gain_food(food_gain)

                     # Remove unit
                     self.board.remove_object(unit.position)
                     unit_id_to_remove = None
                     for uid, unit_obj in player.units_on_board.items():
                         if unit_obj == unit:
                             unit_id_to_remove = uid
                             break
                     if unit_id_to_remove:
                         player.remove_unit(unit_id_to_remove) # Adds to discard automatically

                     unit.ap = 0 # End activation immediately
                     # Check win condition if a champion was somehow sacrificed (shouldn't happen)
                     self.check_win_condition()

                 else:
                     print("Only Hearts (Healers) or Spades (Gatherers) can be sacrificed.")


            elif action_choice == '0': # End Activation
                unit.ap = 0
            else:
                print("Invalid action choice.")

            # Check if game ended mid-activation (e.g., champion defeated)
            if self.game_over:
                unit.ap = 0 # Force end activation

        print(f"{unit.base_data['name']} finished activation.")
        input("Press Enter to continue...")


    def run_action_phase(self):
        print(f"\n--- PLAYER {self.current_player_id}'s ACTION PHASE ---")
        player = self.players[self.current_player_id]
        opponent = self.players[3 - self.current_player_id]

        # Reset activation status for all units of the current player
        for unit in self.board.get_units_for_player(self.current_player_id):
            unit.activated_this_turn = False
        # Opponent units don't reset until their turn

        player_passed = False
        opponent_passed = False # Track passes for alternating activation ending

        # Determine who activates first (usually the current player)
        activating_player_id = self.current_player_id

        while not (player_passed and opponent_passed):
            current_actor = self.players[activating_player_id]
            is_current_players_main_turn = (activating_player_id == self.current_player_id)

            self.display_game_state()
            print(f"\n--- Player {activating_player_id}'s turn to ACTIVATE ---")

            # Get units that can still be activated this turn
            available_units = [u for u in self.board.get_units_for_player(activating_player_id) if not u.activated_this_turn]

            print("Available Actions:")
            action_options = {}
            next_action_idx = 1

            # Option to activate a unit
            if available_units:
                print("  Activate Unit:")
                for i, unit in enumerate(available_units):
                    action_key = str(next_action_idx + i)
                    print(f"    {action_key}: {unit.base_data['name']} @ {unit.position}")
                    action_options[action_key] = ('activate', unit)
                next_action_idx += len(available_units)
            else:
                 print("  (No units available to activate)")


            # Options only available on your main turn (not opponent's activation slot)
            if is_current_players_main_turn:
                # Option to play a unit card
                playable_unit_cards = [c for c in current_actor.hand if card_data.get_card_data(c)['type'] == 'Unit']
                if playable_unit_cards:
                    print("  Play Unit Card from Hand:")
                    for i, card_code in enumerate(playable_unit_cards):
                        card_info = card_data.get_card_data(card_code)
                        action_key = str(next_action_idx + i)
                        print(f"    {action_key}: {card_info['name']} ({card_code}) - Cost: {card_info['cost']} Food")
                        action_options[action_key] = ('play_unit', card_code)
                    next_action_idx += len(playable_unit_cards)

                # Option to play a resource card (5-10)
                playable_resource_cards = [c for c in current_actor.hand if card_data.get_card_data(c)['rank'] in ['5','6','7','8','9','T']]
                if playable_resource_cards:
                    print("  Play Resource Card (Gain +1 Food):")
                    for i, card_code in enumerate(playable_resource_cards):
                        card_info = card_data.get_card_data(card_code)
                        action_key = str(next_action_idx + i)
                        print(f"    {action_key}: {card_info['name']} ({card_code})")
                        action_options[action_key] = ('play_resource', card_code)
                    next_action_idx += len(playable_resource_cards)

            # Option to Pass
            pass_key = '0'
            print(f"  {pass_key}: Pass Activation")
            action_options[pass_key] = ('pass', None)

            # Get Player Choice
            choice = input("Choose action: ")

            if choice in action_options:
                action_type, data = action_options[choice]

                if action_type == 'activate':
                    unit_to_activate = data
                    self.handle_unit_activation(unit_to_activate)
                    # Reset pass status since an action was taken
                    player_passed = False
                    opponent_passed = False

                elif action_type == 'play_unit':
                    if not is_current_players_main_turn:
                        print("Cannot play cards during opponent's activation slot.")
                        continue # Don't switch player yet, let them choose again

                    card_code = data
                    card_info = card_data.get_card_data(card_code)
                    cost = card_info['cost']

                    if current_actor.food >= cost:
                        # Find valid placement squares (adjacent to friendly units)
                        valid_squares = set()
                        for unit in self.board.get_units_for_player(activating_player_id):
                            for dx in [-1, 0, 1]:
                                for dy in [-1, 0, 1]:
                                    if dx == 0 and dy == 0: continue
                                    adj_pos = (unit.position[0] + dx, unit.position[1] + dy)
                                    if self.board.is_valid_pos(adj_pos) and self.board.get_at_pos(adj_pos) is None:
                                        valid_squares.add(adj_pos)

                        if not valid_squares:
                            print("No valid squares adjacent to friendly units to place the new unit.")
                            continue # Let player choose again

                        print("Choose placement square:")
                        valid_list = list(valid_squares)
                        for i, pos in enumerate(valid_list):
                            print(f"  {i}: {pos}")

                        try:
                            sq_choice = int(input("Enter square number: "))
                            if 0 <= sq_choice < len(valid_list):
                                place_pos = valid_list[sq_choice]
                                if current_actor.spend_food(cost):
                                    current_actor.discard_from_hand(card_code) # Discard after successful payment
                                    new_unit = Unit(card_code, activating_player_id, place_pos)
                                    new_unit.activated_this_turn = True # Cannot act turn it's played
                                    unit_id = self._get_next_unit_id()
                                    if self.board.place_object(new_unit, place_pos):
                                         current_actor.add_unit(new_unit, unit_id)
                                         print(f"Played {card_info['name']} at {place_pos}.")
                                         # Reset pass status
                                         player_passed = False
                                         opponent_passed = False
                                    else:
                                         print("Failed to place unit on board (shouldn't happen after check). Refunding food.")
                                         current_actor.gain_food(cost) # Refund
                                         current_actor.hand.append(card_code) # Put card back
                                         current_actor.discard.remove(card_code) # Remove from discard if it got there
                            else:
                                print("Invalid square choice.")
                        except ValueError:
                            print("Invalid input.")
                    else:
                        print(f"Not enough Food (Need {cost}, Have {current_actor.food}).")


                elif action_type == 'play_resource':
                    if not is_current_players_main_turn:
                        print("Cannot play cards during opponent's activation slot.")
                        continue # Don't switch player yet, let them choose again

                    card_code = data
                    card_info = card_data.get_card_data(card_code)
                    current_actor.discard_from_hand(card_code)
                    current_actor.gain_food(card_data.SUIT_RESOURCE_VALUE) # Simplified: +1 generic food
                    print(f"Played {card_info['name']} for +{card_data.SUIT_RESOURCE_VALUE} Food.")
                    # Reset pass status
                    player_passed = False
                    opponent_passed = False

                elif action_type == 'pass':
                    print(f"Player {activating_player_id} passes activation.")
                    if activating_player_id == self.current_player_id:
                        player_passed = True
                    else:
                        opponent_passed = True

                # Switch activating player only if an action was taken or pass occurred
                if action_type != 'play_unit' or action_type != 'play_resource' or action_type == 'pass' or action_type == 'activate':
                     activating_player_id = 3 - activating_player_id # Switch turn for next activation

            else:
                print("Invalid choice.")
                # Don't switch player on invalid choice

            # Check if game ended mid-action phase
            if self.game_over:
                break

        print("Both players passed consecutively. Action Phase ends.")


    def run_turn(self):
        player = self.players[self.current_player_id]
        print(f"\n=== PLAYER {self.current_player_id}'s TURN START (Round {self.current_round}) ===")

        # 1. Start Phase
        print("\n-- Start Phase --")
        # Base Income
        player.gain_food(card_data.BASE_FOOD_INCOME)
        # Gatherer Income (Spades)
        spade_units = [u for u in self.board.get_units_for_player(self.current_player_id) if u.base_data['suit'] == 'Spades']
        spade_food = 0
        for unit in spade_units:
             # Check for specific passive abilities like "Generates Food" or "Hardy Worker"
             if any(ab['name'] == "Generates Food" for ab in unit.base_data.get('abilities',[])):
                 spade_food += 1
             if any(ab['name'] == "Hardy Worker" for ab in unit.base_data.get('abilities',[])):
                 spade_food += 1 # Hardy worker might grant extra on top of base spade gen? Rule unclear, assume yes.
        if spade_food > 0:
             player.gain_food(spade_food)

        # Champion Passives (Resourceful Leader)
        champion = None
        for unit in self.board.get_units_for_player(self.current_player_id):
            if unit.base_data['type'] == 'Champion':
                champion = unit
                break
        if champion and any(ab['name'] == "Resourceful Leader" for ab in champion.base_data.get('abilities',[])):
             print(f"({champion.base_data['name']} passive)")
             player.gain_food(1)


        # Draw Card
        player.draw_card(self.deck, player.discard)

        input("Press Enter to proceed to Action Phase...")

        # 2. Action Phase
        self.run_action_phase()
        if self.game_over: return # End turn early if game ended

        # 3. End Phase
        print("\n-- End Phase --")
        # Discard down to max hand size
        while len(player.hand) > card_data.MAX_HAND_SIZE:
            self.display_game_state() # Show hand before discard prompt
            print(f"Hand size ({len(player.hand)}) exceeds maximum ({card_data.MAX_HAND_SIZE}). Choose card to discard:")
            for i, card_code in enumerate(player.hand):
                print(f"  {i}: {card_data.get_card_data(card_code)['name']} ({card_code})")
            try:
                choice = int(input("Enter card number to discard: "))
                if 0 <= choice < len(player.hand):
                    card_to_discard = player.hand[choice]
                    player.discard_from_hand(card_to_discard)
                    print(f"Discarded {card_data.get_card_data(card_to_discard)['name']}.")
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")

        print(f"=== PLAYER {self.current_player_id}'s TURN END ===")
        input("Press Enter to continue...")


    def run_game(self):
        self.setup_game()

        while not self.game_over:
            self.run_turn() # Player 1's turn

            if self.game_over: break

            self.switch_player()
            self.run_turn() # Player 2's turn

            if self.game_over: break

            # End of round cleanup/checks if needed
            self.current_round += 1
            if not self.game_over: # Only switch back if game continues
                 self.switch_player() # Back to Player 1 for next round start

            # Final round check after both players have acted
            if self.check_win_condition():
                 break # Exit loop if game ended due to rounds/VP

        # Game Over message
        print("\n--- GAME OVER ---")
        if self.winner == 0:
            print("The game is a draw!")
        elif self.winner is not None:
            print(f"Player {self.winner} is victorious!")
        else:
            print("The game ended unexpectedly.")


# --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    game.run_game()