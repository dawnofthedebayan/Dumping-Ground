"""Animation 40 (continues from the end of animation 39): what we actually have to predict.

The sample table clears and one aircraft is plotted on its own: flight cycles and flight hours,
one point per month, from January 2014 to December 2024. The 2025 band then lights up empty, with
a question mark for each of its twelve months. 1080p only; the series is illustrative but shaped
like a real short-haul A320 (summer peaks, the 2020 collapse, the odd very quiet month).

    python anim_40_predict_2025.py            # -> output_slides/anim_40_predict_2025.gif
    python anim_40_predict_2025.py --preview  # fast check
"""

from common import main, progress
from map_common import SHARE_RED
from usecase_common import (CAM_USE, FINAL_NOTE, GOAL_NOTE, GOAL_Y, NOTE_Y, PREDICT_NOTE, Scene,
                            draw_series, draw_stats, draw_table, draw_title)

DURATION = 17.0
CHART_IN = 1.2
SWEEP = [1.8, 2.2]
BAND_IN, MARKS_IN, GOAL_IN = 8.4, 9.6, 13.0


def timeline(t):
    sc = Scene()
    draw_title(sc, 1.0, meta_a=0.0, data_a=1 - progress(t, 0.3, 0.5),
               goal_a=progress(t, 0.9, 0.5))
    draw_stats(sc, squeeze=1.0)
    table = 1 - progress(t, 0.3, 0.7)
    draw_table(sc, label_a=table, a=table)
    sc.pill(50.0, NOTE_Y, FINAL_NOTE, 1.3, 1 - progress(t, 0.2, 0.4), SHARE_RED, (255, 255, 255))
    band = progress(t, BAND_IN, 0.6)
    marks = progress(t, MARKS_IN, 1.4)
    for k in range(2):
        draw_series(sc, k, progress(t, CHART_IN, 0.6), progress(t, SWEEP[k], 4.4), band, marks)
    sc.pill(50.0, GOAL_Y, PREDICT_NOTE, 1.2,
            progress(t, BAND_IN + 0.5, 0.5) * (1 - progress(t, GOAL_IN - 0.3, 0.4)))
    sc.pill(50.0, GOAL_Y, GOAL_NOTE, 1.3, progress(t, GOAL_IN, 0.6), SHARE_RED, (255, 255, 255))
    return sc.state(CAM_USE)


if __name__ == "__main__":
    main("anim_40_predict_2025", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
