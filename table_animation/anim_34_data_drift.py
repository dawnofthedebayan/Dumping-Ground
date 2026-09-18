"""Animation 34 (continues from the end of animation 33): data drift. Time is paused at the alert.
The data-drift chart is outlined in red while the other charts dim, and the left side explains
what happened: a strip of 20 days from last year (mostly clear) and this winter, where days flip
to fog one by one and the average visibility falls, then what that does to the model. It ends
holding the full explanation; animation 35 clears it. 1080p only.

    python anim_34_data_drift.py            # 1080p GIF -> output_slides/anim_34_data_drift.gif
    python anim_34_data_drift.py --preview  # fast check
"""

from common import main
from mlops_common import (CAM_OPS, DURATIONS, PAUSE_WEEK, T0, draw_data_explainer, draw_ops,
                          highlight_in)
from model_common import Scene

DURATION = DURATIONS["data"]
T_IN = 0.3


def timeline(t):
    explainer, dim = highlight_in(t, T_IN)
    sc = Scene()
    draw_ops(sc, T0["data"] + t, PAUSE_WEEK, left_a=1 - dim, f1_a=1 - 0.8 * dim,
             concept_a=1 - 0.8 * dim, highlights=[("data", dim)])
    draw_data_explainer(sc, t - T_IN - 0.6, explainer)
    return sc.state(CAM_OPS)


if __name__ == "__main__":
    main("anim_34_data_drift", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
