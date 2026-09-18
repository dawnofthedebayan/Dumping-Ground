"""Animation 8 (continues from the end of animation 7): new feature columns slide open one at a
time in the sample-of-10 table: visibility, scheduled departure, day of week, departures in the
same hour, aircraft model, and two columns that have nothing to do with delays (livery color,
in-flight magazine issue). The camera eases out to keep the widening table in frame.

    python anim_8_add_columns.py            # 4K GIF -> output/anim_8_add_columns.gif
    python anim_8_add_columns.py --preview  # fast 1080p check
"""

from common import clamp01, main, sample_table_state

DURATION = 8.4  # s
ADD_ORDER = ["vis", "sched", "day", "deps", "model", "livery", "magazine"]
START, STEP, OPEN = 0.5, 0.75, 1.3  # s: first column, gap between columns, time to fully open
ALL_COLS = {key: 1.0 for key in ADD_ORDER}  # end state


def timeline(t):
    return sample_table_state({key: clamp01((t - START - k * STEP) / OPEN)
                               for k, key in enumerate(ADD_ORDER)})


if __name__ == "__main__":
    main("anim_8_add_columns", DURATION, timeline)
