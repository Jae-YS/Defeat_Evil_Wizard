import random


def battle(player, enemy):
    """
    Main game loop handling turn-by-turn combat between player and enemy.
    Ends when one character's health drops to zero or the player quits.
    """
    while player.health > 0 and enemy.health > 0:
        print_turn_header(player, enemy)

        try:
            if player.status_effects.get("stunned", 0) > 0:
                print(f"{player.name} is stunned and cannot act this turn!")
            else:
                if not handle_player_turn(player, enemy):
                    return
            player.update()
        except Exception as e:
            print(f"Something went wrong during your turn: {e}")

        print("-" * 40)

        try:
            if enemy.health > 0:
                if enemy.status_effects.get("stunned", 0) > 0:
                    print(f"{enemy.name} is stunned and cannot act this turn!")
                else:
                    handle_enemy_turn(enemy, player)
                enemy.update()
        except Exception as e:
            print(f"Something went wrong during the enemy's turn: {e}")

        print("-" * 40)

    if player.health <= 0:
        print(f"{player.name} has been defeated!")
    elif enemy.health <= 0:
        print(f"{enemy.name} has been defeated!")


def print_turn_header(player, enemy):
    """
    Print a visual header at the beginning of each turn with current HP.
    """
    print("\n--- New Turn ---")
    print(f"{player.name}: {player.health} HP")
    print(f"{enemy.name}: {enemy.health} HP\n")


def get_player_action(player, enemy):
    """
    Display the action menu and return the player's chosen action.

    Returns:
        str: The selected action keyword.
    """
    menu = [
        ("View stats", "view_stats"),
        ("View enemy stats", "view_enemy_stats"),
        ("View special abilities", "view_special_abilities"),
        ("Attack", "attack"),
        ("Special", "special"),
        ("Heal", "heal"),
        ("Quit", "quit"),
    ]

    while True:
        print("\nChoose your action:")
        for i, (label, _) in enumerate(menu, start=1):
            print(f" {i}. {label}")

        choice = input("> ").strip()

        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(menu):
                action = menu[index - 1][1]

                # Handle preview-only options immediately
                if action == "view_stats":
                    player.display_stats()
                elif action == "view_enemy_stats":
                    enemy.display_stats()
                elif action == "view_special_abilities":
                    player.view_special_abilities()
                else:
                    return action
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
        else:
            print("Invalid input. Please enter a number.")


def handle_player_turn(player, enemy):
    """
    Handles the player's entire turn based on input.

    Returns:
        bool: True to continue, False to quit battle.
    """
    while True:
        action = get_player_action(player, enemy)

        if action == "attack":
            player.attack(enemy)
            return True

        elif action == "special":
            while True:
                player.view_special_abilities()
                ability_choice = input(
                    "Choose a special ability by number (or 'back' to cancel): "
                ).strip()

                if ability_choice.lower() == "back":
                    break  # Return to main action menu

                if not ability_choice.isdigit():
                    print("Invalid input. Please enter a number.")
                    continue

                ability_index = int(ability_choice) - 1
                if 0 <= ability_index < len(player.abilities):
                    ability_name = list(player.abilities.keys())[ability_index]
                    if player.is_ability_ready(ability_name):
                        player.special(ability_index, enemy)
                        return True
                    else:
                        print(
                            f"{ability_name.replace('_', ' ').title()} is on cooldown. Try another."
                        )
                else:
                    print("Invalid ability choice.")

        elif action == "heal":
            player.heal()
            return True

        elif action == "quit":
            print("You fled the battle!")
            return False


def handle_enemy_turn(enemy, player):
    """
    Handles enemy AI logic for deciding whether to use a special or regular attack.
    Prioritizes specials 60% of the time if any are ready.
    """
    if enemy.status_effects.get("stunned", 0) > 0:
        print(f"{enemy.name} is stunned and cannot act this turn!")
        return

    # Get indices of all abilities that are currently ready
    ready_specials = [
        i for i, name in enumerate(enemy.abilities) if enemy.is_ability_ready(name)
    ]

    # 60% chance to use a special ability if at least one is ready
    if ready_specials and random.random() < 0.6:
        chosen_index = random.choice(ready_specials)
        enemy.special(chosen_index, player)
    else:
        enemy.attack(player)
