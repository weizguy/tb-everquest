# game/story.py

class Quest:
    """
    Represents a single quest in the game.
    """
    def __init__(self, quest_id, title, description, objectives, reward_xp, reward_items=None, status='not_started'):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives  # A dictionary: {objective_id: {'description': '...', 'completed': False}}
        self.reward_xp = reward_xp
        self.reward_items = reward_items if reward_items is not None else []
        self.status = status  # 'not_started', 'active', 'completed', 'failed'

    def update_objective(self, objective_id):
        """Marks an objective as completed."""
        if objective_id in self.objectives:
            self.objectives[objective_id]['completed'] = True
            print(f"Objective '{self.objectives[objective_id]['description']}' completed!")
            return True
        return False

    def is_completed(self):
        """Checks if all objectives of the quest are completed."""
        return all(obj['completed'] for obj in self.objectives.values())

    def display_quest_status(self):
        """Prints the quest's title, description, and objective status."""
        print(f"\n--- Quest: {self.title} ({self.status.capitalize()}) ---")
        print(self.description)
        print("Objectives:")
        for obj_id, obj_data in self.objectives.items():
            status_marker = "[X]" if obj_data['completed'] else "[ ]"
            print(f"  {status_marker} {obj_data['description']}")
        print("-----------------------------------")

    def to_dict(self):
        """Converts the quest to a dictionary for saving."""
        return {
            'quest_id': self.quest_id,
            'title': self.title,
            'description': self.description,
            'objectives': self.objectives,
            'reward_xp': self.reward_xp,
            'reward_items': self.reward_items,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Quest object from a dictionary for loading."""
        return cls(
            data['quest_id'],
            data['title'],
            data['description'],
            data['objectives'],
            data['reward_xp'],
            data.get('reward_items', []),
            data.get('status', 'not_started')
        )

class Story:
    """
    Manages the game's narrative, quests, dialogue, and events.
    This class orchestrates story progression based on player actions and game state.
    """
    def __init__(self, quest_data, dialogue_data):
        self.quests = {}  # Stores active/available Quest objects, keyed by quest_id
        self.completed_quests = {} # Stores completed quests
        self.quest_data = quest_data # Raw data loaded from data/quests.json
        self.dialogue_data = dialogue_data # Raw data loaded from data/dialogue.json

        # Player's current progress in the main storyline (e.g., chapter, flag)
        self.story_progress_flags = {} # {flag_name: True/False or integer value}

        self._load_initial_quests()

    def _load_initial_quests(self):
        """Loads quests that are available from the start or specific story flags."""
        # For simplicity, load all quests here initially
        # In a real game, you'd load quests based on story flags
        for quest_id, data in self.quest_data.items():
            if data.get('initial_quest', False): # A flag in your quest data
                 self.quests[quest_id] = Quest.from_dict({'quest_id': quest_id, **data})
                 self.quests[quest_id].status = 'active' # Mark as active if it's an initial quest
                 print(f"New quest available: {self.quests[quest_id].title}")

    def start_quest(self, player, quest_id):
        """Adds a quest to the player's active quests."""
        if quest_id in self.quest_data and quest_id not in self.quests:
            quest_details = self.quest_data[quest_id]
            new_quest = Quest.from_dict({'quest_id': quest_id, **quest_details})
            new_quest.status = 'active'
            self.quests[quest_id] = new_quest
            print(f"Quest Started: {new_quest.title}")
            return True
        return False

    def complete_objective(self, player, quest_id, objective_id):
        """Marks a quest objective as completed."""
        if quest_id in self.quests and self.quests[quest_id].status == 'active':
            if self.quests[quest_id].update_objective(objective_id):
                if self.quests[quest_id].is_completed():
                    self._complete_quest(player, quest_id)
                    return True
            return True # Objective updated but quest not necessarily complete
        return False

    def _complete_quest(self, player, quest_id):
        """Handles the completion of a quest, awarding rewards."""
        quest = self.quests[quest_id]
        quest.status = 'completed'
        print(f"Quest Completed: {quest.title}!")
        player.gain_experience(quest.reward_xp)
        print(f"You gained {quest.reward_xp} experience points!")
        # Add reward items to player inventory or current room
        # You'd need a reference to the item data map to create these items
        # For simplicity, we'll just print them here
        if quest.reward_items:
            print(f"You received: {', '.join(quest.reward_items)}.")
            # In a real game, you would add these items to the player's inventory
            # player.add_item(create_item_from_id(item_id, self._item_data_map))
        self.completed_quests[quest_id] = quest
        del self.quests[quest_id] # Remove from active quests

    def display_quests(self, player):
        """Displays the player's active and completed quests."""
        print("\n--- Your Quests ---")
        if not self.quests and not self.completed_quests:
            print("No active or completed quests.")
            return

        print("\nActive Quests:")
        if self.quests:
            for quest_id, quest in self.quests.items():
                quest.display_quest_status()
        else:
            print("  None")

        print("\nCompleted Quests:")
        if self.completed_quests:
            for quest_id, quest in self.completed_quests.items():
                quest.display_quest_status()
        else:
            print("  None")
        print("-------------------")

    def handle_dialogue(self, player, npc_id):
        """
        Manages dialogue with an NPC.
        Dialogue can be conditional based on story flags, quests, or player attributes.
        """
        if npc_id in self.dialogue_data:
            npc_dialogue = self.dialogue_data[npc_id]

            # Determine which dialogue branch to use
            # This is where your narrative logic lives
            current_dialogue_branch = None
            for branch_id, branch_data in npc_dialogue.items():
                conditions_met = True
                if 'requires_flag' in branch_data:
                    if not self.story_progress_flags.get(branch_data['requires_flag'], False):
                        conditions_met = False
                if 'requires_quest_active' in branch_data:
                    if branch_data['requires_quest_active'] not in self.quests:
                        conditions_met = False
                # Add more conditions (e.g., player has item, player strength > X)

                if conditions_met:
                    current_dialogue_branch = branch_data
                    break # Take the first branch whose conditions are met

            if current_dialogue_branch:
                print(f"\n--- Talking to {npc_id.capitalize()} ---")
                for line_data in current_dialogue_branch['lines']:
                    if 'speaker' in line_data:
                        print(f"<{line_data['speaker']}>: {line_data['text']}")
                    else:
                        print(line_data['text']) # Default speaker

                    if 'choices' in line_data:
                        self._handle_dialogue_choices(player, line_data['choices'])
                        break # After choices, dialogue might end or jump

                    if 'triggers_quest' in line_data:
                        self.start_quest(player, line_data['triggers_quest'])

                    if 'sets_flag' in line_data:
                        self.story_progress_flags[line_data['sets_flag']] = True
                        print(f"[Story flag '{line_data['sets_flag']}' set.]")

                    if 'updates_objective' in line_data:
                        quest_id, objective_id = line_data['updates_objective']
                        self.complete_objective(player, quest_id, objective_id)

                print("------------------------------")
            else:
                print(f"{npc_id.capitalize()} has nothing new to say right now.")
        else:
            print(f"There's no one named '{npc_id.capitalize()}' to talk to here.")

    def _handle_dialogue_choices(self, player, choices_data):
        """Presents dialogue choices to the player and handles their selection."""
        print("\nWhat will you say?")
        for i, choice in enumerate(choices_data, 1):
            print(f"{i}. {choice['text']}")

        while True:
            try:
                choice_index = int(input("> Choose a number: ")) - 1
                if 0 <= choice_index < len(choices_data):
                    selected_choice = choices_data[choice_index]
                    print(f"\nYour response: '{selected_choice['text']}'")

                    if 'response' in selected_choice:
                        print(f"<{selected_choice.get('speaker', 'NPC')}>: {selected_choice['response']}")

                    if 'triggers_quest' in selected_choice:
                        self.start_quest(player, selected_choice['triggers_quest'])

                    if 'updates_objective' in selected_choice:
                        quest_id, objective_id = selected_choice['updates_objective']
                        self.complete_objective(player, quest_id, objective_id)

                    if 'sets_flag' in selected_choice:
                        self.story_progress_flags[selected_choice['sets_flag']] = True
                        print(f"[Story flag '{selected_choice['sets_flag']}' set.]")

                    # Handle consequences, e.g., reputation change, item received
                    # This could lead to another dialogue branch or end the conversation
                    break
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def check_for_events(self, player):
        """
        A general method to check for and trigger story events
        based on location, player progress, items, etc.
        This would be called regularly in the game loop.
        """
        # Example: Trigger an event when a player enters a specific room and has a specific item
        if player.current_room.room_id == "old_library" and 'ancient_map' in player.inventory:
            if not self.story_progress_flags.get('found_library_secret', False):
                print("\nYou notice a hidden compartment in the library shelf, illuminated by the ancient map!")
                self.story_progress_flags['found_library_secret'] = True
                self.start_quest(player, 'find_ancient_relic') # Example: start a new quest
                # Add item, trigger combat, etc.
                # player.add_item(create_item_from_id('library_key'))
                # player.current_room.enemies.append(create_enemy_from_id('spectral_guardian'))


    def to_dict(self):
        """Converts the story manager to a dictionary for saving."""
        return {
            'quests': {q_id: q.to_dict() for q_id, q in self.quests.items()},
            'completed_quests': {q_id: q.to_dict() for q_id, q in self.completed_quests.items()},
            'story_progress_flags': self.story_progress_flags
        }

    @classmethod
    def from_dict(cls, data, quest_data_ref, dialogue_data_ref):
        """Creates a Story object from a dictionary for loading."""
        story_instance = cls(quest_data_ref, dialogue_data_ref) # Pass references to original data
        story_instance.quests = {q_id: Quest.from_dict(q_data) for q_id, q_data in data['quests'].items()}
        story_instance.completed_quests = {q_id: Quest.from_dict(q_data) for q_id, q_data in data['completed_quests'].items()}
        story_instance.story_progress_flags = data['story_progress_flags']
        return story_instance

