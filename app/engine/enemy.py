
default_modifiers = {
        'str': 0,
        'dex': 0,
        'con': 0,
        'int': 0,
        'wis': 0,
        'cha': 0
    }
default_armor_class = 10

class Enemy(object):
    def __init__(self, armor_class, modifiers):
        self.armor_class = armor_class
        self.modifiers = modifiers

def create_enemy(**deviations):
    e = Enemy(default_armor_class, default_modifiers)

    for dev, val in deviations.items():
        if dev == 'armor_class':
            e.armor_class = val
        else:
            e.modifiers[dev] = val

    return e