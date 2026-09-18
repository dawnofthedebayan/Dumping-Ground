"""Animation 10 (continues from the end of animation 9): wind speed and visibility are outlined,
the formula for a new feature appears above them, and a BAD WEATHER column opens next to them,
filled row by row: True when wind > 25 kt or visibility < 3 km.

    python anim_10_new_feature.py            # 4K GIF -> output/anim_10_new_feature.gif
    python anim_10_new_feature.py --preview  # fast 1080p check
"""

from anim_9_drop_irrelevant import KEPT_COLS
from common import BAD_VIS, THRESHOLD, clamp01, main, progress, sample_table_state

DURATION = 5.6  # s
SOURCES = ("wind", "vis", "bad")
FORMULA = f"BAD WEATHER  =  wind > {THRESHOLD:g} kt   OR   visibility < {BAD_VIS:g} km"
FEATURE_COLS = dict(KEPT_COLS, bad=1.0)  # end state


def timeline(t):
    label = progress(t, 0.3, 0.5) * (1 - progress(t, 3.9, 0.4))
    return sample_table_state(
        dict(KEPT_COLS, bad=clamp01((t - 1.2) / 1.6)),
        col_box=[(SOURCES, label)],
        notes=[(FORMULA, SOURCES, label)],
    )


if __name__ == "__main__":
    main("anim_10_new_feature", DURATION, timeline)
