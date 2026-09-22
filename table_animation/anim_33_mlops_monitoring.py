"""Animation 33 (continues from the end of animation 32): deployment and monitoring.

The machine-learning map clears and the CLASSIFICATION panel becomes the deployed MODEL v1. Live
flights stream through it, the MLOps loop and the monitoring dashboard come up, and the weeks tick
by: first the data drifts (winter fog), then the concept drifts (a runway closes). Live F1 sags and
falls through the 75% threshold; the ALERT fires and the animation stops there. Animations 34 and
35 then explain each drift. 1080p only; all numbers are illustrative.

    python anim_33_mlops_monitoring.py            # 1080p GIF -> output_slides/anim_33_mlops_monitoring.gif
    python anim_33_mlops_monitoring.py --preview  # fast check
"""

from common import ease_in_out_cubic, lerp, lerp_camera, main, progress
from map_common import CAM_MAP, CLS, DONE, map_state
from mlops_common import (CAM_OPS, DURATIONS, MODEL_BOX, PAUSE_WEEK, T0, draw_ops, piecewise)
from model_common import Scene, fade_state

DURATION = DURATIONS["monitor"]
WEEKS = [(4.0, 0.0), (17.3, PAUSE_WEEK)]


def timeline(t):
    others = 1 - progress(t, 0.2, 0.8)
    base = fade_state(map_state(cls=0.0, cls_content=0.0, top=0.0, **DONE), others)
    fading = map_state(cls=1 - progress(t, 0.3, 0.6), cls_content=1 - progress(t, 0.2, 0.6),
                       top=1 - progress(t, 0.2, 0.5))
    p = progress(t, 0.6, 2.0, ease_in_out_cubic)
    sc = Scene()
    for key in ("tiles", "boxes", "lines", "texts", "pills"):
        getattr(sc, key).extend(base[key] + fading[key])
    sc.box(tuple(lerp(u, v, p) for u, v in zip(CLS, MODEL_BOX)), 1.0, lerp(0.9, 0.6, p),
           lerp(0.16, 0.14, p))
    w = piecewise(WEEKS, t) if t >= WEEKS[0][0] else -1.0
    draw_ops(sc, T0["monitor"] + t, w, panels_a=progress(t, 2.4, 0.9),
             title_a=progress(t, 1.8, 0.6), model_box=False)
    return sc.state(lerp_camera(CAM_MAP, CAM_OPS, p))


if __name__ == "__main__":
    main("anim_33_mlops_monitoring", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
