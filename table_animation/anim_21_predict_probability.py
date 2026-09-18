"""Animation 21 (continues from the end of animation 20): prediction. One by one, the 20 hidden
test flights travel through the trained boosted-tree model and come out as a probability of delay:
a bar per flight, red when it is above the 50% threshold (predict delayed), green below it.

    python anim_21_predict_probability.py            # 4K GIF -> output/anim_21_predict_probability.gif
    python anim_21_predict_probability.py --preview  # fast 1080p check
"""

import math

import anim_20_boosted_trees as trees
from common import INK, clamp01, ease_in_out_cubic, lerp, main, progress
from model_common import (BOX, N_TEST, TEST, TEST_RECT, Scene, draw_data_panel, draw_frame,
                          draw_output_hint, draw_output_row, draw_threshold, draw_trees,
                          output_tile_rect)
from split_common import CX, color

DURATION = 12.6  # s
TITLE = ("Prediction: a probability of delay",
         "The trained model scores the 20 hidden test flights, one at a time")
NOTE = "Above 50%: predict delayed   ·   below 50%: predict on time"
LAUNCH, GAP, TRAVEL = 1.0, 0.36, 1.5
PATH_Y = 11.72


def _path(k, u):
    """Point along test grid -> under the model box -> output row, for u in 0..1."""
    x0, y0, x1, y1 = TEST_RECT[TEST[k]]
    ox0, oy0, ox1, oy1 = output_tile_rect(k)
    pts = [((x0 + x1) / 2, (y0 + y1) / 2), (BOX[0] + 0.3, PATH_Y), (BOX[2] - 0.3, PATH_Y),
           ((ox0 + ox1) / 2, (oy0 + oy1) / 2)]
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    d = ease_in_out_cubic(u) * sum(segs)
    for (a, b), s in zip(zip(pts, pts[1:]), segs):
        if d <= s:
            return lerp(a[0], b[0], d / s), lerp(a[1], b[1], d / s)
        d -= s
    return pts[-1]


def timeline(t):
    sc = Scene()
    sc.title(*trees.TITLE, 1 - progress(t, 0.1, 0.4))
    sc.title(*TITLE, progress(t, 0.45, 0.5))
    moving = {TEST[k] for k in range(N_TEST) if t >= LAUNCH + k * GAP}
    draw_data_panel(sc, 1.0, skip_test=moving)
    draw_frame(sc, 1.0, header=trees.HEADER)
    draw_trees(sc, 1.0, [1.0, 1.0])
    sc.pill(CX, 12.75, trees.NOTE, 0.36, 1 - progress(t, 0.2, 0.4))
    draw_output_hint(sc, 1 - progress(t, 0.3, 0.4))
    draw_threshold(sc, progress(t, 0.8, 0.5))
    for k in range(N_TEST):
        start = LAUNCH + k * GAP
        if t < start:
            continue
        u = clamp01((t - start) / TRAVEL)
        arrived = progress(t, start + TRAVEL - 0.2, 0.3)
        draw_output_row(sc, k, TEST[k], progress(t, start + TRAVEL, 0.5), arrived)
        cx, cy = _path(k, u)
        half = lerp(0.25, 0.17, u)
        sc.tile(color(TEST[k]), (cx - half, cy - half, cx + half, cy + half), 1.0)
    sc.pill(CX, 12.75, NOTE, 0.36, progress(t, LAUNCH + (N_TEST - 1) * GAP + TRAVEL + 0.8, 0.5))
    return sc.state()


if __name__ == "__main__":
    main("anim_21_predict_probability", DURATION, timeline)
