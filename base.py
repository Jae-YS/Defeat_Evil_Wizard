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
        self.cached_attack_roll = (
            None  # Cache for attack roll to ensure consistency in multi-hit scenarios
        )
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
        base = self.attack_power
        if self.cached_attack_roll is None:
            self.cached_attack_roll = random.randint(base, base + 5)

        atk = self.cached_attack_roll

        if self.status_effects["empowered"][1] > 0:
            atk += self.status_effects["empowered"][0]
        if self.status_effects["weakened"][1] > 0:
            atk -= self.status_effects["weakened"][0]
        return max(1, atk)

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

    def try_evade(self, attacker_name=""):
        """
        Determines whether this character evades an incoming attack.

        Args:
            attacker_name (str): Optional name of the attacker for the log.

        Returns:
            bool: True if evaded, False if hit.
        """
        evade_chance = self.get_effective_evasion()
        if random.random() < evade_chance:
            print(
                f"{self.name} evaded the attack!"
                if not attacker_name
                else f"{self.name} evaded {attacker_name}'s attack!"
            )
            return True
        return False

    def attack(self, opponent):
        """
        Perform a normal attack. May miss if opponent evades.

        Args:
            opponent (Character): The target of the attack.
        """
        if opponent.try_evade(self.name):
            self.cached_attack_roll = None
            return

        damage = max(1, self.get_effective_attack() - opponent.get_effective_defense())
        opponent.health -= damage
        print(f"{self.name} attacks {opponent.name} for {damage} damage!")
        self.cached_attack_roll = None
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

        return False

    def special(self, index, target):
        """
        Call a special ability by menu index.

        Args:
            index (int): 1-based index from the player's ability menu.
            target (Character): The opponent or target of the ability.
        """
        abilities = list(self.abilities.keys())
        if not 0 <= index < len(abilities):
            print("Invalid ability choice.")
            return

        ability = abilities[index]
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
        Decrement status effect durations and cooldowns. Should be called at the END of the character's turn.
        """
        # Tick down status effects

        for k, v in self.status_effects.items():
            if isinstance(v, tuple):
                value, duration = v
                if duration > 0:
                    self.status_effects[k] = (value, duration - 1)
            elif isinstance(v, int):
                if v > 0:
                    self.status_effects[k] -= 1
                if self.status_effects[k] <= 0:
                    self.status_effects[k] = 0

        # Tick down cooldowns
        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] -= 1

    def display_stats(self):
        """
        Print current stats and active status effects,
        showing stat modifications for attack, defense, and evasion.
        """
        print(f"{self.name}'s Stats\n" + "-" * 40)

        # Use cached or generate new attack roll
        if self.cached_attack_roll is None:
            self.cached_attack_roll = random.randint(
                self.attack_power, self.attack_power + 5
            )
        rolled_attack = self.cached_attack_roll

        # Compute net attack modifier
        empowered = (
            self.status_effects["empowered"][0]
            if self.status_effects["empowered"][1] > 0
            else 0
        )
        weakened = (
            self.status_effects["weakened"][0]
            if self.status_effects["weakened"][1] > 0
            else 0
        )
        net_attack_mod = empowered - weakened

        # Defense
        effective_def = self.get_effective_defense()
        net_def_mod = effective_def - self.defense

        # Evasion
        effective_eva = self.get_effective_evasion()
        net_eva_mod = effective_eva - self.evasion_chance
        net_eva_percent = round(net_eva_mod * 100)

        # Display
        print(f"Health       : {self.health}/{self.max_health}")
        print(
            f"Attack Power : {rolled_attack} ({'+' if net_attack_mod >= 0 else ''}{net_attack_mod})"
        )
        print(
            f"Defense      : {effective_def} ({'+' if net_def_mod >= 0 else ''}{net_def_mod})"
        )
        print(
            f"Evasion      : {effective_eva * 100:.0f}% ({'+' if net_eva_percent >= 0 else ''}{net_eva_percent}%)"
        )

        # Status Effects
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
