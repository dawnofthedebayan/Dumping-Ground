"""Animation 17 (continues from the end of animation 16): 5-fold cross-validation. The bars merge
and shuffle, the bar becomes fold 1 and four copies drop below it; in each fold a different 20%
block is the test set (full colour, outlined) and the rest is training (faded).

    python anim_17_kfold_cross_validation.py            # 4K GIF -> output/anim_17_kfold_cross_validation.gif
    python anim_17_kfold_cross_validation.py --preview  # fast 1080p check
"""

from common import INK, N_ROWS, ease_in_out_cubic, main, progress
from split_common import (CHRONO, CX, FULL_X0, NOTE_Y, RANDOM_ORDER, TILE_R, BarView, bar_state,
                          color, fade_between, lerp_rect, regroup_rect, slot_x, tile_rect)

K, FOLD = 5, N_ROWS // 5
ROWS_TOP, ROW_H, ROW_STEP = 3.4, 1.0, 1.55
KFOLD = BarView(RANDOM_ORDER, "K-fold cross-validation  (k = 5)",
                "Rotate which 20% is the test set, training on the other 80% each time")
KFOLD.overlays = lambda a: ([], [], [])
TIMES = {"merge": 0.3, "reorder": 1.7}
FOLD_T = 4.3                                  # bar squashes into fold 1
ROW_T = [5.1 + 0.7 * k for k in range(K)]     # fold k appears (fold 1 is already there)
NOTE_T = ROW_T[-1] + 1.0
DURATION = NOTE_T + 3.0


def fold_rect(k, slot):
    x0, _, x1, _ = tile_rect(slot_x(slot))
    y = ROWS_TOP + k * ROW_STEP
    return (x0, y, x1, y + ROW_H)


def timeline(t):
    texts, pills, lines = fade_between(CHRONO, KFOLD, t)
    squash = progress(t, FOLD_T, 0.8, ease_in_out_cubic)
    tiles = []
    for k in range(K):
        show = 1.0 if k == 0 else progress(t, ROW_T[k] - 0.4, 0.6, ease_in_out_cubic)
        mark = progress(t, ROW_T[k], 0.4)  # this fold's test block lights up
        if show <= 0:
            continue
        for i in RANDOM_ORDER:
            slot = KFOLD.slot[i]
            if k == 0:
                r, dy = regroup_rect(i, t, CHRONO, KFOLD, TIMES)
                r = lerp_rect(r, fold_rect(0, slot), squash)
                r = (r[0], r[1] + dy, r[2], r[3] + dy)
            else:
                r = lerp_rect(fold_rect(0, slot), fold_rect(k, slot), show)
            in_test = k * FOLD <= slot < (k + 1) * FOLD
            alpha = show * (1 - (0 if in_test else 0.7 * mark))
            tiles.append((color(i), *r, TILE_R, alpha))
        y0, y1 = ROWS_TOP + k * ROW_STEP - 0.15, ROWS_TOP + k * ROW_STEP + ROW_H + 0.15
        x0, x1 = slot_x(k * FOLD) - 0.04, slot_x((k + 1) * FOLD) + 0.04
        for a, b, c, d in [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]:
            lines.append((a, b, c, d, 0.07, mark, False))
        texts.append((FULL_X0 - 0.35, (y0 + y1) / 2, f"Fold {k + 1}", 0.34, INK, mark, True, "rm"))
    head = progress(t, ROW_T[0], 0.4)
    texts.append(((slot_x(0) + slot_x(FOLD)) / 2, ROWS_TOP - 0.55, "TEST", 0.34, INK, head, True,
                  "mm"))
    texts.append(((slot_x(FOLD) + slot_x(N_ROWS)) / 2, ROWS_TOP - 0.55, "TRAIN", 0.34, INK, head,
                  True, "mm"))
    pills.append((CX, NOTE_Y + 0.6, "Every flight is tested exactly once: average the 5 scores "
                  "for a more reliable estimate", 0.4, progress(t, NOTE_T, 0.5)))
    return bar_state(tiles, texts, pills, lines)


if __name__ == "__main__":
    main("anim_17_kfold_cross_validation", DURATION, timeline)
