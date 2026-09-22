"""Animation 41 (continues from the end of animation 40): the prediction, then the truth.

The twelve empty slots of 2025 fill with the model's answer (red, dashed), and then the months
actually happen: the real flight cycles and flight hours arrive in black. The gap between the two
lines is drawn in last - that gap is what the score is made of. 1080p only; numbers illustrative.

    python anim_41_prediction_vs_actual.py            # -> output_slides/anim_41_...gif
    python anim_41_prediction_vs_actual.py --preview  # fast check
"""

from common import ease_in_out_cubic, main, progress
from map_common import SHARE_RED
from usecase_common import (ACT_NOTE, CAM_USE, ERR_NOTE, GOAL_NOTE, GOAL_Y, PRED_NOTE, Scene,
                            draw_series, draw_stats, draw_title)

DURATION = 17.0
ZOOM_IN = 0.5
PRED_IN, ACT_IN, ERR_IN = 2.6, 7.6, 12.6
WHITE = (255, 255, 255)


def timeline(t):
    sc = Scene()
    draw_title(sc, 1.0, meta_a=0.0, goal_a=1.0)
    draw_stats(sc, squeeze=1.0)
    sc.pill(50.0, GOAL_Y, GOAL_NOTE, 1.3, 1 - progress(t, 0.3, 0.4), SHARE_RED, WHITE)
    q = 1 - progress(t, 0.4, 0.5)
    zoom = progress(t, ZOOM_IN, 1.6, ease_in_out_cubic)
    for k in range(2):
        draw_series(sc, k, 1.0, 1.0, 1.0, 1.0, q,
                    pred=progress(t, PRED_IN + 0.4 * k, 2.0),
                    act=progress(t, ACT_IN + 0.4 * k, 2.0),
                    err=progress(t, ERR_IN, 1.2), zoom=zoom)
    sc.pill(50.0, GOAL_Y, PRED_NOTE, 1.25,
            progress(t, PRED_IN + 0.4, 0.5) * (1 - progress(t, ACT_IN - 0.4, 0.4)))
    sc.pill(50.0, GOAL_Y, ACT_NOTE, 1.25,
            progress(t, ACT_IN + 0.4, 0.5) * (1 - progress(t, ERR_IN - 0.4, 0.4)))
    sc.pill(50.0, GOAL_Y, ERR_NOTE, 1.3, progress(t, ERR_IN + 0.4, 0.5), SHARE_RED, WHITE)
    return sc.state(CAM_USE)


if __name__ == "__main__":
    main("anim_41_prediction_vs_actual", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
