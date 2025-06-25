from base import Character
import random


class Warrior(Character):
    """
    A tanky melee fighter with a passive Berserker Rage that activates at low health.
    """

    def __init__(self, name):
        abilities = {
            "shield_bash": {"cooldown": 3, "desc": "Stuns the enemy for 1 turn."}
        }

        super().__init__(
            name,
            health=140,
            attack_power=25,
            defense=15,
            evasion_chance=0.05,
            abilities=abilities,
        )

        self.raging = False  # Track rage state

    def update(self):
        """
        Called every turn to handle status updates and passive effects like rage.
        """
        super().update()
        self.berserker_rage()

    def shield_bash(self, opponent):
        """
        Special: Stuns the enemy for 1 turn. Has a 3-turn cooldown.
        """
        if opponent.try_evade(self.name):
            return

        opponent.status_effects["stunned"] = 1
        print(f"{self.name} uses Shield Bash on {opponent.name}, stunning them!")

    def berserker_rage(self):
        """
        Passive: If health is below 30%, gain +10 attack and +5 defense.
        Removed when health returns above 30%.
        Implemented via status_effects, not base stat changes.
        """
        health_ratio = self.health / self.max_health

        if not self.raging and health_ratio < 0.3:
            self.apply_status("empowered", 10, -1)  # permanent while below 30%
            self.apply_status("shielded", 5, -1)
            self.raging = True
            print(
                f"{self.name} enters Berserker Rage! "
                f"Attack Power: {self.get_effective_attack()}, Defense: {self.get_effective_defense()}"
            )
        elif self.raging and health_ratio >= 0.3:
            self.apply_status("empowered", 0, 0)
            self.apply_status("shielded", 0, 0)
            self.raging = False
            print(f"{self.name} calms down. Rage effect removed.")


class Mage(Character):
    """
    A glass-cannon spellcaster with powerful damage and random utility magic.
    """

    def __init__(self, name):
        abilities = {
            "arcane_surge": {"cooldown": 4, "desc": "Deals 50 damage to the enemy."},
            "random_spell": {
                "cooldown": 5,
                "desc": "Casts a random spell with various effects.",
            },
        }
        super().__init__(name, 120, 30, 3, 0.1, abilities)

    def arcane_surge(self, opponent):
        """
        Special: Deals 50 flat magic damage. Ignores defense.
        """
        if opponent.try_evade(self.name):
            return

        damage = 50
        opponent.health -= damage
        print(f"{self.name} casts Arcane Surge on {opponent.name} for {damage} damage!")

    def random_spell(self, opponent):
        """
        Special: Casts one of several random spells:
        - Teleport (evasion buff)
        - Ice Shard (damage + slow)
        - Boost Attack
        - Boost Defense
        """

        spells = ["Teleport", "Ice Shard", "Boost Attack", "Boost Defense"]
        spell = random.choice(spells)
        print(f"{self.name} casts {spell}!")

        if spell == "Teleport":
            self.apply_status("evade_boost", 1, 3)
            print(f"{self.name} teleports! +100% evasion for 2 turns.")
        elif spell == "Ice Shard":
            if opponent.try_evade(self.name):
                return
            damage = 20
            opponent.status_effects["slowed"] = (opponent.evasion_chance / 2, 4)
            opponent.health -= damage
            print(
                f"{self.name} hits {opponent.name} with Ice Shard for {damage} damage. Target is slowed for 3 turns."
            )
        elif spell == "Boost Attack":
            self.apply_status("empowered", 7, 2)
            print(f"{self.name}'s attack power is boosted by 7 for 1 turn!")
        elif spell == "Boost Defense":
            self.apply_status("shielded", 5, 2)
            print(f"{self.name}'s defense increases by 5 for 1 turn!")


class Archer(Character):
    """
    A high-damage ranged fighter with multi-hit and power-shot abilities.
    """

    def __init__(self, name):
        abilities = {
            "multi_shot": {
                "cooldown": 3,
                "desc": "Hits 3-5 times for a third damage each.",
            },
            "headshot": {"cooldown": 4, "desc": "Next attack deals double damage."},
        }
        super().__init__(name, 120, 35, 7, 0.15, abilities)

    def multi_shot(self, opponent):
        """
        Special: Hits 3-5 times at a third power each hit.
        Good against low-defense targets.
        """

        hits = random.randint(3, 5)
        damage_per_hit = self.attack_power // 3
        landed = 0
        total_damage = 0

        for _ in range(hits):
            if opponent.try_evade(self.name):
                continue
            opponent.health -= damage_per_hit
            total_damage += damage_per_hit
            landed += 1

        print(
            f"{self.name} uses Multi-Shot on {opponent.name}, "
            f"attempting {hits} hits, {landed} landed for a total of {total_damage} damage!"
        )

    def headshot(self, opponent=None):
        """
        Special: Buffs next attack to deal double damage.
        Uses 'empowered' status effect.
        """

        self.apply_status("empowered", self.attack_power, 2)
        print(
            f"{self.name} is lining up a Headshot! Next attack will deal double damage."
        )


class Assassin(Character):
    """
    A stealthy fighter with high evasion and abilities to bypass defenses.
    """

    def __init__(self, name):
        abilities = {
            "shadow_step": {
                "cooldown": 3,
                "desc": "Next attack hits with 1.5x power and bypasses evasion.",
            },
            "smoke_bomb": {
                "cooldown": 4,
                "desc": "Increases evasion to 75% for 2 turns.",
            },
        }
        super().__init__(name, 100, 40, 2, 0.25, abilities)

    def shadow_step(self, opponent):
        """
        Special: Empowers next attack (1.5x) and disables enemy evasion for 1 turn.
        """

        self.apply_status("empowered", self.attack_power * 0.5, 2)
        opponent.status_effects["evade_boost"] = (0, 2)  # Removes evasion
        print(
            f"{self.name} uses Shadow Step! Next attack is empowered and unavoidable."
        )

    def smoke_bomb(self, opponent=None):
        """
        Special: Greatly increases evasion for 2 turns.
        Useful defensively.
        """

        self.apply_status("evade_boost", 0.75, 3)
        print(f"{self.name} uses Smoke Bomb! Evasion increased to 75% for 2 turns.")
