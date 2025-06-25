from characters import Warrior, Mage, Archer, Assassin


def create_character():
    while True:
        print("Choose your character class:")
        print("1. Warrior\n2. Mage\n3. Archer\n4. Assassin\n5. Exit")
        try:
            choice = int(input("Enter number: ").strip())
            name = input("Enter your name: ")
        except TypeError:
            print("Invalid input. Please enter a number corresponding to your choice.")
            continue
        except KeyboardInterrupt:
            print("\nCharacter creation cancelled. Exiting game.")
            exit()
        else:
            if choice < 1 or choice > 5:
                print("Invalid choice. Defaulting to Warrior.")
                return Warrior(name)
            elif choice == 1:
                return Warrior(name)
            elif choice == 2:
                return Mage(name)
            elif choice == 3:
                return Archer(name)
            elif choice == 4:
                return Assassin(name)
            elif choice == 5:
                print("Exiting game. Goodbye!")
                exit()
            else:
                print("Invalid choice. Defaulting to Warrior.")
                return Warrior(name)
        finally:
            print("-" * 40)
