# game/enemies.py

class Enemy:
    """
    Base class for all enemies in the game.
    """
    def __init__(self, enemy_id, name, description, health, attack_power, defense, initiative_bonus, loot_xp, loot_items=None, enemy_type='Enemy'):
        self.enemy_id = enemy_id
        self.name = name
        self.description = description
        self.max_health = health
        self.health = health
        self.attack_power = attack_power
        self.defense = defense
        self.initiative_bonus = 0
        self.loot_xp = loot_xp # Experience points gained upon defeating this enemy
        self.loot_items = loot_items if loot_items is not None else [] # List of item_ids to drop
        self.enemy_type = enemy_type # Used for dynamic loading/saving
    
    def get_initiative_bonus(self):
        return self.initiative_bonus

    def is_alive(self):
        """Checks if the enemy is still alive."""
        return self.health > 0

    def take_damage(self, damage):
        """Reduces the enemy's health by the given damage amount."""
        actual_damage = max(0, damage - self.defense) # Apply defense
        self.health -= actual_damage
        if self.health < 0:
            self.health = 0
        print(f"The {self.name} takes {actual_damage} damage.")
        if not self.is_alive():
            print(f"The {self.name} has been defeated!")

    def attack(self, target):
        """Performs a basic attack on a target (e.g., the player)."""
        damage = self.attack_power # Simple damage for now
        target.take_damage(damage) # Player also has a take_damage method
        print(f"The {self.name} attacks you, dealing {damage} damage.")

    def to_dict(self):
        """Converts the enemy to a dictionary for saving."""
        return {
            'enemy_id': self.enemy_id,
            'name': self.name,
            'description': self.description,
            'max_health': self.health,
            'health': self.health,
            'attack_power': self.attack_power,
            'defense': self.defense,
            'initiative_bonus': self.initiative_bonus,
            'loot_xp': self.loot_xp,
            'loot_items': self.loot_items,
            'type': self.enemy_type # Store the type for reconstruction
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an Enemy object from a dictionary for loading."""
        return cls(
            data['enemy_id'],
            data['name'],
            data['description'],
            data['health'],
            data['attack_power'],
            data['defense'],
            data['loot_xp'],
            data['initiative_bonus'],
            data.get('loot_items', [])
        )

# --- Specific Enemy Types (Subclasses) ---

class Goblin(Enemy):
    """
    A weak, common goblin enemy.
    """
    def __init__(self, enemy_id, name="Goblin", description="A small, green-skinned creature with beady eyes.",
                 health=20, attack_power=5, defense=2, initiative_bonus=0, loot_xp=10, loot_items=None):
        super().__init__(enemy_id, name, description, health, attack_power, defense, initiative_bonus, loot_xp, loot_items, enemy_type='Goblin')

    def attack(self, target):
        """Goblin's specific attack (e.g., slightly increased chance of missing)."""
        import random
        if random.random() < 0.15: # 15% chance to miss
            print(f"The {self.name} lunges at you but misses!")
        else:
            super().attack(target)


class Orc(Enemy):
    """
    A stronger, more resilient orc enemy.
    """
    def __init__(self, enemy_id, name="Orc", description="A hulking brute with tusks and a crude weapon.",
                 health=50, attack_power=12, defense=5, initiative_bonus=0, loot_xp=25, loot_items=None):
        super().__init__(enemy_id, name, description, health, attack_power, defense, initiative_bonus, loot_xp, loot_items, enemy_type='Orc')

    def attack(self, target):
        """Orc's specific attack (e.g., chance for a critical hit)."""
        import random
        damage = self.attack_power
        if random.random() < 0.2: # 20% chance for critical hit
            damage *= 1.5
            print(f"The {self.name} unleashes a mighty blow!")
        super().attack(target)


# --- Helper Functions for dynamic instantiation ---

_enemy_classes = {
    'Enemy': Enemy,
    'Goblin': Goblin,
    'Orc': Orc,
    # Add other enemy types here
}

def get_enemy_class(enemy_type):
    """Returns the Enemy class based on its type string."""
    return _enemy_classes.get(enemy_type, Enemy)

def get_enemy_classes_map():
    """Returns the dictionary of enemy classes for loading purposes."""
    return _enemy_classes

