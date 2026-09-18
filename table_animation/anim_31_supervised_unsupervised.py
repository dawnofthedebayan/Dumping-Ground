"""Animation 31 (continues from the end of animation 30): brackets grow over the panels: SUPERVISED
LEARNING (we have labels) spans classification and regression (with forecasting), UNSUPERVISED
(no labels) spans clustering.

    python anim_31_supervised_unsupervised.py            # 4K GIF -> output/anim_31_supervised_unsupervised.gif
    python anim_31_supervised_unsupervised.py --preview  # fast 1080p check
"""

from common import ease_in_out_cubic, main, progress
from map_common import map_state

DURATION = 5.0  # s


def timeline(t):
    return map_state(reg=(1, 1, 1, 1), fc=(1, 1, 1, 1), clu=(1, 1, 1),
                     groups=(progress(t, 0.3, 1.0, ease_in_out_cubic),
                             progress(t, 1.5, 1.0, ease_in_out_cubic)))


if __name__ == "__main__":
    main("anim_31_supervised_unsupervised", DURATION, timeline)
