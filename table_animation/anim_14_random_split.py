"""Animation 14 (continues from the end of animation 13): random split. The two bars merge, the
flights shuffle, and the last 20% go to test. By chance only 20% of the test flights are delayed
(43% overall), which sets up the need for a class-aware split.

    python anim_14_random_split.py            # 4K GIF -> output/anim_14_random_split.gif
    python anim_14_random_split.py --preview  # fast 1080p check
"""

from common import main
from split_common import RANDOM, SIMPLE, split_timeline

timeline, DURATION = split_timeline(RANDOM, SIMPLE)

if __name__ == "__main__":
    main("anim_14_random_split", DURATION, timeline)
