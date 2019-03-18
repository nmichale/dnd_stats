from ipywidgets import *
import matplotlib.pyplot as plt
import engine
import enemy
import numpy as np
import matplotlib.ticker as ticker

STARTING_DEX = 0
STARTING_SLOT = 2
STARTING_AC = 10
STARTING_ADVANTAGE = False
STARTING_ROUNDS = 1
STARTING_RANGE_ENEMIES = 1

DEX_SLIDER = dict(min=-10, max=10, step=1, value=STARTING_DEX)
AC_SLIDER = dict(min=0, max=30, step=1, value=STARTING_AC)
SLOT_SLIDER = dict(min=1, max=9, step=1, value=STARTING_SLOT)
ROUNDS_SLIDER = dict(min=1, max=10, step=1, value=STARTING_ROUNDS)
RANGE_ENEMIES_SLIDER = dict(min=1, max=10, step=1, value=STARTING_RANGE_ENEMIES)


def default_interact(update):
    return interact(update, dex=widgets.IntSlider(**DEX_SLIDER),
                            armor_class=widgets.IntSlider(**AC_SLIDER),
                            slot_level=widgets.IntSlider(**SLOT_SLIDER),
                            rounds=widgets.IntSlider(**ROUNDS_SLIDER),
                            range_enemies=widgets.IntSlider(**RANGE_ENEMIES_SLIDER))


def expected_damage(character='Darthur', figsize=(8,4), rotate=False, ylim=30):
    eng = engine.Engine(character)
    fig = plt.figure(figsize=figsize)
    ax = plt.gca()
    ax.set_ylim(top=ylim)

    e = enemy.create_enemy()

    bars = ax.bar(eng.spell_names, eng.evaluate_spells_exp_v(enemy=e))
    if rotate:
        plt.xticks(rotation=45)
    plt.title('Expected Damage')
    plt.ylabel('Damage')
    plt.show()

    texts = []

    def update(dex=STARTING_DEX, armor_class=STARTING_AC, slot_level=STARTING_SLOT, advantage=STARTING_ADVANTAGE,
               rounds=STARTING_ROUNDS, range_enemies=STARTING_RANGE_ENEMIES):
        e = enemy.create_enemy(dex=dex, armor_class=armor_class)
        calcs = eng.evaluate_spells_exp_v(enemy=e, slot_level=slot_level, advantage=advantage, rounds=rounds,
                                          range_enemies=range_enemies)
        for i in range(len(texts)):
            texts.pop().remove()
        for i, (bar, calc) in enumerate(zip(bars, calcs)):
            bar.set_height(calc)
            texts.append(ax.text(bar.get_x() + bar.get_width() / 2, min(calc + 1, ylim-3), str(calc),
                    ha='center', va='bottom', fontweight='bold'))
        plt.show()

    return default_interact(update)

def distribution(character='Darthur', figsize=(8,6), bins=50, sims=10000):
    eng = engine.Engine(character)

    def plot_cdf(data, ax):
        data_sorted = np.sort(data)
        p = 1. * np.arange(len(data)) / (len(data) - 1)
        ax.plot(data_sorted, p)

    def update(dex=STARTING_DEX, armor_class=STARTING_AC, slot_level=STARTING_SLOT, advantage=STARTING_ADVANTAGE,
               rounds=STARTING_ROUNDS, range_enemies=STARTING_RANGE_ENEMIES):
        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 6))
        e = enemy.create_enemy(dex=dex, armor_class=armor_class)

        sample_list = eng.evaluate_spells_sim(enemy=e, slot_level=slot_level, advantage=advantage, sims=sims, rounds=rounds,
                                          range_enemies=range_enemies)

        ax[0].hist(sample_list, bins, label=eng.spell_names)
        ax[0].legend(loc='upper right')

        ticks_y = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / sims))
        ax[0].yaxis.set_major_formatter(ticks_y)

        for spell_samples in sample_list:
            plot_cdf(spell_samples, ax[1])

        fig.tight_layout()
        plt.show()

    return default_interact(update)