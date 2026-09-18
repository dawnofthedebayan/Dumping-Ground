"""Animation 13 (continues from the end of animation 12): the 80 : 20 idea. A divider cuts the bar
at 80%, the last 20 flights lift out and slide right into a separate TEST bar.

    python anim_13_split_80_20.py            # 4K GIF -> output/anim_13_split_80_20.gif
    python anim_13_split_80_20.py --preview  # fast 1080p check
"""

from common import main
from split_common import DATASET, SIMPLE, split_timeline

timeline, DURATION = split_timeline(SIMPLE, DATASET, reorder=False)

if __name__ == "__main__":
    main("anim_13_split_80_20", DURATION, timeline)
