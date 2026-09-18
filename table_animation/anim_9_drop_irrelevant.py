"""Animation 9 (continues from the end of animation 8): livery color and magazine issue are
outlined, greyed out and labelled as unrelated to delays, then both columns collapse away.

    python anim_9_drop_irrelevant.py            # 4K GIF -> output/anim_9_drop_irrelevant.gif
    python anim_9_drop_irrelevant.py --preview  # fast 1080p check
"""

from anim_8_add_columns import ALL_COLS
from common import clamp01, main, progress, sample_table_state

DURATION = 5.4  # s
DROP = ("livery", "magazine")
KEPT_COLS = {k: v for k, v in ALL_COLS.items() if k not in DROP}  # end state


def timeline(t):
    mark = progress(t, 0.3, 0.5)
    label = mark * (1 - progress(t, 2.4, 0.4))
    cols = dict(ALL_COLS, livery=1 - clamp01((t - 2.6) / 1.3),
                magazine=1 - clamp01((t - 2.8) / 1.3))
    return sample_table_state(
        cols,
        col_dim={key: mark for key in DROP},
        col_box=[(DROP, label)],
        notes=[("Not related to delays: drop them", DROP, label)],
    )


if __name__ == "__main__":
    main("anim_9_drop_irrelevant", DURATION, timeline)
