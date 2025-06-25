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
            - regenerate: Recover a portion of health.
        """
        abilities = {
            "dark_bolt": 3,
            "drain_life": 4,
            "curse": 2,
            "shadow_veil": 5,
            "regenerate": 6,
        }

        super().__init__(
            name,
            health=150,
            attack_power=15,
            defense=10,
            evasion_chance=0.25,
            abilities=abilities,
        )

    def dark_bolt(self, target):
        """
        Special: Fires a bolt of dark magic for base attack +10 damage.
        """
        if self.use_ability("dark_bolt"):
            damage = self.attack_power + 10
            print(f"{self.name} casts Dark Bolt on {target.name} for {damage} damage.")
            target.health -= damage
            if target.health <= 0:
                print(f"{target.name} has been defeated!")

    def drain_life(self, target):
        """
        Special: Deals 20 damage to the opponent and heals self for half.
        """
        if self.use_ability("drain_life"):
            damage = 20
            heal = damage // 2
            target.health -= damage
            self.health = min(self.max_health, self.health + heal)
            print(
                f"{self.name} drains {damage} HP from {target.name}, healing for {heal}."
            )
            if target.health <= 0:
                print(f"{target.name} has been defeated!")

    def curse(self, target):
        """
        Special: Reduces the target's attack power by 5 points.
        """
        if self.use_ability("curse"):
            reduction = 5
            target.attack_power = max(0, target.attack_power - reduction)
            print(
                f"{self.name} curses {target.name}, reducing their attack power by {reduction}."
            )

    def shadow_veil(self, target=None):
        """
        Special: Grants a 50% evasion boost for 2 turns.
        """
        if self.use_ability("shadow_veil"):
            boost = 0.5
            duration = 2
            self.status_effects["evade_boost"] = (boost, duration)
            print(
                f"{self.name} shrouds themselves in shadows, increasing evasion by {int(boost * 100)}% for {duration} turns."
            )

    def regenerate(self, target=None):
        """
        Special: Heals 1/3 of max HP.
        """
        if self.use_ability("regenerate"):
            heal = self.max_health // 3
            self.health = min(self.max_health, self.health + heal)
            print(f"{self.name} regenerates {heal} health. Now at {self.health} HP.")
