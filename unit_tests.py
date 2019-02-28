import unittest
import numpy as np
from engine import Engine
from enemy import Enemy

eng = Engine('Darthur')

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
    test_enemy1 = Enemy(default_armor_class, default_modifiers)


    def test_all_spells(function):
        def wrapper(self):
            for spell in eng.spell_names:
                exp_v, sim_avg = function(self, spell)
                self.assertAlmostEqual(round(exp_v, 1), round(sim_avg, 1), delta=0.3)
                print('Passed {}. {} ~= {}'.format(spell, exp_v, sim_avg))

        return wrapper

    @test_all_spells
    def test_sim_equals_exp_v(self, spell, slot_level=3, sims=10000):
        exp_v = eng.cast_spell(spell, self.test_enemy1, slot_level=slot_level)
        sim_avg = np.mean([eng.cast_spell(spell, self.test_enemy1, slot_level=slot_level, sim=True)
                           for i in range(sims)])

        return exp_v, sim_avg

    @test_all_spells
    def test_sim_equals_exp_v_advantagve(self, spell, slot_level=3, sims=10000):
        exp_v = eng.cast_spell(spell, self.test_enemy1, slot_level=slot_level, advantage=True)
        sim_avg = np.mean([eng.cast_spell(spell, self.test_enemy1, slot_level=slot_level, sim=True, advantage=True)
                           for i in range(sims)])

        return exp_v, sim_avg