"""Animation 26a (continues from the end of animation 26): every model has two scores, not one.

The confusion matrix and the four metric cards clear away and the training and test grids come back
side by side with the score the model gets on each. The 90% we have been quoting all along is the
second number; the first one - what it scores on the 80 flights it was trained on - is a memory
test, and the distance between them is the subject of the next few slides.

    python anim_26a_two_scores.py            # 4K GIF -> output/anim_26a_two_scores.gif
    python anim_26a_two_scores.py --preview  # fast 1080p check
"""

import anim_26_f1_score as f1
from common import HEADER_BG, INK, MUTED, WHITE, main, mix, progress
from fit_common import DECK_TEST_ACC, DECK_TRAIN_ACC
from model_common import (TEST, TEST_GRID0, TEST_RECT, TRAIN, TRAIN_GRID0, TRAIN_RECT, Scene,
                          fade_state, pct)
from split_common import CX, color

DURATION = 9.0  # s
END = f1.timeline(f1.DURATION)

TITLE = ("Evaluation  ·  the score we never showed you",
         "A model is always scored twice: on what it has seen, and on what it has not")
CARDS = [
    ((13.0, 3.8, 35.4, 7.8), "SCORED ON THE 80 IT TRAINED ON",
     "It has already seen every one of these flights", DECK_TRAIN_ACC, 0.38),
    ((13.0, 8.4, 35.4, 12.4), "SCORED ON THE 20 IT NEVER SAW",
     "The only number that says anything about tomorrow", DECK_TEST_ACC, 1.0),
]
GAP = round(100 * (DECK_TRAIN_ACC - DECK_TEST_ACC), 1)
NOTE_1 = "Every score in this workshop so far has been the second one"
NOTE_2 = (f"{pct(DECK_TRAIN_ACC)} remembered, {pct(DECK_TEST_ACC)} understood  ·  "
          f"the {GAP:g}-point gap is the warning light")


def grids(sc, a):
    sc.text(TRAIN_GRID0[0] + 3.1, TRAIN_GRID0[1] - 0.55, "TRAINING DATA  ·  80", 0.32, INK,
            a, True)
    for i in TRAIN:
        sc.tile(color(i), TRAIN_RECT[i], a)
    sc.text(TEST_GRID0[0] + 3.1, TEST_GRID0[1] - 0.5, "TEST DATA  ·  20", 0.32, INK, a, True)
    for i in TEST:
        sc.tile(color(i), TEST_RECT[i], a)


def card(sc, k, a, count):
    (x0, y0, x1, y1), label, sub, value, dark = CARDS[k]
    sc.tile(HEADER_BG, (x0, y0, x1, y1), a, 0.3)
    sc.text(x0 + 0.7, y0 + 0.95, label, 0.38, INK, a, True, "lm")
    sc.text(x0 + 0.7, y0 + 1.72, sub, 0.29, MUTED, a, False, "lm")
    sc.text(x1 - 0.7, y0 + 1.4, pct(value * count), 1.35, INK, a, True, "rm")
    sc.tile(mix(WHITE, INK, 0.1), (x0 + 0.7, y0 + 3.0, x1 - 0.7, y0 + 3.28), a, 0.14)
    sc.tile(mix(WHITE, INK, dark), (x0 + 0.7, y0 + 3.0,
                                    x0 + 0.7 + (x1 - x0 - 1.4) * value * count, y0 + 3.28), a, 0.14)


def timeline(t):
    sc = Scene()
    sc.title(*TITLE, progress(t, 0.5, 0.5))
    grids(sc, progress(t, 0.9, 0.6))
    arrows = progress(t, 1.7, 0.5)
    for y in (5.9, 10.4):
        sc.arrow(7.2, y, 12.6, arrows)
    for k, start in enumerate((2.1, 3.7)):
        card(sc, k, progress(t, start, 0.5), progress(t, start + 0.25, 1.1))
    sc.pill(CX, 13.7, NOTE_1, 0.36, progress(t, 5.3, 0.5) * (1 - progress(t, 6.9, 0.4)))
    sc.pill(CX, 13.7, NOTE_2, 0.36, progress(t, 7.2, 0.5))
    st = sc.state()
    old = fade_state(END, 1 - progress(t, 0.15, 0.45))
    for key in ("tiles", "boxes", "lines", "texts", "pills"):
        st[key] = old[key] + st[key]
    return st


if __name__ == "__main__":
    main("anim_26a_two_scores", DURATION, timeline)
