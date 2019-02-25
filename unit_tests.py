import unittest
import numpy as np
from engine import Engine
from enemy import Enemy

class UnitTests(unittest.TestCase):
    default_modifiers = {
        'str': 0,
        'dex': 0,
        'con': 0,
        'int': 0,
        'wis': 0,
        'cha': 0
    }
    default_armor_class = 10
    eng = Engine('Darthur')
    test_enemy1 = Enemy(default_armor_class, default_modifiers)

    def test_sim_equals_exp_v(self):
        SLOT_LEVEL = 3
        SIMS = 10000

        for spell in self.eng.spell_names:
            exp_v = self.eng.cast_spell(spell, self.test_enemy1, slot_level=SLOT_LEVEL)
            sim_avg = np.mean([self.eng.cast_spell(spell, self.test_enemy1, slot_level=SLOT_LEVEL) for i in range(SIMS)])

            self.assertAlmostEqual(exp_v, sim_avg, places=4)

    def test_sim_equals_exp_v_advantagve(self):
        SLOT_LEVEL = 3
        SIMS = 10000

        for spell in self.eng.spell_names:
            exp_v = self.eng.cast_spell(spell, self.test_enemy1, slot_level=SLOT_LEVEL, advantage=True)
            sim_avg = np.mean([self.eng.cast_spell(spell, self.test_enemy1, slot_level=SLOT_LEVEL, advantage=True) for i in range(SIMS)])

            self.assertAlmostEqual(exp_v, sim_avg, places=4)