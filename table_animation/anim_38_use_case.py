"""Animation 38 (a new slide, independent of the delay story): the use case.

Five cards with line-art icons lay out the shape of the dataset: 14,000 aircraft, eleven years of
months, more than 1.2 million rows, 860 operators, and the two things measured for every aircraft
in every month - flight cycles and flight hours. Animation 39 carries on from its last frame with
a sample of the table itself. 1080p only.

    python anim_38_use_case.py            # 1080p GIF -> output_slides/anim_38_use_case.gif
    python anim_38_use_case.py --preview  # fast check
"""

from common import ease_out_cubic, main, progress
from usecase_common import CAM_USE, META_NOTE, META_NOTE_Y, Scene, draw_stats, draw_title

DURATION = 11.0
CARD_IN = [1.0, 2.0, 3.0, 4.0, 5.6]  # when each card arrives
NOTE_IN = 7.4


def timeline(t):
    sc = Scene()
    draw_title(sc, 1.0, meta_a=progress(t, 0.2, 0.6))
    appear = [progress(t, s, 0.5) for s in CARD_IN]
    rise = [(1 - progress(t, s, 0.6, ease_out_cubic)) * 1.4 for s in CARD_IN]
    counts = [progress(t, s + 0.15, 1.1) for s in CARD_IN]
    draw_stats(sc, appear, counts, rise)
    sc.pill(50.0, META_NOTE_Y, META_NOTE, 1.3, progress(t, NOTE_IN, 0.6))
    return sc.state(CAM_USE)


if __name__ == "__main__":
    main("anim_38_use_case", DURATION, timeline, default_size="1920x1080",
         default_out="output_slides")
