"""Animation 28 (continues from the end of animation 27): a REGRESSION panel appears beside
classification: axes draw, points pop in and a best-fit line sweeps across, predicting a number
(minutes late) instead of a category.

    python anim_28_regression.py            # 4K GIF -> output/anim_28_regression.gif
    python anim_28_regression.py --preview  # fast 1080p check
"""

from common import clamp01, ease_in_out_cubic, main, progress
from map_common import map_state

DURATION = 6.2  # s


def timeline(t):
    return map_state(reg=(progress(t, 0.3, 0.6), progress(t, 0.9, 0.6),
                          progress(t, 1.3, 1.6, clamp01), progress(t, 3.1, 1.2, ease_in_out_cubic)))


if __name__ == "__main__":
    main("anim_28_regression", DURATION, timeline)
