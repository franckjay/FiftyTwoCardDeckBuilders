game_rules_markdown = """
# Avian Ascendancy: Rules of Engagement

## 1. Overview & Theme

**Avian Ascendancy** is a 2-player tactical deckbuilder wargame set in a fantasy world ruled by sentient bird factions. Players command unique champions and summon feathered warriors, healers, mages, and gatherers to control the battlefield, utilizing a standard poker deck as the core resource and unit pool.

## 2. Objective

The primary objective is to defeat the opponent's **Champion** unit. Alternatively, if after 8 full rounds neither Champion is defeated, the player with the most Victory Points (earned through controlling objectives, defeating units, etc. - *specific scoring TBD*) wins.

## 3. Components

*   **Game Board:** A virtual grid, typically 9x9 squares.
*   **Deck:** One standard 52-card poker deck.
*   **Player Resources:** Each player tracks their **Food** total.
*   **Dice:** At least one six-sided die (d6) for combat resolution.

## 4. Factions & Suits

The four suits of the deck represent the core factions and their general roles:

*   **Clubs (The Talon Confederacy - Raptors):** **Warriors.** Excel in melee combat, high attack and health. (Eagles, Hawks, Falcons)
*   **Hearts (The Dove Concord - Pigeons/Doves):** **Healers & Support.** Focus on healing units, buffing allies, and resilience. (Doves, Pigeons, Peacocks)
*   **Diamonds (The Obsidian Parliament - Owls/Ravens):** **Spellcasters & Ranged Attackers.** Utilize powerful spells for damage, control, and utility, often attacking from a distance. (Owls, Ravens, Vultures - *Necromancy*)
*   **Spades (The Foragers' Union - Quails/Hummingbirds):** **Gatherers & Skirmishers.** Specialize in resource generation (Food), board mobility, and utility actions like drawing cards. (Quails, Hummingbirds, Woodpeckers)

## 5. Setup

1.  **Choose Champions:** Separate the four Aces from the deck. Players secretly choose one Ace to be their Champion. Reveal simultaneously. The chosen Champions are placed on designated starting squares on opposite sides of the board (e.g., center square of their respective back rows). The two unchosen Aces are removed from the game.
2.  **Prepare the Deck:** Remove the 2s, 3s, and 4s from the remaining deck (48 cards).
3.  **Place Terrain & Resources:**
    *   Players take turns placing the 2s and 3s onto empty squares on the board. They cannot be placed in the starting rows or adjacent to each other initially.
        *   **2s:** Represent **Low Cover** (Provides a defensive bonus, e.g., -1 to hit).
        *   **3s:** Represent **Heavy Cover** (Provides a better defensive bonus, e.g., -2 to hit, and blocks line of sight - **Obscuring**).
    *   Players then take turns placing the 4s onto empty squares. These represent **Food Caches**. A unit moving onto a Food Cache square can consume it as an action to gain a one-time Food bonus (e.g., +3 Food). Once consumed, the 4 is removed from the board and placed in the discard pile.
4.  **Shuffle & Draw:** Shuffle the remaining deck (Aces, 5s through Kings - 44 cards total) thoroughly to form the Draw Pile. Place it centrally. Create a Discard Pile area next to it.
5.  **Starting Hand & Food:** Each player draws an initial hand of 3 cards and starts with 2 Food.

## 6. Card Types

*   **Aces (Champions):** Unique, powerful starting units with multiple health points and strong abilities. Cannot be removed from the board unless defeated. If defeated, that player loses the game.
*   **Face Cards (Jack, Queen, King):** **Units.** These are summoned to the board by paying their Food cost. Each has Health, Attack, Movement, and potentially special abilities or spells. More powerful units (Kings > Queens > Jacks) generally cost more Food.
*   **Numbered Cards (5 through 10):** **Suit Resources.** These cards are not units. They are played from the hand directly to the Discard Pile during the Action Phase to generate **Suit-Specific Food**. For example, playing a 7 of Hearts provides 1 'Heart Food'. This can be used to help pay the Food cost of summoning Heart units (Face Cards) or activating certain Heart abilities. The number on the card (5-10) might influence the amount or have secondary effects (*optional complexity*). For now, assume each card (5-10) provides 1 Food specific to its suit when played this way.
*   **2s & 3s (Terrain):** Placed during setup as Cover. Not part of the draw deck.
*   **4s (Resources):** Placed during setup as Food Caches. Not part of the draw deck. Consumed for Food.

## 7. Resources: Food

*   **Primary Cost:** Food is the main resource used to play Unit cards (Face Cards) from your hand onto the board.
*   **Generation:**
    *   **Base Income:** At the start of each turn, players gain a base amount of Food (e.g., 1 Food).
    *   **Gatherers:** Each Spade unit (Gatherer class) on the board under your control generates additional Food at the start of your turn (e.g., +1 Food per Spade unit).
    *   **Food Caches (4s):** Consuming a Food Cache grants a one-time Food bonus.
    *   **Sacrifice:** As an action, a player may sacrifice one of their Heart (Healer) or Spade (Gatherer) units currently on the board. Remove the unit and gain Food equal to a set value or perhaps its initial cost.
    *   **Suit Resources (5-10):** Playing a numbered card (5-10) generates 1 Food specific to that card's suit. This can contribute towards the generic Food cost of summoning a unit of that same suit. *Example: A Queen of Clubs costs 4 Food. You could pay this with 2 base Food and by playing a 5 of Clubs and a 10 of Clubs from your hand.*

## 8. Gameplay & Turn Structure

The game lasts for a maximum of **8 Rounds**. Each Round consists of both players taking a turn. A player's turn follows these phases:

1.  **Start Phase:**
    *   **Gain Resources:** Gain base Food (e.g., +1). Gain additional Food for each Spade unit you control.
    *   **Draw Card(s):** Draw 1 card from the Draw Pile. If the Draw Pile is empty, shuffle the Discard Pile to create a new Draw Pile, then draw.
2.  **Action Phase:**
    *   Players **alternate activating one unit** they control on the board, starting with the player whose turn it is.
    *   **Unit Activation:** When a unit is activated, it gets **2 Action Points (AP)** to spend on the following actions (each costs 1 AP unless specified otherwise):
        *   **Move:** Move the unit up to its Movement speed in squares (orthogonally or diagonally). Cannot move through other units or Heavy Cover (unless the unit has a special ability).
        *   **Attack:** Perform a melee or ranged attack against an enemy unit within range and line of sight. (See Combat).
        *   **Use Ability/Spell:** Activate a special ability or spell listed on the unit's card. Some abilities might cost 2 AP or have other costs (like Food).
        *   **Consume Food Cache:** If on a square with a 4, spend 1 AP to consume it, gain the Food bonus, and remove the 4 from the board.
        *   **Gather (Spades Only - Optional):** A Spade unit might use an action to generate extra Food or perform another utility function.
    *   **Player Actions (Can be done *instead* of activating a unit when it's your turn to activate):**
        *   **Play Unit Card:** Pay the Food cost (using general Food and/or Suit-Specific Food from Numbered Cards) to place a Face Card unit from your hand onto an empty square adjacent to your Champion or another friendly unit. The new unit cannot act the turn it is played.
        *   **Play Suit Resource Card:** Play a Numbered Card (5-10) from your hand to the Discard Pile to gain 1 Suit-Specific Food, usable towards summoning units of that suit.
    *   Activation continues back and forth until **both players pass consecutively**, indicating they have no more units they wish to activate or actions they wish to take.
3.  **End Phase:**
    *   **Discard:** Discard cards from your hand until you reach the maximum hand size of **4**. Choose which cards to discard.
    *   Pass the turn to the opponent.

## 9. Combat

*   **Initiating:** An activated unit uses an Attack action against a valid target (within range, line of sight not blocked by Heavy Cover unless specified).
*   **Rolling:** The attacking player rolls a d6.
*   **Calculating Hit:** Add the attacker's Attack bonus (from their card) and any other relevant modifiers (e.g., buffs, terrain penalties for the defender). Compare this total to the defender's Defense value (base defense + cover bonus). If the modified roll is greater than or equal to the defender's Defense, the attack hits.
*   **Damage:** If the attack hits, the attacker deals damage equal to their Damage value (potentially modified by abilities or critical hits on a high roll like a 6). Subtract this damage from the defender's Health.
*   **Defeat:** If a unit's Health reaches 0 or less, it is defeated and removed from the board, placed in its owner's Discard Pile. (Champions are removed but trigger game end).

## 10. Abilities & Spells (Examples)

Units (especially Face Cards and Champions) have unique abilities:

*   **Raptors (Clubs):** High Attack, Charge (Move + Attack bonus), Cleave (hit adjacent enemies).
*   **Doves (Hearts):** Heal (restore Health), Mend (remove negative effects), Sanctuary (protective aura), Sacrifice (gain Food when defeated).
*   **Owls/Ravens (Diamonds):** Ranged Attack, Spell Barrage (damage), Obscure (create temporary blocking terrain/effect), Stun (target loses next activation), Necromancy (Vulture specific? Return a defeated unit from discard pile to hand or board with reduced stats).
*   **Quails/Hummingbirds (Spades):** Generate Food, Scout (reveal opponent's hand card?), Swift (high movement), Forage (draw extra card), Rally (grant bonus AP or attack to adjacent ally).

## 11. Deck & Discard

*   Cards played (Units, Suit Resources) or discarded go to the owner's Discard Pile.
*   Defeated units go to their owner's Discard Pile.
*   When the Draw Pile is empty and a player needs to draw, the Discard Pile is shuffled thoroughly to become the new Draw Pile.

## 12. End of Game & Winning

*   The game ends immediately if a player's **Champion** is defeated. The opposing player wins.
*   If 8 full rounds are completed and neither Champion is defeated, the player with the most Victory Points wins. (Victory Point system needs further definition - e.g., points for defeated enemy units, controlling center squares, remaining Food, etc.).
"""
