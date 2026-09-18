"""Animation 6: the rule is checked against every aircraft from left to right. Each dot pops with a
tick (rule was right) or a cross and ring (rule was wrong) while the tally counts up, ending on the
rule's accuracy: 60 / 100.

    python anim_6_apply_rule.py            # 4K GIF -> output/anim_6_apply_rule.gif
    python anim_6_apply_rule.py --preview  # fast 1080p check
"""

from common import N_ROWS, X_ORDER, chart_state, clamp01, main, progress

DURATION = 7.6  # s
RANK = {i: k for k, i in enumerate(X_ORDER)}


def timeline(t):
    return chart_state(
        boundary=1.0, rule=1.0, region=1.0, region_label=1.0,
        score=progress(t, 0.3, 0.4),
        verdict=[progress(t, 0.7 + 0.035 * RANK[i], 0.4, clamp01) for i in range(N_ROWS)],
        final=progress(t, 4.8, 0.7, clamp01),
    )


if __name__ == "__main__":
    main("anim_6_apply_rule", DURATION, timeline)
