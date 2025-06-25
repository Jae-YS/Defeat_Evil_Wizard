import unittest
from base import Character
from enemy import EvilWizard


# Dummy player for testing
class DummyPlayer(Character):
    def __init__(self):
        super().__init__("Dummy", 100, 20, 5, 0.0, {})  # no abilities

    def view_special_abilities(self):
        pass


class EvilWizardTestCase(unittest.TestCase):
    def setUp(self):
        self.enemy = EvilWizard("Dark Wizard")
        self.player = DummyPlayer()

    def test_dark_bolt_damage(self):
        self.enemy.cooldowns["dark_bolt"] = 0
        initial_health = self.player.health
        self.enemy.dark_bolt(self.player)
        self.assertLess(self.player.health, initial_health)

    def test_drain_life_damage_and_heal(self):
        self.enemy.cooldowns["drain_life"] = 0
        self.enemy.health = 100  # set to less than max
        self.player.health = 100
        self.enemy.drain_life(self.player)
        self.assertEqual(self.enemy.health, 110)  # healed for 10
        self.assertEqual(self.player.health, 80)  # took 20 damage

    def test_curse_reduces_attack(self):
        self.enemy.cooldowns["curse"] = 0
        self.player.attack_power = 20
        self.enemy.curse(self.player)
        self.assertEqual(self.player.attack_power, 15)

    def test_shadow_veil_sets_evasion_boost(self):
        self.enemy.cooldowns["shadow_veil"] = 0
        self.enemy.shadow_veil()
        boost = self.enemy.status_effects["evade_boost"]
        self.assertEqual(boost, (0.5, 2))

    def test_regenerate_heals_fraction(self):
        self.enemy.cooldowns["regenerate"] = 0
        self.enemy.health = 50
        self.enemy.regenerate()
        expected_heal = self.enemy.max_health // 3
        self.assertEqual(
            self.enemy.health, min(50 + expected_heal, self.enemy.max_health)
        )

    def test_ability_cooldowns_decrement(self):
        self.enemy.cooldowns = {key: 1 for key in self.enemy.cooldowns}
        self.enemy.update()
        self.assertTrue(all(cd == 0 for cd in self.enemy.cooldowns.values()))

    def test_cannot_use_ability_on_cooldown(self):
        self.enemy.cooldowns["dark_bolt"] = 1
        self.enemy.dark_bolt(self.player)  # should NOT apply damage
        self.assertEqual(self.player.health, 100)

    def test_shadow_veil_does_not_crash_without_target(self):
        self.enemy.cooldowns["shadow_veil"] = 0
        try:
            self.enemy.shadow_veil()
        except Exception:
            self.fail("shadow_veil() raised an exception unexpectedly!")

    def test_regenerate_does_not_crash_without_target(self):
        self.enemy.cooldowns["regenerate"] = 0
        self.enemy.health = 100
        try:
            self.enemy.regenerate()
        except Exception:
            self.fail("regenerate() raised an exception unexpectedly!")


if __name__ == "__main__":
    unittest.main()
