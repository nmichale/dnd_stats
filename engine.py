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
        return (sides + 1) / 2

    def _die_value(self, sides, sim=False):
        if sim:
            return self.roll(sides)
        else:
            return self.exp_v_die(sides)

    def _hit_chance(self, num, den=20, sim=False):
        chance = float(num)/float(den)
        if chance > 1:
            return 1
        elif chance < 0:
            return 0
        return chance

    def cast_spell(self, spell, enemy, slot_level=2, sim=False):
        spell_class = spell['class']
        spell_level = spell['level']

        damage = 0
        for attack in spell.attack:
            hit_type = attack.attrib['hit_type']
            attack_damage = 0
            for i in range(int(attack.attrib.get('times', 0))):
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

                for die in attack.roll:
                    if not sim:
                        num = die.num
                        num_bonus = die.get('level_bonus')
                        if num_bonus:
                            num += (spell_level - slot_level)*num_bonus

                        roll = num * self._exp_v_die(die.sides)
                        damage += roll * hit_chance

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

    print(eng.cast_spell(eng.get_spell('Chromatic Orb'), enemy, slot_level=2))

if __name__ == '__main__':
     main()