import random


class Character:
    """
    Base class for all character types in the RPG.
    Manages core attributes like health, attack, defense, evasion, abilities, and status effects.
    Supports buffs, debuffs, cooldowns, and turn-based updates.
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
            abilities (dict): Ability names mapped to cooldowns and descriptions.
        """
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.cached_attack_roll = None
        self.defense = defense
        self.evasion_chance = evasion_chance
        self.max_health = health

        self.status_effects = {
            "stunned": 0,
            "weakened": (0, 0),
            "vulnerable": (0, 0),
            "slowed": (0, 0),
            "shielded": (0, 0),
            "empowered": (0, 0),
            "evade_boost": (0, 0),
        }

        self.abilities = abilities
        self.cooldowns = {name: 0 for name in abilities}

    def has_status(self, status_name):
        """Return True if a status is currently active (duration > 0)."""
        effect = self.status_effects.get(status_name)
        return effect > 0 if isinstance(effect, int) else effect[1] > 0

    def apply_status(self, name, value, duration):
        """Apply a status effect with a value and duration."""
        self.status_effects[name] = (value, duration)

    def try_evade(self, attacker_name=""):
        """Returns True if the character evades the incoming attack."""
        if random.random() < self.get_effective_evasion():
            attacker_str = f"{attacker_name}'s " if attacker_name else ""
            print(f"{self.name} evaded {attacker_str}attack!")
            return True
        return False

    def get_effective_attack(self):
        """Return current attack power including random roll and status effects."""
        base = self.attack_power
        if self.cached_attack_roll is None:
            self.cached_attack_roll = random.randint(base, base + 5)

        atk = self.cached_attack_roll
        if self.has_status("empowered"):
            atk += self.status_effects["empowered"][0]
        if self.has_status("weakened"):
            atk -= self.status_effects["weakened"][0]
        return max(1, atk)

    def get_effective_defense(self):
        """Return current defense stat after buffs/debuffs."""
        defn = self.defense
        if self.has_status("shielded"):
            defn += self.status_effects["shielded"][0]
        if self.has_status("vulnerable"):
            defn -= self.status_effects["vulnerable"][0]
        return max(0, defn)

    def get_effective_evasion(self):
        """Return current evasion rate after buffs/debuffs."""
        eva = self.evasion_chance
        if self.has_status("evade_boost"):
            eva += self.status_effects["evade_boost"][0]
        if self.has_status("slowed"):
            eva -= self.status_effects["slowed"][0]
        return max(0.0, min(1.0, eva))

    def attack(self, opponent):
        """
        Perform an attack against the opponent.
        Takes evasion and attack/defense modifiers into account.
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
        """Return True if the specified ability is off cooldown."""
        return self.cooldowns.get(ability, 0) == 0

    def use_ability(self, ability_name):
        """
        Trigger an ability if it is ready, and start its cooldown.

        Args:
            ability_name (str): The name of the ability to use.

        Returns:
            bool: Whether the ability was successfully activated.
        """
        cd = self.abilities[ability_name]["cooldown"]
        if self.is_ability_ready(ability_name):
            self.cooldowns[ability_name] = cd
            return True
        return False

    def special(self, index, target):
        """
        Execute the special ability by index from the ability list.

        Args:
            index (int): Index of the ability (0-based).
            target (Character): The target to use the ability on.
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
        """Restore 10 HP, not exceeding maximum health."""
        amount = 10
        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + amount)
            print(f"{self.name} heals for {amount} HP. Current health: {self.health}")
        else:
            print(f"{self.name} is already at full health!")

    def update(self):
        """
        Update status effect durations and cooldowns.
        Call this at the end of the character's turn.
        """
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

        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] -= 1

    def display_stats(self):
        """Print the character's current stats and active status effects."""
        print(f"{self.name}'s Stats\n" + "-" * 40)

        if self.cached_attack_roll is None:
            self.cached_attack_roll = random.randint(
                self.attack_power, self.attack_power + 5
            )
        rolled_attack = self.cached_attack_roll

        empowered = (
            self.status_effects["empowered"][0] if self.has_status("empowered") else 0
        )
        weakened = (
            self.status_effects["weakened"][0] if self.has_status("weakened") else 0
        )
        net_attack_mod = empowered - weakened

        effective_def = self.get_effective_defense()
        net_def_mod = effective_def - self.defense

        effective_eva = self.get_effective_evasion()
        net_eva_mod = round((effective_eva - self.evasion_chance) * 100)

        print(f"Health       : {self.health}/{self.max_health}")
        print(
            f"Attack Power : {rolled_attack} ({'+' if net_attack_mod >= 0 else ''}{net_attack_mod})"
        )
        print(
            f"Defense      : {effective_def} ({'+' if net_def_mod >= 0 else ''}{net_def_mod})"
        )
        print(
            f"Evasion      : {effective_eva * 100:.0f}% ({'+' if net_eva_mod >= 0 else ''}{net_eva_mod}%)"
        )

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
        """Print a summary of available special abilities and their cooldowns."""
        print(f"{self.name}'s Special Abilities:")
        for i, (name, info) in enumerate(self.abilities.items(), 1):
            cd = info["cooldown"]
            desc = info.get("desc", "No description.")
            remaining = self.cooldowns.get(name, 0)
            status = "Ready" if remaining == 0 else f"{remaining} turn(s) left"
            print(
                f" {i}. {name.replace('_', ' ').title()} — {desc} (CD: {cd}, {status})"
            )
