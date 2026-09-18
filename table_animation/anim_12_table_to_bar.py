"""Animation 12 (continues from the end of animation 11): the encoded table's text fades, each of
the 10 rows squeezes into a thin tile at the left of a bar, and the other 90 flights grow in beside
them: one tile per flight, red = delayed, green = on time.

    python anim_12_table_to_bar.py            # 4K GIF -> output/anim_12_table_to_bar.gif
    python anim_12_table_to_bar.py --preview  # fast 1080p check
"""

import anim_11_encode_features as encoded
from common import (HEADER_H, INSET, N_ROWS, N_SAMPLE, RADIUS, ROW_FILL, ease_in_out_cubic, lerp,
                    main, progress, table_width)
from split_common import (CAMERA, DATASET, TILE_R, color, lerp_rect, title_items)

DURATION = 5.5  # s
BASE = encoded.timeline(encoded.DURATION)  # final encoded table
PW = table_width(BASE["cols"])


def row_rect(r):
    top = HEADER_H + r + (1 - ROW_FILL) / 2
    return (INSET, top, PW - INSET, top + ROW_FILL)


def timeline(t):
    s = dict(BASE, camera=CAMERA)
    s["caption"] = (BASE["caption"][0], 1 - progress(t, 0.3, 0.4))
    s["row_text"] = 1 - progress(t, 0.3, 0.5)
    s["header_alpha"] = [1 - progress(t, 0.6, 0.4)] + [0.0] * 3
    tiles = []
    if t >= 1.0:  # rows are text-free now: hand them over to tiles at the identical rect
        s["row_alpha"] = [0.0] * N_ROWS
        for i in range(N_SAMPLE):
            p = progress(t, 1.0 + 0.07 * i, 1.0, ease_in_out_cubic)
            tiles.append((color(i), *lerp_rect(row_rect(i), DATASET.full_rect(i), p),
                          lerp(RADIUS, TILE_R, p), 1.0))
    for i in range(N_SAMPLE, N_ROWS):
        p = progress(t, 2.0 + 0.012 * (i - N_SAMPLE), 0.5)
        x0, y0, x1, y1 = DATASET.full_rect(i)
        tiles.append((color(i), x0, y1 - (y1 - y0) * p, x1, y1, TILE_R, p))
    texts, _, _ = DATASET.overlays(progress(t, 3.8, 0.5))
    s.update(tiles=tiles, texts=title_items(DATASET, progress(t, 3.4, 0.5)) + texts)
    return s


if __name__ == "__main__":
    main("anim_12_table_to_bar", DURATION, timeline)
