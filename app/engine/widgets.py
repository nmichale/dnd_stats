from ipywidgets import *
import matplotlib.pyplot as plt
import engine
import enemy
import numpy as np
import matplotlib.ticker as ticker

STARTING_MOD = 0
STARTING_SLOT = 2
STARTING_AC = 10
STARTING_ADVANTAGE = False
STARTING_ROUNDS = 1
STARTING_RANGE_ENEMIES = 1
STARTING_WEB = False

MOD_SLIDER = dict(min=-10, max=10, step=1, value=STARTING_MOD)
AC_SLIDER = dict(min=0, max=30, step=1, value=STARTING_AC)
SLOT_SLIDER = dict(min=1, max=9, step=1, value=STARTING_SLOT)
ROUNDS_SLIDER = dict(min=1, max=10, step=1, value=STARTING_ROUNDS)
RANGE_ENEMIES_SLIDER = dict(min=1, max=10, step=1, value=STARTING_RANGE_ENEMIES)


def default_interact(update):
    return interact(update,
                    dex=widgets.IntSlider(**MOD_SLIDER),
                    con=widgets.IntSlider(**MOD_SLIDER),
                    _str=widgets.IntSlider(**MOD_SLIDER),
                    armor_class=widgets.IntSlider(**AC_SLIDER),
                    slot_level=widgets.IntSlider(**SLOT_SLIDER),
                    rounds=widgets.IntSlider(**ROUNDS_SLIDER),
                    range_enemies=widgets.IntSlider(**RANGE_ENEMIES_SLIDER))


def expected_damage(character='Darthur', figsize=(8,4), rotate=False, ylim=30, show=None):
    eng = engine.Engine(character)
    if show is None:
        show = eng.spell_names
    fig = plt.figure(figsize=figsize)
    ax = plt.gca()
    ax.set_ylim(top=ylim)

    e = enemy.create_enemy()

    bars = ax.bar(show, eng.evaluate_spells_exp_v(spells=show, enemy=e))
    if rotate:
        ax.set_xticklabels(show, rotation=45, ha="right")
    plt.title('Expected Damage')
    plt.ylabel('Damage')
    plt.show()

    texts = []

    def update(dex=STARTING_MOD, con=STARTING_MOD, _str=STARTING_MOD,
               armor_class=STARTING_AC, slot_level=STARTING_SLOT, advantage=STARTING_ADVANTAGE,
               rounds=STARTING_ROUNDS, range_enemies=STARTING_RANGE_ENEMIES, web=STARTING_WEB):
        e = enemy.create_enemy(dex=dex, con=con, str=_str, armor_class=armor_class)
        calcs = eng.evaluate_spells_exp_v(show, enemy=e, slot_level=slot_level, advantage=advantage, rounds=rounds,
                                          range_enemies=range_enemies, web=web)
        for i in range(len(texts)):
            texts.pop().remove()
        for i, (bar, calc) in enumerate(zip(bars, calcs)):
            bar.set_height(calc)
            texts.append(ax.text(bar.get_x() + bar.get_width() / 2, min(calc + 1, ylim-3), str(calc),
                    ha='center', va='bottom', fontweight='bold'))
        plt.show()

    return default_interact(update)

def distribution(character='Darthur', figsize=(8,6), bins=50, sims=10000, show=None):
    eng = engine.Engine(character)
    if show is None:
        show = eng.spell_names

    def plot_cdf(data, ax):
        data_sorted = np.sort(data)
        p = 1. * np.arange(len(data)) / (len(data) - 1)
        ax.plot(data_sorted, p)

    def update(dex=STARTING_MOD, con=STARTING_MOD, _str=STARTING_MOD,
               armor_class=STARTING_AC, slot_level=STARTING_SLOT, advantage=STARTING_ADVANTAGE,
               rounds=STARTING_ROUNDS, range_enemies=STARTING_RANGE_ENEMIES, web=STARTING_WEB):
        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 6))
        e = enemy.create_enemy(dex=dex, con=con, str=_str, armor_class=armor_class)

        sample_list = eng.evaluate_spells_sim(show, enemy=e, slot_level=slot_level, advantage=advantage, sims=sims, rounds=rounds,
                                          range_enemies=range_enemies, web=web)

        ax[0].hist(sample_list, bins, label=show)
        ax[0].legend(loc='upper right')

        ticks_y = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / sims))
        ax[0].yaxis.set_major_formatter(ticks_y)

        for spell_samples in sample_list:
            plot_cdf(spell_samples, ax[1])

        fig.tight_layout()
        plt.show()

    return default_interact(update)