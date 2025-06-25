import unittest
import random
from characters import Warrior, Mage, Archer, Assassin
from base import Character


class AutoBattleTest(unittest.TestCase):

    def simulate_battle(self, player: Character, enemy: Character, max_turns=50):
        """Simulates a full battle and returns the winner's name."""
        turn = 0
        while player.health > 0 and enemy.health > 0 and turn < max_turns:
            # Player turn
            if player.status_effects.get("stunned", 0) == 0:
                self.perform_auto_action(player, enemy)
            else:
                print(f"{player.name} is stunned.")

            # Enemy turn
            if enemy.health > 0 and enemy.status_effects.get("stunned", 0) == 0:
                self.perform_auto_action(enemy, player)
            else:
                print(f"{enemy.name} is stunned.")

            player.update()
            enemy.update()
            turn += 1

        if player.health > 0 and enemy.health <= 0:
            return player.name
        elif enemy.health > 0 and player.health <= 0:
            return enemy.name
        return "draw"

    def perform_auto_action(self, actor: Character, target: Character):
        """Randomly choose an action for the actor."""
        action = random.choice(["attack", "special", "heal"])
        if action == "attack":
            actor.attack(target)
        elif action == "heal":
            actor.heal()
        elif action == "special" and actor.abilities:
            ready = [
                i
                for i, name in enumerate(actor.abilities)
                if actor.is_ability_ready(name)
            ]
            if ready:
                idx = random.choice(ready)
                try:
                    actor.special(idx, target)
                except Exception as e:
                    print(f"{actor.name} failed to use special: {e}")
            else:
                actor.attack(target)

    def test_warrior_vs_mage(self):
        winner = self.simulate_battle(Warrior("Throg"), Mage("Zyra"))
        self.assertIn(winner, ["Throg", "Zyra"], "Unexpected result")

    def test_archer_vs_assassin(self):
        winner = self.simulate_battle(Archer("Lina"), Assassin("Vale"))
        self.assertIn(winner, ["Lina", "Vale"], "Unexpected result")

    def test_mage_vs_assassin(self):
        winner = self.simulate_battle(Mage("Merla"), Assassin("Nyx"))
        self.assertIn(winner, ["Merla", "Nyx"], "Unexpected result")

    def test_archer_vs_warrior(self):
        winner = self.simulate_battle(Archer("Robin"), Warrior("Krug"))
        self.assertIn(winner, ["Robin", "Krug"], "Unexpected result")


if __name__ == "__main__":
    unittest.main()
