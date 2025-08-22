# game/world.py

from .items import Item  # Import the base Item class to associate items with rooms
from .enemies import Enemy # Import the base Enemy class to associate enemies with rooms

class Room:
    """
    Represents a single location in the game world.
    """
    def __init__(self, room_id, name, description, exits, items=None, enemies=None):
        self.room_id = room_id
        self.name = name
        self.description = description
        self.exits = exits  # A dictionary mapping directions (e.g., "north") to room_ids
        self.items = items if items is not None else []  # List of Item objects in the room
        self.enemies = enemies if enemies is not None else [] # List of Enemy objects in the room

    def display_room_description(self):
        """Prints the room's name, description, exits, items, and enemies."""
        print(f"\n--- {self.name} ---")
        print(self.description)
        print("\nExits:", ", ".join(self.exits.keys()))

        if self.items:
            print("You see:", ", ".join([item.name for item in self.items]))
        if self.enemies:
            print("You encounter:", ", ".join([enemy.name for enemy in self.enemies]))

    def add_item(self, item):
        """Adds an item to the room."""
        self.items.append(item)

    def remove_item(self, item_name):
        """
        Removes an item from the room by name and returns it.
        Returns None if the item is not found.
        """
        for i, item in enumerate(self.items):
            if item.name.lower() == item_name.lower():
                return self.items.pop(i)
        return None

    def to_dict(self):
        """Converts the room to a dictionary for saving."""
        return {
            'room_id': self.room_id,
            'name': self.name,
            'description': self.description,
            'exits': self.exits,
            'items': [item.to_dict() for item in self.items],
            'enemies': [enemy.to_dict() for enemy in self.enemies]
        }

    @classmethod
    def from_dict(cls, data, item_classes, enemy_classes):
        """Creates a Room object from a dictionary for loading."""
        # Need to dynamically create item and enemy objects based on their type
        items = []
        for item_data in data.get('items', []):
            item_type = item_data.get('type')
            if item_type and item_type in item_classes:
                items.append(item_classes[item_type].from_dict(item_data))
            else:
                print(f"Warning: Unknown item type '{item_type}' encountered during loading.")

        enemies = []
        for enemy_data in data.get('enemies', []):
            enemy_type = enemy_data.get('type')
            if enemy_type and enemy_type in enemy_classes:
                enemies.append(enemy_classes[enemy_type].from_dict(enemy_data))
            else:
                print(f"Warning: Unknown enemy type '{enemy_type}' encountered during loading.")
        
        return cls(
            data['room_id'],
            data['name'],
            data['description'],
            data['exits'],
            items=items,
            enemies=enemies
        )


class World:
    """
    Manages all the rooms in the game world and provides methods for navigation.
    """
    def __init__(self, room_data, item_data_map, enemy_data_map):
        self.rooms = {}  # Dictionary to store Room objects, keyed by room_id
        self.start_room_id = None
        self._item_data_map = item_data_map # Storing the original item data map
        self._enemy_data_map = enemy_data_map # Storing the original enemy data map

        # Load rooms from provided data
        self._load_rooms(room_data)

    def _load_rooms(self, room_data):
        """
        Loads room data, initializes Room objects, and sets up the world map.
        The room_data is expected to be a dictionary where keys are room_ids and values are room details.
        """
        for room_id, details in room_data.items():
            exits = details.get('exits', {})
            items_in_room = []
            for item_id in details.get('items', []):
                item_details = self._item_data_map.get(item_id)
                if item_details:
                    # Dynamically create item instances based on loaded data
                    from .items import get_item_class
                    item_class = get_item_class(item_details.get('type', 'Item'))
                    items_in_room.append(item_class.from_dict({'id': item_id, **item_details}))
                else:
                    print(f"Warning: Item ID '{item_id}' not found in item_data_map.")

            enemies_in_room = []
            for enemy_id in details.get('enemies', []):
                enemy_details = self._enemy_data_map.get(enemy_id)
                if enemy_details:
                    # Dynamically create enemy instances based on loaded data
                    from .enemies import get_enemy_class
                    enemy_class = get_enemy_class(enemy_details.get('type', 'Enemy'))
                    print(f"Creating enemy with: {{'enemy_id': {enemy_id}, **{enemy_details}}}")
                    enemies_in_room.append(enemy_class.from_dict({'enemy_id': enemy_id, **enemy_details}))
                else:
                    print(f"Warning: Enemy ID '{enemy_id}' not found in enemy_data_map.")

            room = Room(
                room_id=room_id,
                name=details['name'],
                description=details['description'],
                exits=exits,
                items=items_in_room,
                enemies=enemies_in_room
            )
            self.rooms[room_id] = room

            if details.get('is_starting_room', False):
                self.start_room_id = room_id

    def get_room_by_id(self, room_id):
        """Returns a Room object by its ID, or None if not found."""
        return self.rooms.get(room_id)

    def get_starting_room(self):
        """Returns the starting Room object."""
        if self.start_room_id:
            return self.rooms.get(self.start_room_id)
        return None

    def to_dict(self):
        """Converts the world to a dictionary for saving."""
        return {
            'rooms': {room_id: room.to_dict() for room_id, room in self.rooms.items()},
            'start_room_id': self.start_room_id
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a World object from a dictionary for loading."""
        # For loading, you'd need the item_classes and enemy_classes to reconstruct objects
        # This assumes you have functions/dictionaries in your item.py and enemy.py
        # to map item/enemy types to their classes.
        from .items import get_item_classes_map
        from .enemies import get_enemy_classes_map

        item_classes = get_item_classes_map()
        enemy_classes = get_enemy_classes_map()

        world_instance = cls(room_data={}, item_data_map={}, enemy_data_map={}) # Initialize an empty world
        world_instance.start_room_id = data.get('start_room_id')

        for room_id, room_data in data['rooms'].items():
            world_instance.rooms[room_id] = Room.from_dict(room_data, item_classes, enemy_classes)

        return world_instance

