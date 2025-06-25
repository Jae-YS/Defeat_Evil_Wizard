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
        """Dark Bolt should reduce the target's HP by attack_power + 10."""
        self.enemy.cooldowns["dark_bolt"] = 0
        initial_health = self.player.health
        self.enemy.dark_bolt(self.player)
        expected_damage = self.enemy.attack_power + 10
        self.assertEqual(self.player.health, initial_health - expected_damage)

    def test_drain_life_damage_and_heal(self):
        """Drain Life should deal 20 damage and heal the caster for 10."""
        self.enemy.cooldowns["drain_life"] = 0
        self.enemy.health = 100  # not full
        self.player.health = 100
        self.enemy.drain_life(self.player)
        self.assertEqual(self.enemy.health, 110)
        self.assertEqual(self.player.health, 80)

    def test_drain_life_heal_caps_at_max(self):
        """Healing from Drain Life should not exceed max health."""
        self.enemy.cooldowns["drain_life"] = 0
        self.enemy.health = self.enemy.max_health - 5
        self.enemy.drain_life(self.player)
        self.assertEqual(self.enemy.health, self.enemy.max_health)

    def test_curse_reduces_attack(self):
        """Curse should reduce the target's attack power by 5."""
        self.enemy.cooldowns["curse"] = 0
        self.player.attack_power = 20
        self.enemy.curse(self.player)
        self.assertEqual(self.player.attack_power, 15)

    def test_curse_does_not_go_below_zero(self):
        """Curse should not reduce attack power below 0."""
        self.enemy.cooldowns["curse"] = 0
        self.player.attack_power = 4
        self.enemy.curse(self.player)
        self.assertEqual(self.player.attack_power, 0)

    def test_shadow_veil_sets_evasion_boost(self):
        """Shadow Veil should set a 0.5 evasion boost for 2 turns."""
        self.enemy.cooldowns["shadow_veil"] = 0
        self.enemy.shadow_veil()
        boost = self.enemy.status_effects["evade_boost"]
        self.assertEqual(boost, (0.5, 2))

    def test_regenerate_heals_fraction(self):
        """Regenerate should heal 1/3 of max HP without exceeding it."""
        self.enemy.cooldowns["regenerate"] = 0
        self.enemy.health = 50
        self.enemy.regenerate()
        expected = min(50 + self.enemy.max_health // 3, self.enemy.max_health)
        self.assertEqual(self.enemy.health, expected)

    def test_regenerate_does_not_exceed_max_health(self):
        """Regenerate should not heal above max health."""
        self.enemy.cooldowns["regenerate"] = 0
        self.enemy.health = self.enemy.max_health - 1
        self.enemy.regenerate()
        self.assertEqual(self.enemy.health, self.enemy.max_health)

    def test_ability_cooldowns_decrement(self):
        """Cooldowns should decrease by 1 after update()."""
        self.enemy.cooldowns = {k: 1 for k in self.enemy.cooldowns}
        self.enemy.update()
        self.assertTrue(all(cd == 0 for cd in self.enemy.cooldowns.values()))

    def test_cannot_use_ability_on_cooldown(self):
        """Attempting to use an ability on cooldown should do nothing."""
        self.enemy.cooldowns["dark_bolt"] = 1
        self.enemy.dark_bolt(self.player)  # Should not apply damage
        self.assertEqual(self.player.health, 100)

    def test_shadow_veil_does_not_crash_without_target(self):
        """Calling shadow_veil() with no target should not raise an error."""
        self.enemy.cooldowns["shadow_veil"] = 0
        try:
            self.enemy.shadow_veil()
        except Exception as e:
            self.fail(f"shadow_veil() raised an unexpected exception: {e}")

    def test_regenerate_does_not_crash_without_target(self):
        """Calling regenerate() with no target should not raise an error."""
        self.enemy.cooldowns["regenerate"] = 0
        try:
            self.enemy.regenerate()
        except Exception as e:
            self.fail(f"regenerate() raised an unexpected exception: {e}")

    def test_all_abilities_have_cooldowns(self):
        """Each ability in the dictionary should be initialized with a cooldown."""
        for ability in self.enemy.abilities:
            self.assertIn(ability, self.enemy.cooldowns)
            self.assertIsInstance(self.enemy.cooldowns[ability], int)

    def test_cooldowns_start_at_zero(self):
        """By default, all ability cooldowns should start at 0."""
        self.assertTrue(all(cd == 0 for cd in self.enemy.cooldowns.values()))


if __name__ == "__main__":
    unittest.main()
