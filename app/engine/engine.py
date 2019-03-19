from lxml import objectify
import os
from enemy import Enemy
import random
import numpy as np
import pandas as pd

class_modifier = {
    'Wizard': 'int',
    'Warlock': 'cha'
}

path = os.path.dirname(os.path.realpath(__file__))

class Engine(object):
    def __init__(self, character_name):
        self.character_xml = objectify.parse('{}/dnd_config/characters/{}.xml'.format(path, character_name.lower()))
        self.spellbook_xml = objectify.parse('{}/dnd_config/actions/{}.xml'.format(path, 'spells'))

        self.character = self.character_xml.getroot()
        self.spellbook = self.spellbook_xml.getroot()
        self.spell_names = [node.text for node in self.spellbook_xml.findall('./spell/name')]
        self.character.proficiency = self.character.level % 4 + 2

    def _roll(self, sides):
        return random.randint(1, sides)

    def get_spell(self, name):
        return self.spellbook.spell[self.spell_names.index(name)]

    def _exp_v_die(self, sides):
        return (float(sides) + 1.0) / 2.0

    def _die_value(self, sides, sim=False):
        if sim:
            return self.roll(sides)
        else:
            return self.exp_v_die(sides)

    def _hit_chance(self, num, den=20):
        chance = max(min(float(num)/float(den),1),0)
        return chance

    def cast_spell(self, spell, enemy, slot_level=2, advantage=False, sim=False, rounds=1, range_enemies=1, web=False):
        if isinstance(spell, basestring):
            spell = self.get_spell(spell)

        spell_class = spell['class']
        spell_level = spell['level']

        if spell_level > slot_level:
            return 0

        higher_slot = slot_level - spell_level

        damage = 0
        for attack in spell.attack:

            continuing_bonus = 0
            continuing = bool(attack.get('continuing', False))

            if continuing and rounds <= 1:
                continue

            if continuing or spell_level == 0:
                max_rounds = float(attack.get('max_rounds', np.inf))
                continuing_bonus += int(min(rounds - 1, max_rounds - 1))

            hit_type = attack.attrib['hit_type']
            attack_damage = 0
            attack_times = int(attack.attrib.get('times', 1)) + higher_slot * int(attack.attrib.get('level_bonus', 0))

            enemy_bonus = 0
            if attack.get('radius'):
                enemy_bonus += range_enemies - 1

            total_times = attack_times + enemy_bonus + continuing_bonus
            for i in range(total_times):
                hit_chance = 0
                spell_dc = self.character.modifiers[class_modifier[spell_class]] + self.character.proficiency
                if hit_type == 'spell_attack':
                    if sim:
                        hit_roll = self._roll(20)

                        if advantage:
                            hit_roll2 = self._roll(20)
                            hit_roll = max(hit_roll, hit_roll2)

                        if hit_roll + spell_dc >= enemy.armor_class:
                            hit_chance = 1
                    else:
                        num = 20 + spell_dc - enemy.armor_class + 1
                        hit_chance = self._hit_chance(num)
                elif hit_type == 'saving_throw':
                    enemy_mod = float(enemy.modifiers[attack.attrib['modifier']])
                    to_beat = 8 + spell_dc
                    if sim:
                        saving_roll = self._roll(20)

                        if advantage:
                            saving_roll2 = self._roll(20)
                            saving_roll = min(saving_roll, saving_roll2)

                        if to_beat > saving_roll + enemy_mod:
                            hit_chance = 1
                    else:
                        num = to_beat - enemy_mod - 1
                        hit_chance = self._hit_chance(num)
                elif hit_type == 'auto':
                    hit_chance = 1
                else:
                    raise NotImplementedError

                half_dmg_fail = bool(attack.attrib.get('half_dmg_fail', False))
                if hit_chance <= 0 and not half_dmg_fail:
                    continue

                if not sim:
                    crit_chance = 1.0/20.0

                    if hit_type == 'spell_attack':
                        hit_chance -= crit_chance

                    if advantage:
                        if hit_type == 'spell_attack':
                            no_hit_chance = (1 - hit_chance - crit_chance)**2
                            crit_chance = 39.0/400.0
                            hit_chance = 1 - no_hit_chance - crit_chance
                        else:
                            hit_chance = 1 - (1 - hit_chance) ** 2

                rolls = 0
                for die in attack.roll:
                    bonus = float(die.get('plus', 0))
                    num = die.num
                    num_bonus = int(die.num.get('level_bonus', 0))
                    if num_bonus > 0:
                        bonus_levels = die.num.get('bonus_levels')
                        if bonus_levels is not None:
                            bonus_levels = map(int, bonus_levels.split(','))
                            level_bonus = sum([1 if self.character.level >= l else 0 for l in bonus_levels])
                            num += level_bonus * num_bonus
                        else:
                            num += higher_slot * num_bonus

                    # Critical Hit
                    if sim and hit_type == 'spell_attack' and hit_roll == 20:
                        num *= 2

                    if not sim:
                        single_roll = (self._exp_v_die(die.sides) + bonus)
                        roll = num * single_roll
                        rolls += roll
                    else:
                        for n in range(num):
                            rolls += self._roll(die.sides) + bonus

                if not sim and hit_type == 'spell_attack':
                    attack_damage += (crit_chance * rolls * 2) + ((hit_chance) * rolls)
                else:
                    attack_damage += float(hit_chance) * rolls

                if hit_type == 'saving_throw' and half_dmg_fail:
                    attack_damage += (1.0 - hit_chance) * (rolls / 2.0)

            damage += attack_damage

            damage_type = attack.get('damage_type')
            if damage_type:
                damage_type = damage_type.split(',')
                if web and 'fire' in damage_type and spell.name != 'Web':
                    damage += self.cast_spell('Web', enemy, 2, advantage, sim, rounds, range_enemies, False)

        return damage

    def evaluate_spells_exp_v(self, spells=None, **kwargs):
        if spells is None:
            spells = self.spell_names
        return [self.cast_spell(sp, **kwargs) for sp in spells]

    def evaluate_spells_sim(self, spells=None, **kwargs):
        sims = kwargs.pop('sims')
        if spells is None:
            spells = self.spell_names
        return [[self.cast_spell(sp, sim=True, **kwargs) for i in range(sims)] for sp in spells]