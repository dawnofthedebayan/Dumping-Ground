"""Animation 16 (continues from the end of animation 15): chronological split. The bars merge, the
flights sort by departure date along a Jan-Dec axis, and the most recent 20% become the test set:
train on the past, test on the future.

    python anim_16_chronological_split.py            # 4K GIF -> output/anim_16_chronological_split.gif
    python anim_16_chronological_split.py --preview  # fast 1080p check
"""

from common import INK, MUTED, N_ROWS, main, progress
from split_common import (BAR_BOT, CHRONO, CHRONO_ORDER, CX, DATES, STRATIFIED, slot_x,
                          split_timeline)


def date_axis(t, times):
    a = progress(t, times["reorder"] + 1.8, 0.5) * (1 - progress(t, times["split"], 0.4))
    if a <= 0:
        return [], []
    y = BAR_BOT + 0.35
    lines = [(slot_x(0), y, slot_x(N_ROWS), y, 0.05, a, False)]
    texts = [(CX, y + 1.45, "DEPARTURE DATE (2025)", 0.32, INK, a, True, "mm")]
    months = [DATES[i] for i in CHRONO_ORDER]
    start = 0
    for k in range(1, N_ROWS + 1):
        if k == N_ROWS or months[k].month != months[start].month:
            x0, x1 = slot_x(start), slot_x(k)
            lines.append((x0, y, x0, y + 0.25, 0.05, a, False))
            if k - start >= 4:  # label months wide enough to fit the name
                texts.append(((x0 + x1) / 2, y + 0.75, f"{months[start]:%b}", 0.3, MUTED, a,
                              False, "mm"))
            start = k
    return texts, lines


timeline, DURATION = split_timeline(CHRONO, STRATIFIED, extras=date_axis, extras_time=1.6)

if __name__ == "__main__":
    main("anim_16_chronological_split", DURATION, timeline)
