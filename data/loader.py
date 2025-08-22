# data/loader.py

import json
import os

# Define the paths to your data files
ROOM_DATA_FILE = os.path.join('data', 'rooms', 'rooms.json')
ITEM_DATA_FILE = os.path.join('data', 'items', 'items.json')
ENEMY_DATA_FILE = os.path.join('data', 'enemies', 'enemies.json')
STORY_DATA_FILE = os.path.join('data', 'story', 'story.json')

def _load_json_file(filepath):
    """
    Helper function to load data from a JSON file.
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return {}

def load_room_data():
    """
    Loads all room data from the rooms.json file.
    Returns a dictionary of room data keyed by room_id.
    """
    print(f"Loading room data from {ROOM_DATA_FILE}...")
    return _load_json_file(ROOM_DATA_FILE)

def load_item_data():
    """
    Loads all item data from the items.json file.
    Returns a dictionary of item data keyed by item_id.
    """
    print(f"Loading item data from {ITEM_DATA_FILE}...")
    return _load_json_file(ITEM_DATA_FILE)

def load_enemy_data():
    """
    Loads all enemy data from the enemies.json file.
    Returns a dictionary of enemy data keyed by enemy_id.
    """
    print(f"Loading enemy data from {ENEMY_DATA_FILE}...")
    return _load_json_file(ENEMY_DATA_FILE)

def load_story_data():
    """
    Loads all story and quest data from the story.json file.
    Returns a dictionary of story data.
    """
    print(f"Loading story data from {STORY_DATA_FILE}...")
    return _load_json_file(STORY_DATA_FILE)

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create dummy data files if they don't exist for testing
    os.makedirs(os.path.join('data', 'rooms'), exist_ok=True)
    os.makedirs(os.path.join('data', 'items'), exist_ok=True)
    os.makedirs(os.path.join('data', 'enemies'), exist_ok=True)
    os.makedirs(os.path.join('data', 'story'), exist_ok=True)

    with open(ROOM_DATA_FILE, 'w') as f:
        json.dump({
            "starting_room": {
                "name": "Old Cabin",
                "description": "A dusty old cabin with a flickering fireplace.",
                "exits": {"north": "forest_path"},
                "items": ["old_key"],
                "enemies": []
            },
            "forest_path": {
                "name": "Forest Path",
                "description": "A winding path through a dense forest.",
                "exits": {"south": "starting_room", "east": "goblin_cave"},
                "items": [],
                "enemies": ["forest_goblin"]
            }
        }, f, indent=4)

    with open(ITEM_DATA_FILE, 'w') as f:
        json.dump({
            "old_key": {
                "name": "Old Key",
                "description": "A rusty key that might unlock something.",
                "value": 5,
                "type": "Item"
            },
            "healing_potion": {
                "name": "Healing Potion",
                "description": "Restores a small amount of health.",
                "value": 10,
                "type": "Potion",
                "effect_type": "heal",
                "effect_strength": 20
            }
        }, f, indent=4)

    with open(ENEMY_DATA_FILE, 'w') as f:
        json.dump({
            "forest_goblin": {
                "name": "Forest Goblin",
                "description": "A sneaky little goblin of the forest.",
                "health": 20,
                "attack_power": 5,
                "defense": 2,
                "loot_xp": 10,
                "loot_items": ["healing_potion"],
                "type": "Goblin"
            }
        }, f, indent=4)

    with open(STORY_DATA_FILE, 'w') as f:
        json.dump({
            "quests": {
                "find_treasure": {
                    "name": "Find the Hidden Treasure",
                    "description": "A local legend speaks of a treasure buried deep within the forest.",
                    "status": "not_started",
                    "objectives": ["find_map", "decode_map", "reach_location", "dig_treasure"],
                    "rewards": {"xp": 50, "items": ["golden_idol"]}
                }
            },
            "dialogue": {
                "villager_intro": ["Hello adventurer!", "The forest is dangerous, be careful."],
                "goblin_encounter": ["Grrr... me smash!", "You intruder!"]
            }
        }, f, indent=4)

    print("\n--- Testing Loader Functions ---")
    rooms = load_room_data()
    print(f"Loaded Rooms: {len(rooms)}")
    if 'starting_room' in rooms:
        print(f"Starting Room Name: {rooms['starting_room']['name']}")

    items = load_item_data()
    print(f"Loaded Items: {len(items)}")
    if 'old_key' in items:
        print(f"Old Key Description: {items['old_key']['description']}")

    enemies = load_enemy_data()
    print(f"Loaded Enemies: {len(enemies)}")
    if 'forest_goblin' in enemies:
        print(f"Forest Goblin Health: {enemies['forest_goblin']['health']}")

    story = load_story_data()
    print(f"Loaded Quests: {len(story.get('quests', {}))}")
    if 'find_treasure' in story.get('quests', {}):
        print(f"Find Treasure Description: {story['quests']['find_treasure']['description']}")
