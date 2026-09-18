"""Animation 11 (continues from the end of animation 10): feature encoding. Wind, visibility and
departures are flagged as already numeric; then, one column at a time, the mapping appears above
the column and its cells roll over to numbers: aircraft model -> code, departure time -> decimal
hour, day -> 0-6, bad weather and the delayed label -> 1/0.

    python anim_11_encode_features.py            # 4K GIF -> output/anim_11_encode_features.gif
    python anim_11_encode_features.py --preview  # fast 1080p check
"""

from anim_10_new_feature import FEATURE_COLS
from common import ENCODE_NOTES, clamp01, main, progress, sample_table_state

DURATION = 13.6  # s
NUMERIC = [("wind", "vis"), ("deps",)]
ENCODE_ORDER = ["model", "sched", "day", "bad", "delayed"]
FIRST, STEP = 2.2, 1.9  # s: first encoded column, gap between columns


def timeline(t):
    a = progress(t, 0.3, 0.4) * (1 - progress(t, 1.6, 0.4))
    notes = [("Already numeric", keys, a) for keys in NUMERIC]
    boxes = [(keys, a) for keys in NUMERIC]
    encode = {}
    for k, key in enumerate(ENCODE_ORDER):
        start = FIRST + k * STEP
        a = progress(t, start, 0.4) * (1 - progress(t, start + 1.5, 0.3))
        notes.append((ENCODE_NOTES[key], (key,), a))
        boxes.append(((key,), a))
        encode[key] = clamp01((t - start - 0.4) / 1.0)
    done = progress(t, FIRST + len(ENCODE_ORDER) * STEP, 0.5)
    return sample_table_state(
        FEATURE_COLS, notes=notes, col_box=boxes, encode=encode,
        caption=("Every feature is now a number, ready for a machine learning model", done),
    )


if __name__ == "__main__":
    main("anim_11_encode_features", DURATION, timeline)
