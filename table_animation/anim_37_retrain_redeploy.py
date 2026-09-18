"""Animation 37 (continues from the end of animation 36): back to the drawing board. The
"constant monitoring" message clears and the MLOps loop moves on: check hypothesis, collect new
data, retrain (the model box shows "v2 being trained..."), evaluate and deploy. MODEL v2 goes
live, F1 climbs back above the threshold and the alert clears, the training data catches up with
the foggy live data and the model's belief lines up with reality again. The loop returns to
Monitor and it ends on "The loop never ends: ... v2, v3, v4 ...". 1080p only.

    python anim_37_retrain_redeploy.py            # 1080p GIF -> output_slides/anim_37_retrain_redeploy.gif
    python anim_37_retrain_redeploy.py --preview  # fast check
"""

from common import WHITE, main, progress
from map_common import SHARE_RED
from mlops_common import (CAM_OPS, DURATIONS, FINAL_NOTE, NOTE_Y, PAUSE_WEEK, T0, draw_ops,
                          last_frame_time, monitor_pulse, piecewise)
from model_common import Scene

DURATION = DURATIONS["retrain"]
WEEKS = [(0.8, PAUSE_WEEK), (10.8, 32.0), (16.8, 42.0)]
LOOP_NOTE = "The loop never ends: monitor, retrain, redeploy...   v2, v3, v4 ..."
PULSE_AT_START = monitor_pulse(last_frame_time(DURATIONS["constant"]))


def timeline(t):
    sc = Scene()
    draw_ops(sc, T0["retrain"] + t, piecewise(WEEKS, t),
             pulse=PULSE_AT_START * (1 - progress(t, 0.2, 0.5)))
    sc.pill(50.0, NOTE_Y, FINAL_NOTE, 1.5, 1 - progress(t, 0.3, 0.5), SHARE_RED, WHITE)
    sc.pill(50.0, NOTE_Y, LOOP_NOTE, 1.3, progress(t, 17.2, 0.6), SHARE_RED, WHITE)
    return sc.state(CAM_OPS)


if __name__ == "__main__":
    main("anim_37_retrain_redeploy", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
