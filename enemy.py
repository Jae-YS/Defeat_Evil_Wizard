from base import Character


class EvilWizard(Character):
    """
    A cunning magical enemy that uses dark powers to damage, debuff, and heal.
    Specializes in draining life and avoiding attacks via shadow magic.
    """

    def __init__(self, name):
        """
        Initialize the Evil Wizard with custom stats and abilities.

        Abilities:
            - dark_bolt: Moderate damage attack (+10 base).
            - drain_life: Damage enemy and heal self.
            - curse: Reduce enemy's attack.
            - shadow_veil: Temporarily boost evasion.
        """
        abilities = {
            "shadow_veil": {"cooldown": 5, "desc": "Evasion +50% for 2 turns"},
            "dark_bolt": {"cooldown": 3, "desc": "Deals magic damage"},
            "drain_life": {"cooldown": 3, "desc": "Steals life"},
            "curse": {"cooldown": 5, "desc": "Reduces target attack by 10"},
        }

        super().__init__(
            name,
            health=150,
            attack_power=15,
            defense=5,
            evasion_chance=0.25,
            abilities=abilities,
        )

    def update(self):
        super().update()
        self.regenerate()

    def dark_bolt(self, target):
        """
        Special: Fires a bolt of dark magic for base attack +10 damage.
        """
        if target.try_evade(self.name):
            return

        damage = self.attack_power + 10
        print(f"{self.name} casts Dark Bolt on {target.name} for {damage} damage.")
        target.health -= damage
        if target.health <= 0:
            print(f"{target.name} has been defeated!")

    def drain_life(self, target):
        """
        Special: Deals 15 damage to the opponent and heals self for half.
        """
        if target.try_evade(self.name):
            return

        damage = 20
        heal = damage // 2
        target.health -= damage
        self.health = min(self.max_health, self.health + heal)
        print(f"{self.name} drains {damage} HP from {target.name}, healing for {heal}.")
        if target.health <= 0:
            print(f"{target.name} has been defeated!")

    def curse(self, target):
        """
        Special: Reduces the target's attack power by 10 points for 3 turns.
        """
        if target.try_evade(self.name):
            return

        reduction = 10
        target.status_effects["weakened"] = (reduction, 4)
        print(
            f"{self.name} curses {target.name}, reducing their attack power by {reduction}."
        )

    def shadow_veil(self, target=None):
        """
        Special: Grants a 50% evasion boost for 2 turns.
        """

        boost = 0.5
        duration = 3
        self.status_effects["evade_boost"] = (boost, duration)
        print(
            f"{self.name} shrouds themselves in shadows, increasing evasion by {int(boost * 100)}% for {duration} turns."
        )

    def regenerate(self):
        """
        Passive: Heals 5 HP after every turn, up to max health.
        """
        if self.health <= 0:
            return  # Do not regenerate if already defeated

        heal = 5
        self.health = min(self.max_health, self.health + heal)
        print(f"{self.name} passively regenerates {heal} HP. Now at {self.health} HP.")
