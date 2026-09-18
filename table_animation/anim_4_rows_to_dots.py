"""Animation 4 (continues from the end of animation 2): every table row shrinks into a red/green dot
and arcs down onto a wind-speed axis, lowest wind first, forming a dot plot.

    python anim_4_rows_to_dots.py            # 4K GIF -> output/anim_4_rows_to_dots.gif
    python anim_4_rows_to_dots.py --preview  # fast 1080p check
"""

from common import (CAM_100, N_ROWS, PANELS, X_ORDER, ease_in_out_cubic, main, progress)

DURATION = 5.6  # s
RANK = {i: k for k, i in enumerate(X_ORDER)}


def timeline(t):
    headers = 1 - progress(t, 0.4, 0.5)
    return dict(
        camera=CAM_100,
        header_alpha=[headers] * PANELS,
        row_alpha=[1.0] * N_ROWS,
        shrink=[progress(t, 0.5 + 0.006 * i, 0.6, ease_in_out_cubic) for i in range(N_ROWS)],
        fly=[progress(t, 1.7 + 0.012 * RANK[i], 1.0, ease_in_out_cubic) for i in range(N_ROWS)],
        axis=progress(t, 1.0, 1.0, ease_in_out_cubic),
        axis_title=progress(t, 1.7, 0.5),
        legend=progress(t, 3.6, 0.5),
    )


if __name__ == "__main__":
    main("anim_4_rows_to_dots", DURATION, timeline)
