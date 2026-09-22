"""Animation 39 (continues from the end of animation 38): the dataset itself.

The five fact cards squeeze into a strip under the title and a sample of the table builds below
them, column by column and then row by row. Two highlights follow: the same aircraft appearing in
three consecutive months, and the two measured columns (flight cycles and flight hours). 1080p only.
All eight rows are illustrative, the columns and the scale are real.

    python anim_39_dataset_sample.py            # -> output_slides/anim_39_dataset_sample.gif
    python anim_39_dataset_sample.py --preview  # fast check
"""

from common import main, progress
from usecase_common import (CAM_USE, FINAL_NOTE, META_NOTE, META_NOTE_Y, NOTES, NOTE_Y, Scene,
                            draw_highlight, draw_stats, draw_table, draw_title, squeeze_at)

DURATION = 18.0
SQUEEZE_AT = 0.4
HEAD_IN = 1.9
ROW_IN = 3.0
ROWS_HL, MEASURES_HL = 7.0, 11.3
FINAL_IN = 15.4


def timeline(t):
    sc = Scene()
    squeeze = squeeze_at(t, SQUEEZE_AT)
    draw_title(sc, 1.0, meta_a=1 - progress(t, SQUEEZE_AT, 0.5),
               data_a=progress(t, SQUEEZE_AT + 0.7, 0.5))
    draw_stats(sc, squeeze=squeeze)
    sc.pill(50.0, META_NOTE_Y, META_NOTE, 1.3, 1 - progress(t, SQUEEZE_AT, 0.4))
    head = [progress(t, HEAD_IN + 0.11 * j, 0.45) for j in range(8)]
    rows = [progress(t, ROW_IN + 0.3 * k, 0.45) for k in range(9)]
    draw_table(sc, label_a=progress(t, HEAD_IN - 0.4, 0.5), head_a=head, rows_a=rows)
    rows_hl = progress(t, ROWS_HL, 0.5) * (1 - progress(t, ROWS_HL + 3.4, 0.5))
    meas_hl = progress(t, MEASURES_HL, 0.5) * (1 - progress(t, MEASURES_HL + 3.4, 0.5))
    draw_highlight(sc, "rows", rows_hl)
    draw_highlight(sc, "measures", meas_hl)
    sc.pill(50.0, NOTE_Y, NOTES["rows"], 1.15, rows_hl)
    sc.pill(50.0, NOTE_Y, NOTES["measures"], 1.15, meas_hl)
    sc.pill(50.0, NOTE_Y, FINAL_NOTE, 1.3, progress(t, FINAL_IN, 0.6), (221, 83, 88),
            (255, 255, 255))
    return sc.state(CAM_USE)


if __name__ == "__main__":
    main("anim_39_dataset_sample", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
