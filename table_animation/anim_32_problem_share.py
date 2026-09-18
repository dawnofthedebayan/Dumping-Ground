"""Animation 32 (continues from the end of animation 31): a bar across the bottom fills to show
that more than 90% of the ML problems the company will face are supervised (classification and
regression), and the remaining sliver under 10% is clustering and other unsupervised work.

    python anim_32_problem_share.py            # 4K GIF -> output/anim_32_problem_share.gif
    python anim_32_problem_share.py --preview  # fast 1080p check
"""

from common import ease_in_out_cubic, main, progress
from map_common import map_state

DURATION = 6.6  # s


def timeline(t):
    return map_state(reg=(1, 1, 1, 1), fc=(1, 1, 1, 1), clu=(1, 1, 1), groups=(1, 1),
                     share=(progress(t, 0.3, 0.6), progress(t, 0.9, 2.0, ease_in_out_cubic),
                            progress(t, 3.1, 0.8, ease_in_out_cubic)))


if __name__ == "__main__":
    main("anim_32_problem_share", DURATION, timeline)
