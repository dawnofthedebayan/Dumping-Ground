"""Animation 5: a dashed decision boundary rises from the axis at 25 kt, the rule appears above it,
and the chart splits into a green "predict False" side and a red "predict True" side.

    python anim_5_decision_boundary.py            # 4K GIF -> output/anim_5_decision_boundary.gif
    python anim_5_decision_boundary.py --preview  # fast 1080p check
"""

from common import chart_state, ease_in_out_cubic, main, progress

DURATION = 5.0  # s


def timeline(t):
    return chart_state(
        boundary=progress(t, 0.3, 0.9, ease_in_out_cubic),
        rule=progress(t, 1.0, 0.5),
        region=progress(t, 1.3, 0.9, ease_in_out_cubic),
        region_label=progress(t, 2.0, 0.5),
    )


if __name__ == "__main__":
    main("anim_5_decision_boundary", DURATION, timeline)
