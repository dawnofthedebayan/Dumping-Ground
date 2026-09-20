"""Animation 43 (continues from the end of animation 42): the same thing, for every aircraft.

The single aircraft's charts and its error bars clear, and twelve aircraft come up side by side -
each with its own 2024 history, its own red prediction for 2025 and its own black truth. Our MSN
10042 is the first of them, and 13,988 more sit behind. 1080p only; the series are illustrative.

    python anim_43_all_aircraft.py            # -> output_slides/anim_43_all_aircraft.gif
    python anim_43_all_aircraft.py --preview  # fast check
"""

from common import main, progress
from map_common import SHARE_RED
from usecase_common import (CAM_USE, GOAL_Y, MAE_NOTE, MINI_N, MINI_NOTE, Scene, draw_mae,
                            draw_minis, draw_series, draw_stats, draw_title)

DURATION = 12.0
GRID_IN, MORE_IN, NOTE_IN = 1.6, 5.4, 6.4
WHITE = (255, 255, 255)


def timeline(t):
    sc = Scene()
    draw_title(sc, 1.0, meta_a=0.0, goal_a=1.0)
    draw_stats(sc, squeeze=1.0)
    old = 1 - progress(t, 0.3, 0.8)
    draw_series(sc, 0, old, 1.0, 1.0, 1.0, 0.0, pred=1.0, act=1.0, err=1.0, zoom=1.0)
    draw_mae(sc, old, bars=1.0, formula=1.0)
    sc.pill(50.0, GOAL_Y, MAE_NOTE, 1.3, 1 - progress(t, 0.2, 0.4), SHARE_RED, WHITE)
    appear = [progress(t, GRID_IN + 0.16 * k, 0.5) for k in range(MINI_N)]
    draw_minis(sc, 1.0, appear, more_a=progress(t, MORE_IN, 0.5))
    sc.pill(50.0, GOAL_Y, MINI_NOTE, 1.3, progress(t, NOTE_IN, 0.6))
    return sc.state(CAM_USE)


if __name__ == "__main__":
    main("anim_43_all_aircraft", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
