"""Animation 35 (continues from the end of animation 34): concept drift. The data-drift
explanation clears and the slide briefly returns to normal; then the concept-drift chart is
outlined in red while the other charts dim, and the left side animates why: the airport has 13
departure slots an hour, runway 2 closes and 5 slots are crossed out, then a busy hour of 9
departures fills the slots and the 9th has none, so it is delayed. The model still believes a 10%
delay risk for such an hour while reality is ~63% (marked on the chart). It ends holding the
full explanation; animation 36 clears it. 1080p only.

    python anim_35_concept_drift.py            # 1080p GIF -> output_slides/anim_35_concept_drift.gif
    python anim_35_concept_drift.py --preview  # fast check
"""

from common import main, progress
from mlops_common import (CAM_OPS, DONE, DURATIONS, PAUSE_WEEK, T0, draw_concept_explainer,
                          draw_data_explainer, draw_ops, highlight_in, highlight_out)
from model_common import Scene

DURATION = DURATIONS["concept"]
DATA_OUT, T_IN = 0.3, 2.2


def timeline(t):
    data_expl, data_dim = highlight_out(t, DATA_OUT)
    expl, dim = highlight_in(t, T_IN)
    busy = max(data_dim, dim)
    sc = Scene()
    draw_ops(sc, T0["concept"] + t, PAUSE_WEEK, left_a=1 - busy, f1_a=1 - 0.8 * busy,
             data_a=1 - 0.8 * dim, concept_a=1 - 0.8 * data_dim,
             marker=progress(t, T_IN + 11.0, 0.6),
             highlights=[("data", data_dim), ("concept", dim)])
    draw_data_explainer(sc, DONE, data_expl)
    draw_concept_explainer(sc, t - T_IN - 0.6, expl)
    return sc.state(CAM_OPS)


if __name__ == "__main__":
    main("anim_35_concept_drift", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
