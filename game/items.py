# game/items.py

class Item:
    """
    Base class for all items in the game.
    """
    def __init__(self, item_id, name, description, value=0, item_type='Item'):
        self.item_id = item_id # Unique ID for the item, matches data file
        self.name = name
        self.description = description
        self.value = value # How much it's worth (e.g., for selling)
        self.item_type = item_type # Used for dynamic loading/saving

    def __str__(self):
        return f"{self.name} ({self.description})"

    def to_dict(self):
        """Converts the item to a dictionary for saving."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'value': self.value,
            'type': self.item_type # Store the type for reconstruction
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an Item object from a dictionary for loading."""
        return cls(
            data['item_id'],
            data['name'],
            data['description'],
            data.get('value', 0),
            data.get('type', 'Item')
        )

# --- Specific Item Types (Subclasses) ---

class Weapon(Item):
    """
    Represents a weapon that can be equipped by the player.
    """
    def __init__(self, item_id, name, description, value, damage, weapon_type='melee'):
        super().__init__(item_id, name, description, value, item_type='Weapon')
        self.damage = damage
        self.weapon_type = weapon_type # e.g., 'melee', 'ranged'

    def __str__(self):
        return f"{self.name} (Damage: {self.damage}, Type: {self.weapon_type}) - {self.description}"

    def to_dict(self):
        """Converts the weapon to a dictionary for saving."""
        data = super().to_dict()
        data.update({
            'damage': self.damage,
            'weapon_type': self.weapon_type
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a Weapon object from a dictionary for loading."""
        return cls(
            data['item_id'],
            data['name'],
            data['description'],
            data['value'],
            data['damage'],
            data.get('weapon_type', 'melee')
        )

class Armor(Item):
    """
    Represents a piece of armor that can be equipped by the player.
    """
    def __init__(self, item_id, name, description, value, defense, armor_slot='body'):
        super().__init__(item_id, name, description, value, item_type='Armor')
        self.defense = defense
        self.armor_slot = armor_slot # e.g., 'head', 'body', 'legs', 'hands', 'feet'

    def __str__(self):
        return f"{self.name} (Defense: {self.defense}, Slot: {self.armor_slot}) - {self.description}"

    def to_dict(self):
        """Converts the armor to a dictionary for saving."""
        data = super().to_dict()
        data.update({
            'defense': self.defense,
            'armor_slot': self.armor_slot
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates an Armor object from a dictionary for loading."""
        return cls(
            data['item_id'],
            data['name'],
            data['description'],
            data['value'],
            data['defense'],
            data.get('armor_slot', 'body')
        )

class Potion(Item):
    """
    Represents a consumable potion with a specific effect.
    """
    def __init__(self, item_id, name, description, value, effect_type, effect_strength):
        super().__init__(item_id, name, description, value, item_type='Potion')
        self.effect_type = effect_type # e.g., 'heal', 'strength_boost'
        self.effect_strength = effect_strength

    def use(self, target):
        """Applies the potion's effect to the target."""
        if self.effect_type == 'heal':
            target.heal(self.effect_strength)
            print(f"You use the {self.name} and restore {self.effect_strength} health.")
        elif self.effect_type == 'strength_boost':
            target.apply_buff('strength', self.effect_strength, duration=5) # Example with duration
            print(f"You use the {self.name} and feel a surge of strength (+{self.effect_strength} ATK for 5 turns).")
        # Add more effects as needed
        return True # Potion was successfully used

    def __str__(self):
        return f"{self.name} (Effect: {self.effect_type} {self.effect_strength}) - {self.description}"

    def to_dict(self):
        """Converts the potion to a dictionary for saving."""
        data = super().to_dict()
        data.update({
            'effect_type': self.effect_type,
            'effect_strength': self.effect_strength
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a Potion object from a dictionary for loading."""
        return cls(
            data['item_id'],
            data['name'],
            data['description'],
            data['value'],
            data['effect_type'],
            data['effect_strength']
        )

# --- Helper functions for dynamic instantiation ---

_item_classes = {
    'Item': Item,
    'Weapon': Weapon,
    'Armor': Armor,
    'Potion': Potion,
    # Add other item types here
}

def get_item_class(item_type):
    """Returns the Item class based on its type string."""
    return _item_classes.get(item_type, Item)

def get_item_classes_map():
    """Returns the dictionary of item classes for loading purposes."""
    return _item_classes
