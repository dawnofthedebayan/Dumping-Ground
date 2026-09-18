"""Animation 7 (continues from the end of animation 6): the rule, score and chart clear away, every
dot arcs back to its row and grows into the 100-row table again, then the camera pushes back in
on the sample of 10 (the same move as animation 3).

    python anim_7_back_to_table.py            # 4K GIF -> output/anim_7_back_to_table.gif
    python anim_7_back_to_table.py --preview  # fast 1080p check
"""

import anim_3_zoom_in_10 as zoom_in
from common import (N_ROWS, PANELS, chart_state, ease_in_out_cubic, main, progress)

DURATION = 8.8  # s
TABLE_DONE = 4.4  # s: the 100-row table is fully rebuilt; zoom_in's timeline takes over


def fade(t, start, dur=0.5):
    return 1 - progress(t, start, dur)


def timeline(t):
    if t >= TABLE_DONE:
        return zoom_in.timeline(t - TABLE_DONE)
    headers = progress(t, 3.8, 0.5)
    return chart_state(
        verdict=[1.0] * N_ROWS,
        marks=fade(t, 0.3),
        score=fade(t, 0.3), final=fade(t, 0.3), rule=fade(t, 0.4), region_label=fade(t, 0.4),
        legend=fade(t, 0.5),
        region=1 - progress(t, 0.5, 0.7, ease_in_out_cubic),
        boundary=1 - progress(t, 0.6, 0.7, ease_in_out_cubic),
        fly=[1 - progress(t, 1.2 + 0.012 * i, 1.0, ease_in_out_cubic) for i in range(N_ROWS)],
        axis=1 - progress(t, 2.6, 0.8, ease_in_out_cubic),
        axis_title=fade(t, 2.6, 0.4),
        shrink=[1 - progress(t, 3.2 + 0.006 * i, 0.6, ease_in_out_cubic) for i in range(N_ROWS)],
        header_alpha=[headers] * PANELS,
    )


if __name__ == "__main__":
    main("anim_7_back_to_table", DURATION, timeline)
