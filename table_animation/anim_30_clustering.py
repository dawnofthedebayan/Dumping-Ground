"""Animation 30 (continues from the end of animation 29): a CLUSTERING panel: grey, unlabelled
points pop in, then the algorithm finds three natural groups and colours them, with a soft ring
around each group.

    python anim_30_clustering.py            # 4K GIF -> output/anim_30_clustering.gif
    python anim_30_clustering.py --preview  # fast 1080p check
"""

from common import clamp01, ease_in_out_cubic, main, progress
from map_common import map_state

DURATION = 6.2  # s


def timeline(t):
    return map_state(reg=(1, 1, 1, 1), fc=(1, 1, 1, 1),
                     clu=(progress(t, 0.3, 0.6), progress(t, 0.9, 1.4, clamp01),
                          progress(t, 2.9, 1.2, ease_in_out_cubic)))


if __name__ == "__main__":
    main("anim_30_clustering", DURATION, timeline)
