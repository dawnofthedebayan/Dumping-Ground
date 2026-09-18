"""Animation 19 (continues from the end of animation 18): logistic regression. Training flights
stream into the model while the weight bars replay the real gradient-descent path from zero to the
learned weights; the formula turning the weighted sum into a probability sits underneath.

    python anim_19_logistic_regression.py            # 4K GIF -> output/anim_19_logistic_regression.gif
    python anim_19_logistic_regression.py --preview  # fast 1080p check
"""

import anim_18_training_setup as setup
from common import MUTED, clamp01, main, progress
from model_common import (BOX, LR_STEPS, Scene, draw_data_panel, draw_frame, draw_logreg,
                          draw_output_hint, draw_stream)
from split_common import CX

DURATION = 8.6  # s
TITLE = ("Model 1: logistic regression",
         "It learns one weight per feature: how strongly that feature pushes towards a delay")
HEADER = "LOGISTIC REGRESSION"
NOTE = "Nobody wrote these rules: the weights were learned from the 80 training flights"
TRAIN_START, TRAIN_LEN = 1.4, 4.2


def step_at(t):
    return round(LR_STEPS * clamp01((t - TRAIN_START) / TRAIN_LEN))


def timeline(t):
    sc = Scene()
    sc.title(*setup.TITLE, 1 - progress(t, 0.1, 0.4))
    sc.title(*TITLE, progress(t, 0.45, 0.5))
    draw_data_panel(sc, 1.0)
    head = progress(t, 0.5, 0.5)
    draw_frame(sc, 1.0, header_a=0.0)
    mid = (BOX[0] + BOX[2]) / 2
    sc.text(mid, BOX[1] + 0.55, "MODEL", 0.34, (31, 41, 55), 1 - head, True)
    sc.text(mid, BOX[1] + 0.55, HEADER, 0.34, (31, 41, 55), head, True)
    sc.text(mid, 7.3, "?", 2.4, MUTED, 1 - progress(t, 0.2, 0.4), True)
    draw_output_hint(sc, 1.0)
    draw_stream(sc, t, 1.2, 5.0)
    draw_logreg(sc, progress(t, 0.8, 0.5), step_at(t))
    sc.pill(CX, 12.75, NOTE, 0.36, progress(t, 6.2, 0.5))
    return sc.state()


if __name__ == "__main__":
    main("anim_19_logistic_regression", DURATION, timeline)
