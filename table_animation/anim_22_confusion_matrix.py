"""Animation 22 (continues from the end of animation 21): evaluation. The model and data clear
away; each test flight drops from its probability row into a 2 x 2 confusion matrix by what
really happened (row) and what the model predicted (column), and the four counts tick up.

    python anim_22_confusion_matrix.py            # 4K GIF -> output/anim_22_confusion_matrix.gif
    python anim_22_confusion_matrix.py --preview  # fast 1080p check
"""

import math

import anim_20_boosted_trees as trees
import anim_21_predict_probability as predict
from common import ease_in_out_cubic, main, progress
from model_common import (CELL_SLOT, MATRIX_NOTE, N_TEST, TEST, Scene, draw_data_panel,
                          draw_frame, draw_matrix, draw_output_row, draw_threshold, draw_trees,
                          output_tile_rect)
from split_common import CX, color, lerp_rect

DURATION = 8.6  # s
TITLE = ("Evaluation on the test set", "Compare each prediction with what really happened")
DROP0, DROP_GAP, DROP_LEN = 1.4, 0.18, 0.8


def timeline(t):
    sc = Scene()
    sc.title(*predict.TITLE, 1 - progress(t, 0.1, 0.4))
    sc.title(*TITLE, progress(t, 0.45, 0.5))
    fade = 1 - progress(t, 0.2, 0.6)
    draw_data_panel(sc, fade, skip_test=set(TEST))
    draw_frame(sc, fade, header=trees.HEADER)
    draw_trees(sc, fade, [1.0, 1.0])
    draw_threshold(sc, fade)
    sc.pill(CX, 12.75, predict.NOTE, 0.36, fade)
    landed = sum(1 for k in range(N_TEST) if t >= DROP0 + k * DROP_GAP + DROP_LEN)
    draw_matrix(sc, progress(t, 0.9, 0.5), counts_upto=landed)
    for k, i in enumerate(TEST):
        start = DROP0 + k * DROP_GAP
        draw_output_row(sc, k, i, 1.0, 1 - progress(t, start, 0.3))
        p = progress(t, start, DROP_LEN, ease_in_out_cubic)
        x0, y0, x1, y1 = lerp_rect(output_tile_rect(k), CELL_SLOT[k], p)
        lift = math.sin(math.pi * p) * 1.2
        sc.tile(color(i), (x0, y0 - lift, x1, y1 - lift), 1.0)
    sc.pill(CX, 11.85, MATRIX_NOTE, 0.36, progress(t, 6.0, 0.5))
    return sc.state()


if __name__ == "__main__":
    main("anim_22_confusion_matrix", DURATION, timeline)
