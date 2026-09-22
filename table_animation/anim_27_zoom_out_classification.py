"""Animation 27 (continues from the end of animation 26d): the fixes slide clears, the evaluation
slide comes back up, and then the camera pulls far back; the whole evaluation slide shrinks into a
framed CLASSIFICATION panel ("what we just built") on a new "Types of machine learning problems"
slide with room for the other problem types.

    python anim_27_zoom_out_classification.py            # 4K GIF -> output/anim_27_zoom_out_classification.gif
    python anim_27_zoom_out_classification.py --preview  # fast 1080p check
"""

import anim_26d_fixes as previous
from common import ease_in_out_cubic, lerp_camera, main, progress
from map_common import CAM_MAP, map_state
from model_common import fade_state
from split_common import CAMERA

DURATION = 5.8  # s
END = previous.timeline(previous.DURATION)


def timeline(t):
    camera = lerp_camera(CAMERA, CAM_MAP, progress(t, 1.0, 2.4, ease_in_out_cubic))
    st = map_state(camera=camera, cls_content=progress(t, 0.4, 0.4),
                   top=progress(t, 3.1, 0.6), cls=progress(t, 2.8, 0.7))
    old = fade_state(END, 1 - progress(t, 0.1, 0.35))
    for key in ("tiles", "boxes", "lines", "texts", "pills"):
        st[key] = old[key] + st.get(key, [])
    return st


if __name__ == "__main__":
    main("anim_27_zoom_out_classification", DURATION, timeline)
