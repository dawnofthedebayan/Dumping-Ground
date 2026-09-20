"""Animation 44 (continues from the end of animation 43): WAPE, the score.

The grid of aircraft clears and a card builds the metric exactly the way the evaluation script
does it: the error as a share of what really flew; then, for one calendar month, that ratio summed
over all aircraft - once for flight cycles, once for flight hours, and averaged; then the twelve
monthly scores averaged into the final number, with a plain-words reading of what the percentage
means. 1080p only; the fleet figures are illustrative.

    python anim_44_wape.py            # -> output_slides/anim_44_wape.gif
    python anim_44_wape.py --preview  # fast check
"""

from common import main, progress
from map_common import SHARE_RED
from usecase_common import (CAM_USE, GOAL_Y, MINI_N, MINI_NOTE, Scene, WAPE_NOTE, draw_minis,
                            draw_stats, draw_title, draw_wape)

DURATION = 19.0
CARD_IN = 1.5
STEPS = [2.4, 5.0, 9.0]
MONTHS_IN, PLAIN_IN, NOTE_IN = 10.0, 13.6, 15.4
WHITE = (255, 255, 255)


def timeline(t):
    sc = Scene()
    draw_title(sc, 1.0, meta_a=0.0, goal_a=1.0)
    draw_stats(sc, squeeze=1.0)
    draw_minis(sc, 1 - progress(t, 0.4, 0.9), [1.0] * MINI_N, more_a=1.0)
    sc.pill(50.0, GOAL_Y, MINI_NOTE, 1.3, 1 - progress(t, 0.2, 0.4))
    draw_wape(sc, progress(t, CARD_IN, 0.6), lines=[progress(t, s, 0.6) for s in STEPS],
              months=progress(t, MONTHS_IN, 2.2), plain=progress(t, PLAIN_IN, 0.6))
    sc.pill(50.0, GOAL_Y, WAPE_NOTE, 1.35, progress(t, NOTE_IN, 0.6), SHARE_RED, WHITE)
    return sc.state(CAM_USE)


if __name__ == "__main__":
    main("anim_44_wape", DURATION, timeline, default_size="1920x1080", default_out="output_slides")
