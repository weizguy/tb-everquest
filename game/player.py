# game/player.py

from .items import Item, Weapon, Armor, Potion, get_item_class # Import necessary item classes and helper
import random # For dice rolls, etc.

class Player:
    """
    Represents the player character in the game.
    """
    def __init__(self, name="Hero"):
        self.name = name
        self.current_room = None  # Holds a reference to the current Room object
        self.inventory = []       # List to store Item objects
        self.equipped_items = {   # Dictionary to store equipped items by slot
            "head": None,
            "body": None,
            "hands": None,
            "legs": None,
            "feet": None,
            "main_hand": None,
            "off_hand": None,
            "ring_1": None,
            "ring_2": None
            # Add more slots as needed (e.g., "neck", "back", "trinket")
        }

        # Player Stats
        self.max_health = 100
        self.health = self.max_health
        self.max_mana = 50
        self.mana = self.max_mana
        self.attack_power = 10 # Base attack
        self.defense = 5       # Base defense
        self.strength = 10
        self.dexterity = 10
        self.intelligence = 10
        self.experience = 0
        self.level = 1
        self.gold = 0

        self._defending = False # Internal flag for defense action

    def set_current_room(self, room):
        """Sets the player's current location."""
        self.current_room = room

    def get_effective_attack_power(self):
        """Calculates the player's total attack power, including equipped weapon."""
        total_attack = self.attack_power + (self.strength // 2) # Base + Strength bonus
        if self.equipped_items["main_hand"] and isinstance(self.equipped_items["main_hand"], Weapon):
            total_attack += self.equipped_items["main_hand"].damage
        return total_attack

    def get_effective_defense(self):
        """Calculates the player's total defense, including equipped armor."""
        total_defense = self.defense + (self.dexterity // 2) # Base + Dexterity bonus
        for slot, item in self.equipped_items.items():
            if isinstance(item, Armor):
                total_defense += item.defense
        if self._defending:
            total_defense *= 2 # Double defense when defending
        return total_defense

    def get_initiative_bonus(self):
        """Calculates the player's initiative bonus for combat."""
        return self.dexterity // 2

    def is_alive(self):
        """Checks if the player is still alive."""
        return self.health > 0

    def take_damage(self, damage):
        """Reduces the player's health by the given damage amount, considering defense."""
        effective_defense = self.get_effective_defense()
        actual_damage = max(0, damage - effective_defense)
        self.health -= actual_damage
        if self.health < 0:
            self.health = 0
        print(f"You take {actual_damage} damage. Current HP: {self.health}/{self.max_health}")
        if not self.is_alive():
            print("You have been defeated!")

    def heal(self, amount):
        """Restores health to the player."""
        self.health = min(self.max_health, self.health + amount)
        print(f"You heal {amount} health. Current HP: {self.health}/{self.max_health}")

    def restore_mana(self, amount):
        """Restores mana to the player."""
        self.mana = min(self.max_mana, self.mana + amount)
        print(f"You restore {amount} mana. Current MP: {self.mana}/{self.max_mana}")

    def attack(self, target_enemy):
        """Performs an attack on a target enemy."""
        damage = self.get_effective_attack_power()
        print(f"You attack the {target_enemy.name}!")
        target_enemy.take_damage(damage)

    def defend(self):
        """Sets the player to a defending state for the next turn."""
        self._defending = True

    def reset_defense(self):
        """Resets the defending state after a turn."""
        self._defending = False

    def move(self, direction, game_world):
        """Attempts to move the player in the given direction."""
        if direction in self.current_room.exits:
            next_room_id = self.current_room.exits[direction]
            next_room = game_world.get_room_by_id(next_room_id)
            if next_room:
                self.current_room = next_room
                print(f"You move {direction} into the {self.current_room.name}.")
                return True
            else:
                print(f"There's no room with ID '{next_room_id}'. This might be a game data error.")
                return False
        else:
            print(f"You cannot go {direction} from here.")
            return False

    def add_item(self, item):
        """Adds an item to the player's inventory."""
        self.inventory.append(item)
        print(f"You added '{item.name}' to your inventory.")

    def remove_item(self, item_name):
        """
        Removes an item from the inventory by name and returns it.
        Returns None if the item is not found.
        """
        for i, item in enumerate(self.inventory):
            if item.name.lower() == item_name.lower():
                return self.inventory.pop(i)
        return None

    def display_inventory(self):
        """Prints the player's current inventory."""
        print("\n--- Inventory ---")
        if not self.inventory:
            print("Your inventory is empty.")
        else:
            for item in self.inventory:
                print(f"- {item.name}: {item.description}")
        print("-----------------")

    def equip_item(self, item_name):
        """Equips an item from the inventory."""
        item_to_equip = None
        for i, item in enumerate(self.inventory):
            if item.name.lower() == item_name.lower():
                item_to_equip = self.inventory.pop(i)
                break

        if not item_to_equip:
            print(f"You don't have '{item_name}' in your inventory.")
            return

        if isinstance(item_to_equip, Weapon):
            slot = "main_hand" # Assuming single main hand weapon for now
            if self.equipped_items[slot]:
                self.inventory.append(self.equipped_items[slot]) # Unequip old weapon
                print(f"You unequip {self.equipped_items[slot].name}.")
            self.equipped_items[slot] = item_to_equip
            print(f"You equip {item_to_equip.name}.")
        elif isinstance(item_to_equip, Armor):
            slot = item_to_equip.armor_slot
            if slot in self.equipped_items:
                if self.equipped_items[slot]:
                    self.inventory.append(self.equipped_items[slot]) # Unequip old armor
                    print(f"You unequip {self.equipped_items[slot].name}.")
                self.equipped_items[slot] = item_to_equip
                print(f"You equip {item_to_equip.name} in the {slot} slot.")
            else:
                print(f"Cannot equip {item_to_equip.name}: Invalid armor slot '{slot}'.")
                self.inventory.append(item_to_equip) # Put it back if slot invalid
        else:
            print(f"You cannot equip {item_to_equip.name}.")
            self.inventory.append(item_to_equip) # Put it back if not equippable

    def unequip_item(self, slot_name):
        """Unequips an item from the given slot and places it in inventory."""
        if slot_name in self.equipped_items and self.equipped_items[slot_name]:
            item = self.equipped_items[slot_name]
            self.inventory.append(item)
            self.equipped_items[slot_name] = None
            print(f"You unequipped {item.name} from {slot_name}.")
        else:
            print(f"Nothing equipped in the '{slot_name}' slot.")

    def use_item(self, item_name):
        """Uses a consumable item from the inventory."""
        for i, item in enumerate(self.inventory):
            if item.name.lower() == item_name.lower() and isinstance(item, Potion):
                if item.use(self): # Potion's use method handles the effect
                    self.inventory.pop(i) # Remove item after use
                    return True
                else:
                    return False # Potion couldn't be used (e.g., full health)
        print(f"You don't have a consumable item named '{item_name}'.")
        return False

    def gain_experience(self, amount):
        """Adds experience points and checks for level up."""
        self.experience += amount
        print(f"You gained {amount} experience points.")
        while self.experience >= self._xp_for_next_level():
            self._level_up()

    def _xp_for_next_level(self):
        """Calculates XP needed for the next level."""
        # Simple exponential scaling example
        return 100 * (self.level ** 1.5)

    def _level_up(self):
        """Increases player level and stats."""
        self.level += 1
        self.max_health += 10
        self.health = self.max_health # Fully heal on level up
        self.max_mana += 5
        self.mana = self.max_mana
        self.attack_power += 2
        self.defense += 1
        self.strength += 1
        self.dexterity += 1
        self.intelligence += 1
        print(f"Congratulations! You reached Level {self.level}!")
        print("Your stats have improved!")

    def display_stats(self):
        """Displays the player's current stats."""
        print(f"\n--- {self.name}'s Stats (Level {self.level}) ---")
        print(f"HP: {self.health}/{self.max_health}")
        print(f"MP: {self.mana}/{self.max_mana}")
        print(f"Attack Power: {self.get_effective_attack_power()} (Base: {self.attack_power})")
        print(f"Defense: {self.get_effective_defense()} (Base: {self.defense})")
        print(f"Strength: {self.strength}")
        print(f"Dexterity: {self.dexterity}")
        print(f"Intelligence: {self.intelligence}")
        print(f"Experience: {self.experience} / {int(self._xp_for_next_level())}")
        print(f"Gold: {self.gold}")
        print("Equipped Items:")
        for slot, item in self.equipped_items.items():
            print(f"  {slot.replace('_', ' ').title()}: {item.name if item else 'None'}")
        print("-----------------------------")


    def to_dict(self):
        """Converts the player object to a dictionary for saving."""
        return {
            'name': self.name,
            'current_room_id': self.current_room.room_id if self.current_room else None,
            'inventory': [item.to_dict() for item in self.inventory],
            'equipped_items': {slot: item.to_dict() if item else None for slot, item in self.equipped_items.items()},
            'max_health': self.max_health,
            'health': self.health,
            'max_mana': self.max_mana,
            'mana': self.mana,
            'attack_power': self.attack_power,
            'defense': self.defense,
            'strength': self.strength,
            'dexterity': self.dexterity,
            'intelligence': self.intelligence,
            'experience': self.experience,
            'level': self.level,
            'gold': self.gold
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Player object from a dictionary for loading."""
        player = cls(data['name'])
        player.max_health = data['max_health']
        player.health = data['health']
        player.max_mana = data['max_mana']
        player.mana = data['mana']
        player.attack_power = data['attack_power']
        player.defense = data['defense']
        player.strength = data['strength']
        player.dexterity = data['dexterity']
        player.intelligence = data['intelligence']
        player.experience = data['experience']
        player.level = data['level']
        player.gold = data['gold']

        # Reconstruct inventory items
        for item_data in data.get('inventory', []):
            item_type = item_data.get('type', 'Item')
            item_class = get_item_class(item_type)
            player.inventory.append(item_class.from_dict(item_data))

        # Reconstruct equipped items
        for slot, item_data in data.get('equipped_items', {}).items():
            if item_data:
                item_type = item_data.get('type', 'Item')
                item_class = get_item_class(item_type)
                player.equipped_items[slot] = item_class.from_dict(item_data)
            else:
                player.equipped_items[slot] = None

        # current_room will be set by the World class after the player is loaded
        return player

