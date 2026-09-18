"""Animation 36 (continues from the end of animation 35): the concept-drift explanation clears
and the whole monitoring slide returns; "MLOps requires constant monitoring" appears, and the live
flights keep streaming through the model while the Monitor stage of the loop pulses, for about
40 seconds before the GIF holds its last frame. 1080p only.

    python anim_36_constant_monitoring.py            # 1080p GIF -> output_slides/anim_36_constant_monitoring.gif
    python anim_36_constant_monitoring.py --preview  # fast check
"""

from common import WHITE, main, progress
from map_common import SHARE_RED
from mlops_common import (CAM_OPS, DONE, DURATIONS, FINAL_NOTE, NOTE_Y, PAUSE_WEEK, T0,
                          draw_concept_explainer, draw_ops, highlight_out, monitor_pulse)
from model_common import Scene

DURATION = DURATIONS["constant"]
T_OUT = 0.3


def timeline(t):
    expl, dim = highlight_out(t, T_OUT)
    pulse = monitor_pulse(t)
    sc = Scene()
    draw_ops(sc, T0["constant"] + t, PAUSE_WEEK, left_a=1 - dim, f1_a=1 - 0.8 * dim,
             data_a=1 - 0.8 * dim, marker=expl, highlights=[("concept", dim)], pulse=pulse)
    draw_concept_explainer(sc, DONE, expl)
    sc.pill(50.0, NOTE_Y, FINAL_NOTE, 1.5, progress(t, 1.8, 0.6), SHARE_RED, WHITE)
    return sc.state(CAM_OPS)


if __name__ == "__main__":
    main("anim_36_constant_monitoring", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
