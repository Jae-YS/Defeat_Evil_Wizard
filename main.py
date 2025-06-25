from utils import create_character
from enemy import EvilWizard
from battle import battle


def main():
    player = create_character()
    wizard = EvilWizard("Dark Wizard")
    battle(player, wizard)


if __name__ == "__main__":
    main()
