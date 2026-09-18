"""Animation 23 (continues from the end of anim_22_confusion_matrix): accuracy. The confusion-matrix
cells it uses light up, its formula appears with the real counts, and its score card slides in.

    python anim_23_accuracy.py            # 4K GIF -> output/anim_23_accuracy.gif
    python anim_23_accuracy.py --preview  # fast 1080p check
"""

import anim_22_confusion_matrix as previous
from common import main
from model_common import METRICS, metric_timeline

TITLE = ("Evaluation  ·  Accuracy", METRICS[0][1])
timeline, DURATION = metric_timeline(0, previous.TITLE, TITLE)

if __name__ == "__main__":
    main("anim_23_accuracy", DURATION, timeline)
