#!/usr/bin/env bash
# Render all 4K GIFs into ./output. Extra args (e.g. --preview, --fps 50) are passed through.
set -euo pipefail
cd "$(dirname "$0")"
for script in anim_1_sample_10.py anim_2_zoom_out_100.py anim_3_zoom_in_10.py \
              anim_4_rows_to_dots.py anim_5_decision_boundary.py anim_6_apply_rule.py \
              anim_7_back_to_table.py anim_8_add_columns.py \
              anim_9_drop_irrelevant.py anim_10_new_feature.py anim_11_encode_features.py \
              anim_12_table_to_bar.py anim_13_split_80_20.py anim_14_random_split.py \
              anim_15_stratified_split.py anim_16_chronological_split.py \
              anim_17_kfold_cross_validation.py anim_18_training_setup.py \
              anim_19_logistic_regression.py anim_20_boosted_trees.py \
              anim_21_predict_probability.py anim_22_confusion_matrix.py anim_23_accuracy.py \
              anim_24_precision.py anim_25_recall.py anim_26_f1_score.py \
              anim_27_zoom_out_classification.py anim_28_regression.py anim_29_forecasting.py \
              anim_30_clustering.py anim_31_supervised_unsupervised.py anim_32_problem_share.py; do
  python3 "$script" "$@"
done
