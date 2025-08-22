import sys
import json

from game.player import Player
from game.world import World
from game.items import Item, Weapon, Armor, Potion
from game.combat import Combat
from game.story import Story
from data.loader import load_room_data, load_item_data, load_enemy_data

# Global game state (or you could encapsulate this in a Game class)
current_player = None
current_world = None
game_running = True


def display_welcome_message():
    """Displays the initial welcome message to the player."""
    print("Welcome to the **Text Based EverQuest**!")
    print("A text-based adventure where your choices shape your destiny.")
    print("---------------------------------------------------------")
    input("Press Enter to continue...")


def display_main_menu():
    """Displays the main menu options."""
    print("\n--- Main Menu ---")
    print("1. New Game")
    print("2. Load Game")
    print("3. Quit")
    print("-----------------")


def create_new_game():
    """Initializes a new game session."""
    global current_player, current_world

    player_name = input("Enter your hero's name: ")
    current_player = Player(player_name)

    # Load initial world data
    room_data = load_room_data()
    item_data = load_item_data()
    enemy_data = load_enemy_data()

    # Pass loaded data to the World and other components for initialization
    current_world = World(room_data, item_data, enemy_data)
    current_player.set_current_room(current_world.get_starting_room())

    print(f"\nWelcome, {current_player.name}, to the adventure!")
    current_player.current_room.display_room_description()


def load_game():
    """Loads a previously saved game."""
    global current_player, current_world

    print("\n--- Load Game ---")
    # In a real game, you would list save files and let the user choose
    try:
        with open("data/saved_games/save_01.json", "r") as f:
            saved_game_data = json.load(f)

        current_player = Player.from_dict(saved_game_data['player'])
        current_world = World.from_dict(saved_game_data['world'])
        current_player.set_current_room(current_world.get_room_by_id(saved_game_data['player']['current_room_id']))

        print("\nGame loaded successfully!")
        current_player.current_room.display_room_description()
    except FileNotFoundError:
        print("No saved game found. Please start a New Game.")
        current_player = None
        current_world = None
    except Exception as e:
        print(f"Error loading game: {e}")
        current_player = None
        current_world = None


def save_game():
    """Saves the current game state."""
    if current_player and current_world:
        game_state = {
            'player': current_player.to_dict(),
            'world': current_world.to_dict()
        }
        with open("data/saved_games/save_01.json", "w") as f:
            json.dump(game_state, f, indent=4)
        print("Game saved successfully!")
    else:
        print("No game in progress to save.")


def parse_command(command_input):
    """Parses player commands and triggers appropriate actions."""
    global game_running

    parts = command_input.lower().split()
    verb = parts[0] if parts else ""
    noun = " ".join(parts[1:]) if len(parts) > 1 else ""

    if verb in ["quit", "exit"]:
        confirm = input("Are you sure you want to quit? (yes/no): ").lower()
        if confirm == "yes":
            save_game()
            game_running = False
            print("Thanks for playing!")
        return

    if not current_player or not current_world:
        print("Please start a new game or load a game from the main menu.")
        return

    # Movement commands
    if verb in ["go", "move"]:
        if noun in ["north", "south", "east", "west"]:
            current_player.move(noun, current_world)
            current_player.current_room.display_room_description()
        else:
            print("Move where? (north, south, east, west)")
        return

    # Interaction commands
    if verb == "look":
        current_player.current_room.display_room_description()
        return
    if verb == "inventory":
        current_player.display_inventory()
        return
    if verb == "get":
        item = current_player.current_room.remove_item(noun)
        if item:
            current_player.add_item(item)
            print(f"You picked up the {item.name}.")
        else:
            print(f"There's no '{noun}' here to get.")
        return
    if verb == "use":
        # Example for using an item
        if noun == "potion":
            if current_player.use_item("potion"):
                print("You drink the potion and feel a surge of vitality!")
            else:
                print("You don't have a potion to use.")
        else:
            print(f"You can't use '{noun}' right now.")
        return
    if verb == "attack":
        # Trigger combat
        if current_player.current_room.enemies:
            enemy = current_player.current_room.enemies[0]  # Simple: attack the first enemy
            Combat.initiate_combat(current_player, enemy)
            # After combat, check if the player or enemy is defeated
            if current_player.health <= 0:
                print("You have been defeated! Game Over.")
                game_running = False
            elif enemy.health <= 0:
                print(f"You defeated the {enemy.name}!")
                current_player.current_room.enemies.remove(enemy)
        else:
            print("There are no enemies here to attack.")
        return
    if verb == "save":
        save_game()
        return

    # Story/Quest related commands (handled by the Story module)
    # This is a placeholder; actual implementation depends on your story system
    if verb == "talk" and noun:
        Story.handle_dialogue(current_player, noun)
        return
    if verb == "quest":
        Story.display_quests(current_player)
        return

    print("Invalid command. Try 'go north', 'look', 'inventory', 'get [item]', 'attack', 'talk [npc]', 'save', or 'quit'.")


def main_game_loop():
    """The main loop for the game."""
    global game_running

    while game_running:
        if current_player and current_world:
            command = input("\nWhat do you want to do? > ").strip()
            parse_command(command)
        else:
            # If no game is started or loaded, display the main menu
            display_main_menu()
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                create_new_game()
            elif choice == "2":
                load_game()
            elif choice == "3":
                game_running = False
                print("Exiting game. Goodbye!")
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    display_welcome_message()
    main_game_loop()

