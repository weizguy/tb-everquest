# game/combat.py

import random
import time # For slight pauses to improve readability

class Combat:
    """
    Manages the turn-based combat system between a player and one or more enemies.
    """

    def __init__(self):
        # Combat-specific variables could be stored here if needed
        pass

    @staticmethod
    def display_combat_status(player, enemies):
        """Displays the current health of the player and all enemies."""
        print("\n--- Combat Status ---")
        print(f"{player.name}: {player.health}/{player.max_health} HP")
        for enemy in enemies:
            print(f"{enemy.name}: {enemy.health}/{enemy.max_health} HP")
        print("--------------------")

    @staticmethod
    def get_initiative(player, enemies):
        """Determines turn order based on a simple initiative roll."""
        # A more complex system might involve Dexterity or other stats
        player_initiative = random.randint(1, 20) + player.get_initiative_bonus() # Assume player has an initiative bonus
        enemy_initiatives = {enemy: random.randint(1, 20) + enemy.get_initiative_bonus() for enemy in enemies} # Assume enemies also have initiative bonus

        turn_order = []
        turn_order.append((player, player_initiative))
        for enemy, initiative in enemy_initiatives.items():
            turn_order.append((enemy, initiative))

        # Sort by initiative (higher goes first)
        turn_order.sort(key=lambda x: x[1], reverse=True)

        print("\n--- Initiative Roll ---")
        for entity, initiative in turn_order:
            print(f"{entity.name} rolled {initiative} initiative.")
        time.sleep(1)
        print("-----------------------")
        return [entity for entity, _ in turn_order]

    @classmethod
    def initiate_combat(cls, player, enemies):
        """
        Starts and manages a combat encounter.
        Can take a single enemy or a list of enemies.
        """
        if not isinstance(enemies, list):
            enemies = [enemies] # Ensure enemies is always a list

        print("\n!!! COMBAT INITIATED !!!")
        Combat.display_combat_status(player, enemies)

        # Determine turn order
        turn_order = Combat.get_initiative(player, enemies)
        current_turn_index = 0

        while player.is_alive() and any(enemy.is_alive() for enemy in enemies):
            current_combatant = turn_order[current_turn_index]

            if current_combatant == player:
                cls._handle_player_turn(player, enemies)
            elif isinstance(current_combatant, type(enemies[0])): # Check if it's an enemy
                if current_combatant.is_alive():
                    cls._handle_enemy_turn(current_combatant, player)
                else:
                    print(f"The defeated {current_combatant.name} skips its turn.")

            # Check if combat ends after the turn
            if not player.is_alive() or not any(enemy.is_alive() for enemy in enemies):
                break

            current_turn_index = (current_turn_index + 1) % len(turn_order) # Next combatant in order
            Combat.display_combat_status(player, enemies)
            time.sleep(1) # Pause for readability between turns

        print("\n--- Combat Ended ---")
        if player.is_alive():
            print("You are victorious!")
            # Award XP and loot
            total_xp = sum(enemy.loot_xp for enemy in enemies if not enemy.is_alive())
            player.gain_experience(total_xp)
            for enemy in enemies:
                if not enemy.is_alive():
                    player.current_room.add_loot(enemy.loot_items) # Add loot to the room
                    print(f"The {enemy.name} dropped some items!")
        else:
            print("You have been defeated! Game Over.")

        return player.is_alive() # Return True for victory, False for defeat

    @staticmethod
    def _handle_player_turn(player, enemies):
        """Handles player's actions during their turn."""
        print(f"\n--- {player.name}'s Turn ---")
        while True:
            action = input("What will you do? (attack [enemy name], use [item name], defend, run): ").lower().strip()
            action_parts = action.split()
            verb = action_parts[0] if action_parts else ""
            target_name = " ".join(action_parts[1:]) if len(action_parts) > 1 else ""

            if verb == "attack":
                target_enemy = next((e for e in enemies if e.name.lower() == target_name and e.is_alive()), None)
                if target_enemy:
                    player.attack(target_enemy) # Player's attack method from player.py
                    break
                else:
                    print("That enemy is not here or already defeated. Try again.")
            elif verb == "use":
                # Assuming player has a use_item method that returns True on success
                if player.use_item(target_name):
                    break
                else:
                    print(f"You don't have '{target_name}' or can't use it now.")
            elif verb == "defend":
                player.defend() # Player's defend method from player.py
                print("You brace yourself for incoming attacks.")
                break
            elif verb == "run":
                # Implement a chance to run away
                if random.random() < 0.5: # 50% chance to run
                    print("You successfully flee from combat!")
                    player.reset_defense() # Reset defense status
                    return False # Indicate that combat should end
                else:
                    print("You try to run, but the enemies block your escape!")
                    break
            else:
                print("Invalid action. Try 'attack', 'use', 'defend', or 'run'.")
        player.reset_defense() # Reset defense status at the end of player's turn


    @staticmethod
    def _handle_enemy_turn(enemy, player):
        """Handles an enemy's actions during its turn."""
        print(f"\n--- {enemy.name}'s Turn ---")
        # Simple AI: Enemy always attacks the player
        if enemy.is_alive():
            enemy.attack(player) # Enemy's attack method from enemies.py
        time.sleep(0.5) # Slight pause for readability

