"""Animation 18 (continues from the end of animation 17): the cross-validation folds clear away and
the flights regroup using the chronological split: 80 training flights in a grid on the left, the
20 most recent test flights hidden below them. An empty MODEL box and an OUTPUT panel appear.

    python anim_18_training_setup.py            # 4K GIF -> output/anim_18_training_setup.gif
    python anim_18_training_setup.py --preview  # fast 1080p check
"""

import anim_17_kfold_cross_validation as kfold
from common import MUTED, N_ROWS, ease_in_out_cubic, main, progress
from model_common import (BOX, GRID_RECT, Scene, draw_data_panel, draw_frame, draw_output_hint,
                          fade_state)
from split_common import RANDOM_ORDER, color, lerp_rect

DURATION = 5.8  # s
TITLE = ("Training a model",
         "Chronological split: learn from the 80 oldest flights, then predict the 20 most recent")
START = kfold.timeline(kfold.DURATION)


def timeline(t):
    old = fade_state(START, 1 - progress(t, 0.2, 0.5))
    sc = Scene()
    sc.lines, sc.texts, sc.pills = old["lines"], old["texts"], old["pills"]
    for j, entry in enumerate(START["tiles"]):
        col, x0, y0, x1, y1, r, a = entry
        if j >= N_ROWS:  # folds 2-5 fade away
            sc.tile(col, (x0, y0, x1, y1), a * (1 - progress(t, 0.3, 0.5)))
            continue
        i = RANDOM_ORDER[j]
        p = progress(t, 0.9 + 0.012 * j, 1.3, ease_in_out_cubic)
        sc.tile(color(i), lerp_rect((x0, y0, x1, y1), GRID_RECT[i], p),
                a + (1 - a) * progress(t, 0.3, 0.5))
    sc.title(*TITLE, progress(t, 0.6, 0.5))
    a = progress(t, 2.6, 0.6)
    labels = Scene()
    draw_data_panel(labels, a)
    sc.texts += labels.texts  # grid labels only; the tiles above are already in place
    draw_frame(sc, a)
    draw_output_hint(sc, progress(t, 3.0, 0.5))
    sc.text((BOX[0] + BOX[2]) / 2, 7.3, "?", 2.4, MUTED, progress(t, 3.2, 0.5), True)
    return sc.state()


if __name__ == "__main__":
    main("anim_18_training_setup", DURATION, timeline)
