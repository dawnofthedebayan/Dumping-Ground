"""Animation 29 (continues from the end of animation 28): FORECASTING hangs off regression as a
special case of it: a weekly delay series draws in, then continues into the future as a dashed
forecast with a widening uncertainty band.

    python anim_29_forecasting.py            # 4K GIF -> output/anim_29_forecasting.gif
    python anim_29_forecasting.py --preview  # fast 1080p check
"""

from common import clamp01, main, progress
from map_common import map_state

DURATION = 6.8  # s


def timeline(t):
    return map_state(reg=(1, 1, 1, 1),
                     fc=(progress(t, 0.3, 0.6), progress(t, 0.8, 0.6),
                         progress(t, 1.3, 2.0, clamp01), progress(t, 3.5, 1.4, clamp01)))


if __name__ == "__main__":
    main("anim_29_forecasting", DURATION, timeline)
