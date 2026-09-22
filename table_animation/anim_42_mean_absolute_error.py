"""Animation 42 (continues from the end of animation 41): mean absolute error.

The flight_hours chart clears and the twelve monthly gaps of the flight_cycles chart are stacked
up as bars: |actual - predicted| for each month, then averaged into one number, the MAE. It ends
asking whether that number is large or small - which animation 44 answers. 1080p only.

    python anim_42_mean_absolute_error.py            # -> output_slides/anim_42_...gif
    python anim_42_mean_absolute_error.py --preview  # fast check
"""

from common import main, progress
from map_common import SHARE_RED
from usecase_common import (CAM_USE, ERR_NOTE, GOAL_Y, MAE_NOTE, Scene, draw_mae, draw_series,
                            draw_stats, draw_title)

DURATION = 13.0
BARS_IN, FORMULA_IN, NOTE_IN = 1.8, 5.4, 7.2
WHITE = (255, 255, 255)


def timeline(t):
    sc = Scene()
    draw_title(sc, 1.0, meta_a=0.0, goal_a=1.0)
    draw_stats(sc, squeeze=1.0)
    sc.pill(50.0, GOAL_Y, ERR_NOTE, 1.3, 1 - progress(t, 0.3, 0.4), SHARE_RED, WHITE)
    draw_series(sc, 0, 1.0, 1.0, 1.0, 1.0, 0.0, pred=1.0, act=1.0, err=1.0, zoom=1.0)
    draw_series(sc, 1, 1 - progress(t, 0.4, 0.8), 1.0, 1.0, 1.0, 0.0, pred=1.0, act=1.0, err=1.0, zoom=1.0)
    draw_mae(sc, progress(t, 1.4, 0.6), bars=progress(t, BARS_IN, 2.6),
             formula=progress(t, FORMULA_IN, 0.6))
    sc.pill(50.0, GOAL_Y, MAE_NOTE, 1.3, progress(t, NOTE_IN, 0.6), SHARE_RED, WHITE)
    return sc.state(CAM_USE)


if __name__ == "__main__":
    main("anim_42_mean_absolute_error", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
