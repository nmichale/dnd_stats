from lxml import objectify
import os
from enemy import Enemy
import random

class_modifier = {
    'Wizard': 'int',
    'Warlock': 'cha'
}

path = os.path.dirname(os.path.realpath(__file__))

class Engine(object):
    def __init__(self, character_name):
        self.character_xml = objectify.parse('{}/config/characters/{}.xml'.format(path, character_name.lower()))
        self.spellbook_xml = objectify.parse('{}/config/actions/{}.xml'.format(path, 'spells'))

        self.character = self.character_xml.getroot()
        self.spellbook = self.spellbook_xml.getroot()
        self.spell_names = self.spellbook_xml.findall('./spell/name')
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

    def _hit_chance(self, num, den=20, sim=False):
        chance = max(min(float(num)/float(den),1),0)
        return chance

    def cast_spell(self, spell, enemy, slot_level=2, sim=False):
        if isinstance(spell, basestring):
            spell = self.get_spell(spell)

        spell_class = spell['class']
        spell_level = spell['level']

        if spell_level > slot_level:
            return None

        higher_slot = slot_level - spell_level

        damage = 0
        for attack in spell.attack:
            hit_type = attack.attrib['hit_type']
            attack_damage = 0
            attack_times = int(attack.attrib.get('times', 1)) + higher_slot * int(attack.attrib.get('level_bonus', 0))
            for i in range(attack_times):
                spell_dc = self.character.modifiers[class_modifier[spell_class]] + self.character.proficiency
                if hit_type == 'spell_attack':
                    num = 20 + spell_dc - enemy.armor_class + 1
                    hit_chance = self._hit_chance(num)
                elif hit_type == 'saving_throw':
                    enemy_mod = float(enemy.modifiers[attack.attrib['modifier']])
                    num = 8 + spell_dc - enemy_mod - 1
                    hit_chance = self._hit_chance(num)
                elif hit_type == 'auto':
                    hit_chance = 1
                else:
                    raise NotImplementedError

                rolls = 0
                for die in attack.roll:
                    bonus = float(die.get('plus', 0))
                    if not sim:
                        num = die.num
                        num_bonus = die.get('level_bonus', False)
                        if num_bonus:
                            num += higher_slot * num_bonus

                        roll = num * (self._exp_v_die(die.sides) + bonus)
                        rolls += roll

                attack_damage = float(hit_chance) * rolls

                print(hit_chance, rolls)

                if hit_type == 'saving_throw' and bool(attack.attrib.get('half_dmg_fail', False)):
                    attack_damage += (1.0 - hit_chance) * (attack_damage / 2.0)

                damage += attack_damage

        return damage

def main():
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
    enemy = Enemy(default_armor_class, default_modifiers)

    print(eng.cast_spell('Chromatic Orb', enemy, slot_level=2))
    print(eng.cast_spell('Magic Missile', enemy, slot_level=2))
    print(eng.cast_spell('Fire Ball', enemy, slot_level=3))

if __name__ == '__main__':
     main()