"""Animation 26c (continues from the end of animation 26b): catching it with two loss curves.

The three maps shrink into thumbnails and the dial they differ by becomes the axis of a chart: one
line for how wrong the model is on the flights it trained on, one for how wrong it is on the twenty
it never saw. The training line only ever falls. The test line falls, bottoms out, and turns back
up - and the point where it turns is the model we actually want. Both curves are the real staged
log loss of the model in animation 26b, one value per tree added.

    python anim_26c_loss_curves.py            # 4K GIF -> output/anim_26c_loss_curves.gif
    python anim_26c_loss_curves.py --preview  # fast 1080p check
"""

import anim_26b_underfit_overfit as previous
from common import INK, MUTED, RED, ease_in_out_cubic, main, progress
from fit_common import (BEST, CHART, FRAME, N_TREES, PANEL_RECTS, SNAPS, SNAP_K, TEST_COL,
                        TEST_LOSS, THUMB_RECTS, TRAIN_COL, TRAIN_LOSS, chart_x, chart_y, curve_label,
                        draw_axes, draw_bands, draw_curve, draw_gap, draw_panel)
from model_common import Scene, fade_state
from split_common import CX, lerp_rect

DURATION = 13.5  # s

END = previous.timeline(previous.DURATION)
TITLE = ("Catching it  ·  training loss vs test loss",
         "Turn the dial one tree at a time and score the model twice after every step")
NOTES = [
    (2.6, 7.3, "Loss = how wrong the model is, including how confident it was.  Lower is better."),
    (7.6, 11.3, "The widening gap is the part the model kept to itself instead of learning"),
    (11.6, None, f"Stop where the test line turns up.  That is early stopping - here, {BEST} trees."),
]
STOP = f"STOP HERE  ·  {BEST} TREES"


def timeline(t):
    sc = Scene()
    sc.title(*TITLE, progress(t, 0.5, 0.5))
    shrink = progress(t, 0.62, 1.1, ease_in_out_cubic)
    bands = progress(t, 8.8, 0.7)

    for j, (rect0, thumb, k) in enumerate(zip(PANEL_RECTS, THUMB_RECTS, SNAP_K)):
        rect = lerp_rect(rect0, thumb, shrink)
        draw_panel(sc, rect, k, 1.0, dots=1 - 0.35 * shrink, axes=0.0)
        name, trees = SNAPS[j][1], SNAPS[j][2]
        sc.text((rect[0] + rect[2]) / 2, rect[3] + 0.45, f"{name}  ·  {trees}", 0.30, INK,
                shrink * progress(t, 1.5, 0.5), True)
        if bands > 0.004:
            x, y = chart_x(k), chart_y(TEST_LOSS[k - 1])
            sc.line((rect[0] + rect[2]) / 2, rect[3] + 0.85, x, y, bands * 0.55, 0.04, True, FRAME)
            sc.tile(TEST_COL, (x - 0.13, y - 0.13, x + 0.13, y + 0.13), bands, 0.13)

    draw_bands(sc, bands * 0.9)
    axes = progress(t, 1.7, 0.5)
    draw_axes(sc, axes, progress(t, 2.0, 0.5))
    draw_gap(sc, N_TREES * progress(t, 7.4, 1.0), progress(t, 7.4, 0.6))
    draw_curve(sc, TRAIN_LOSS, N_TREES * progress(t, 2.3, 2.2), axes, TRAIN_COL)
    draw_curve(sc, TEST_LOSS, N_TREES * progress(t, 4.9, 2.2), axes, TEST_COL, 0.095)
    curve_label(sc, 62, TRAIN_LOSS, "TRAINING LOSS  ·  always falls", progress(t, 4.2, 0.5),
                MUTED)
    curve_label(sc, 62, TEST_LOSS, "TEST LOSS  ·  turns around", progress(t, 6.8, 0.5), INK)

    stop = progress(t, 10.2, 0.6)
    if stop > 0.004:
        x, y = chart_x(BEST), chart_y(TEST_LOSS[BEST - 1])
        sc.line(x, CHART[1] + 0.9, x, CHART[3], stop * 0.8, 0.05, True, RED)
        sc.tile(RED, (x - 0.17, y - 0.17, x + 0.17, y + 0.17), stop, 0.17)
        sc.pill(x + 3.4, y + 1.25, STOP, 0.34, stop, RED, (255, 255, 255))

    for start, end, text in NOTES:
        sc.pill(CX, 13.9, text, 0.36,
                progress(t, start, 0.5) * (1 - (progress(t, end, 0.4) if end else 0)))

    st = sc.state()
    old = fade_state(END, 1 - progress(t, 0.15, 0.45))
    keep = {"tiles", "boxes", "lines", "texts", "pills"}
    for key in keep:
        st[key] = old[key] + st[key]
    return st


if __name__ == "__main__":
    main("anim_26c_loss_curves", DURATION, timeline)
