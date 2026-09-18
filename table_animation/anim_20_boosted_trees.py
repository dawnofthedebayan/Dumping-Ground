"""Animation 20 (continues from the end of animation 19): gradient-boosted trees, the idea behind
XGBoost. The logistic-regression weights clear, training flights stream in again and two of the
50 real learned trees grow node by node: their questions, thresholds and leaf scores.

    python anim_20_boosted_trees.py            # 4K GIF -> output/anim_20_boosted_trees.gif
    python anim_20_boosted_trees.py --preview  # fast 1080p check
"""

import anim_19_logistic_regression as logreg
from common import INK, main, progress
from model_common import (BOX, LR_STEPS, Scene, draw_data_panel, draw_frame, draw_logreg,
                          draw_output_hint, draw_stream, draw_trees)
from split_common import CX

DURATION = 9.2  # s
TITLE = ("Model 2: gradient-boosted trees",
         "The idea behind XGBoost: many small decision trees, each fixing the errors of the last")
HEADER = "GRADIENT-BOOSTED TREES  ·  XGBOOST-STYLE"
NOTE = "Each tree learned its own questions and thresholds from the data"


def timeline(t):
    sc = Scene()
    sc.title(*logreg.TITLE, 1 - progress(t, 0.1, 0.4))
    sc.title(*TITLE, progress(t, 0.45, 0.5))
    draw_data_panel(sc, 1.0)
    head = progress(t, 0.5, 0.5)
    draw_frame(sc, 1.0, header_a=0.0)
    mid = (BOX[0] + BOX[2]) / 2
    sc.text(mid, BOX[1] + 0.55, logreg.HEADER, 0.34, INK, 1 - head, True)
    sc.text(mid, BOX[1] + 0.55, HEADER, 0.34, INK, head, True)
    draw_output_hint(sc, 1.0)
    draw_logreg(sc, 1 - progress(t, 0.2, 0.5), LR_STEPS)
    sc.pill(CX, 12.75, logreg.NOTE, 0.36, 1 - progress(t, 0.2, 0.4))
    draw_stream(sc, t, 1.0, 5.2)
    draw_trees(sc, 1.0, [progress(t, 1.4, 2.0, lambda x: max(0, min(1, x))),
                         progress(t, 3.7, 2.0, lambda x: max(0, min(1, x)))])
    sc.pill(CX, 12.75, NOTE, 0.36, progress(t, 6.4, 0.5))
    return sc.state()


if __name__ == "__main__":
    main("anim_20_boosted_trees", DURATION, timeline)
