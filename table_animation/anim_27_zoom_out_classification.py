"""Animation 27 (continues from the end of animation 26): the camera pulls far back; the whole
evaluation slide shrinks into a framed CLASSIFICATION panel ("what we just built") on a new
"Types of machine learning problems" slide with room for the other problem types.

    python anim_27_zoom_out_classification.py            # 4K GIF -> output/anim_27_zoom_out_classification.gif
    python anim_27_zoom_out_classification.py --preview  # fast 1080p check
"""

import anim_26_f1_score as f1
from common import ease_in_out_cubic, lerp_camera, main, progress
from map_common import CAM_MAP, map_state
from model_common import TITLE as TITLE_POS
from split_common import CAMERA

DURATION = 5.6  # s
END = f1.timeline(f1.DURATION)
OLD_TITLES = [x for x in END["texts"] if x[1] in (TITLE_POS["y"], TITLE_POS["sub"])]


def timeline(t):
    camera = lerp_camera(CAMERA, CAM_MAP, progress(t, 0.8, 2.4, ease_in_out_cubic))
    st = map_state(camera=camera, top=progress(t, 2.9, 0.6), cls=progress(t, 2.6, 0.7))
    fade = 1 - progress(t, 0.2, 0.5)
    st["texts"] += [(*x[:5], x[5] * fade, *x[6:]) for x in OLD_TITLES]
    st["pills"] = [(*x[:4], x[4] * fade) for x in END["pills"]]
    return st


if __name__ == "__main__":
    main("anim_27_zoom_out_classification", DURATION, timeline)
