"""Animation 15 (continues from the end of animation 14): stratified (class-aware) split. The bars
merge, flights group by class, and 20% of each class goes to test, so train and test both keep the
real share of delayed flights.

    python anim_15_stratified_split.py            # 4K GIF -> output/anim_15_stratified_split.gif
    python anim_15_stratified_split.py --preview  # fast 1080p check
"""

from common import main
from split_common import RANDOM, STRATIFIED, split_timeline

timeline, DURATION = split_timeline(STRATIFIED, RANDOM)

if __name__ == "__main__":
    main("anim_15_stratified_split", DURATION, timeline)
