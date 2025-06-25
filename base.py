import random


class Character:
    """
    Base class for all character types in the RPG.
    Manages core attributes like health, attack, defense, evasion, abilities, and status effects.
    """

    def __init__(self, name, health, attack_power, defense, evasion_chance, abilities):
        """
        Initialize a character with core stats and abilities.

        Args:
            name (str): Character's name.
            health (int): Starting and maximum health.
            attack_power (int): Base attack value.
            defense (int): Base defense value.
            evasion_chance (float): Base evasion chance (0.0 to 1.0).
            abilities (dict): Dictionary of ability names mapped to cooldown and description.
        """
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.defense = defense
        self.evasion_chance = evasion_chance
        self.max_health = health

        # Track ongoing effects with turn durations
        self.status_effects = {
            "stunned": 0,
            "weakened": (0, 0),
            "vulnerable": (0, 0),
            "slowed": (0, 0),
            "shielded": (0, 0),
            "empowered": (0, 0),
            "evade_boost": (0, 0),
        }

        self.abilities = abilities  # Special abilities with cooldowns and descriptions
        self.cooldowns = {
            name: 0 for name in abilities
        }  # Tracks cooldown turns remaining

    def get_effective_attack(self):
        """Return attack power after accounting for buffs/debuffs."""
        atk = self.attack_power
        if self.status_effects["empowered"][1] > 0:
            atk += self.status_effects["empowered"][0]
        if self.status_effects["weakened"][1] > 0:
            atk -= self.status_effects["weakened"][0]
        return max(0, atk)

    def get_effective_defense(self):
        """Return defense after buffs/debuffs like shield or vulnerability."""
        defn = self.defense
        if self.status_effects["shielded"][1] > 0:
            defn += self.status_effects["shielded"][0]
        if self.status_effects["vulnerable"][1] > 0:
            defn -= self.status_effects["vulnerable"][0]
        return max(0, defn)

    def get_effective_evasion(self):
        """Return evasion percentage after boosts or slows."""
        eva = self.evasion_chance
        if self.status_effects["evade_boost"][1] > 0:
            eva += self.status_effects["evade_boost"][0]
        if self.status_effects["slowed"][1] > 0:
            eva -= self.status_effects["slowed"][0]
        return max(0.0, min(1.0, eva))  # Clamp between 0% and 100%

    def attack(self, opponent):
        """
        Perform a normal attack. May miss if opponent evades.

        Args:
            opponent (Character): The target of the attack.
        """
        if random.random() < opponent.get_effective_evasion():
            print(f"{opponent.name} evaded the attack!")
            return

        damage = max(0, self.get_effective_attack() - opponent.get_effective_defense())
        opponent.health -= damage
        print(f"{self.name} attacks {opponent.name} for {damage} damage!")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")

    def is_ability_ready(self, ability):
        """
        Check if an ability is off cooldown.

        Args:
            ability (str): The name of the ability.

        Returns:
            bool: True if ready, False if still on cooldown.
        """
        return self.cooldowns.get(ability, 0) == 0

    def use_ability(self, ability_name):
        """
        Attempt to use an ability. Starts cooldown if ready.

        Args:
            ability_name (str): Ability to use.

        Returns:
            bool: Whether the ability was successfully used.
        """
        cd = self.abilities[ability_name]["cooldown"]
        if self.is_ability_ready(ability_name):
            self.cooldowns[ability_name] = cd
            return True

        print(
            f"{self.name}'s {ability_name.replace('_', ' ').title()} is on cooldown for {self.cooldowns[ability_name]} more turn(s)."
        )
        return False

    def special(self, index, target):
        """
        Call a special ability by menu index.

        Args:
            index (int): 1-based index from the player's ability menu.
            target (Character): The opponent or target of the ability.
        """
        abilities = list(self.abilities.keys())
        if not 1 <= index <= len(abilities):
            print("Invalid ability choice.")
            return

        ability = abilities[index - 1]
        if not self.use_ability(ability):
            return

        method = getattr(self, ability, None)
        if callable(method):
            method(target)
        else:
            print(f"{ability} is not implemented.")

    def heal(self):
        """
        Regain a fixed amount of HP (10), up to max health.
        """
        amount = 10
        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + amount)
            print(f"{self.name} heals for {amount} HP. Current health: {self.health}")
        else:
            print(f"{self.name} is already at full health!")

    def update(self):
        """
        Decrement status durations and cooldowns. Should be called each turn.
        """
        for k, v in self.status_effects.items():
            if isinstance(v, tuple):
                if v[1] > 0:
                    self.status_effects[k] = (v[0], v[1] - 1)
                elif v[1] == 0:
                    self.status_effects[k] = (0, 0)
            elif isinstance(v, int) and v > 0:
                self.status_effects[k] -= 1

        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] -= 1

    def display_stats(self):
        """
        Print current stats and active status effects.
        """
        print(f"{self.name}'s Stats\n" + "-" * 40)
        atk = self.get_effective_attack()
        defn = self.get_effective_defense()
        eva = self.get_effective_evasion()

        print(f"Health       : {self.health}/{self.max_health}")
        print(
            f"Attack Power : {atk} ({'+' if atk > self.attack_power else ''}{atk - self.attack_power})"
        )
        print(
            f"Defense      : {defn} ({'+' if defn > self.defense else ''}{defn - self.defense})"
        )
        print(f"Evasion      : {eva * 100:.0f}%")

        print("\nActive Status Effects:")
        has_status = False
        for k, v in self.status_effects.items():
            if isinstance(v, tuple) and v[1] > 0:
                print(f" - {k}: {v[0]} for {v[1]} more turn(s)")
                has_status = True
            elif isinstance(v, int) and v > 0:
                print(f" - {k}: {v} more turn(s)")
                has_status = True
        if not has_status:
            print(" - None")

    def view_special_abilities(self):
        """
        Print each special ability with its cooldown and description.
        """
        print(f"{self.name}'s Special Abilities:")
        for i, (name, info) in enumerate(self.abilities.items(), 1):
            cd = info["cooldown"]
            desc = info.get("desc", "No description.")
            remaining = self.cooldowns.get(name, 0)
            status = "Ready" if remaining == 0 else f"{remaining} turn(s) left"
            print(
                f" {i}. {name.replace('_', ' ').title()} — {desc} (CD: {cd}, {status})"
            )
