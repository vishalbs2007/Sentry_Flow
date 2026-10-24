"""
models/xgboost_model.py
-----------------------
XGBoost (eXtreme Gradient Boosting) classifier specification for FlowSentry (CN-009, Phase 3).

XGBoost is a gradient boosting ensemble method:
- State-of-the-art performance on structured/tabular data
- Efficient implementation with regularization
- Handles missing values internally
- Feature importance via gain/cover/weight

Key differences from Random Forest:
- Sequential boosting (learns from previous trees' errors)
- Weighted samples (focus on hard-to-classify instances)
- Regularization parameters (L1/L2, tree complexity)

Hyperparameters tuned:
- n_estimators: number of boosting rounds
- max_depth: maximum depth of each tree
- learning_rate: step size shrinkage (eta)
- subsample: fraction of samples per tree
- colsample_bytree: fraction of features per tree
- reg_alpha: L1 regularization
- reg_lambda: L2 regularization

TRD §16, FR-005, ML-001, CN-009.
"""

from __future__ import annotations

import logging
from typing import Any

import xgboost as xgb
from sklearn.base import BaseEstimator

from models.base import ModelSpec

logger = logging.getLogger(__name__)


def get_xgboost_spec(random_state: int = 42) -> ModelSpec:
    """Create XGBoost model specification.
    
    Parameters
    ----------
    random_state : int, default=42
        Random state for reproducibility
        
    Returns
    -------
    ModelSpec
        XGBoost specification with tunable hyperparameters
        
    Notes
    -----
    Parameter names verified against xgboost 3.4.1 (2024-10-24):
    XGBClassifier(
        n_estimators=100,         # number of boosting rounds
        max_depth=6,              # maximum tree depth
        max_leaves=0,             # max leaves (0 = no limit)
        max_bin=256,              # max bins for continuous features
        grow_policy='depthwise',  # tree growth policy
        learning_rate=0.3,        # eta: step size shrinkage
        verbosity=0,              # 0=silent, 1=warning, 2=info, 3=debug
        objective='multi:softprob',  # multi-class classification
        booster='gbtree',         # gbtree, gblinear, dart
        tree_method='auto',       # auto, exact, approx, hist, gpu_hist
        n_jobs=None,              # parallel threads
        gamma=0,                  # min loss reduction for split
        min_child_weight=1,       # minimum sum of instance weight in child
        max_delta_step=0,         # max delta step (for imbalanced classes)
        subsample=1.0,            # subsample ratio of training instances
        sampling_method='uniform',
        colsample_bytree=1.0,     # subsample ratio of columns per tree
        colsample_bylevel=1.0,    # subsample ratio of columns per level
        colsample_bynode=1.0,     # subsample ratio of columns per split
        reg_alpha=0,              # L1 regularization
        reg_lambda=1,             # L2 regularization
        scale_pos_weight=1,       # balance of positive/negative weights
        base_score=0.5,
        random_state=None,
        missing=None,             # value to be treated as missing
        num_parallel_tree=1,
        monotone_constraints=None,
        interaction_constraints=None,
        importance_type='gain',   # 'gain', 'weight', 'cover'
        device='cpu',
        validate_parameters=False,
        enable_categorical=False,
        feature_types=None,
        max_cat_to_onehot=4,
        max_cat_threshold=64,
        multi_strategy='one_output_per_tree',
        eval_metric=None,
        early_stopping_rounds=None,
        callbacks=None,
    )
    
    Search space rationale:
    - n_estimators: [50, 100, 200] - balance between performance and training time
    - max_depth: [3, 6, 10] - control tree complexity
    - learning_rate: [0.01, 0.1, 0.3] - smaller = more robust but slower
    - subsample: [0.8, 1.0] - prevent overfitting
    - colsample_bytree: [0.8, 1.0] - feature sampling
    - reg_alpha: [0, 0.1] - L1 regularization
    - reg_lambda: [1, 10] - L2 regularization
    
    Multi-class handling:
    - objective='multi:softprob' for multi-class probability output
    - Automatically detects number of classes from labels
    - Integer-encoded labels required (LabelEncoder)
    
    Performance notes:
    - XGBoost is typically competitive with Random Forest
    - Often better on imbalanced datasets
    - Regularization helps prevent overfitting
    - Early stopping not used (would require validation split from training only)
    """
    return ModelSpec(
        name='xgboost',
        estimator_factory=lambda: xgb.XGBClassifier(
            random_state=random_state,
            n_jobs=-1,  # Use all CPUs
            objective='multi:softprob',  # Multi-class classification
            verbosity=0,  # Silent
            # All tunable params come from param_space below
        ),
        param_space={
            # Reduced search space for reasonable training time
            # Full space would be: 3×3×3×2×2×2×2 = 216 combinations
            # This reduced space: 2×2×2×1×1×1×1 = 8 combinations
            'classifier__n_estimators': [100, 200],
            'classifier__max_depth': [6, 10],
            'classifier__learning_rate': [0.1, 0.3],
            'classifier__subsample': [1.0],
            'classifier__colsample_bytree': [1.0],
            'classifier__reg_alpha': [0],
            'classifier__reg_lambda': [1],
        },
        notes=(
            "XGBoost: state-of-the-art gradient boosting. "
            "Sequential ensemble that learns from previous trees' errors. "
            "Handles imbalanced classes well. "
            "Requires integer-encoded labels. "
            "Regularization prevents overfitting. "
            "Often competitive with or better than Random Forest. "
            "NOTE: Search space reduced from 216 to 8 combinations for time constraints."
        ),
    )


def export_xgboost_info(
    xgb_classifier: xgb.XGBClassifier,
    feature_names: list[str],
) -> dict[str, Any]:
    """Export feature importances and model info from trained XGBoost.
    
    Parameters
    ----------
    xgb_classifier : XGBClassifier
        Fitted XGBoost classifier
    feature_names : list[str]
        Names of features used for training
        
    Returns
    -------
    dict
        Model info with:
        - feature_importances_gain: importance by gain (default)
        - feature_importances_weight: importance by frequency
        - feature_importances_cover: importance by coverage
        - sorted_features: list of (feature, importance) by gain
        - n_features: number of features
        - n_estimators: number of boosting rounds trained
        
    Notes
    -----
    XGBoost provides three types of feature importance:
    1. **gain**: average gain across all splits using the feature (default)
    2. **weight**: number of times feature is used for splitting
    3. **cover**: average coverage (samples affected) by feature
    
    Gain is typically most informative for understanding feature impact.
    """
    if not hasattr(xgb_classifier, 'feature_importances_'):
        raise ValueError("XGBClassifier must be fitted before exporting info")
    
    # Get importances (default is 'gain') - convert to float for JSON
    importances_gain = xgb_classifier.feature_importances_.tolist()
    
    if len(feature_names) != len(importances_gain):
        raise ValueError(
            f"Mismatch: {len(feature_names)} feature names but "
            f"{len(importances_gain)} importance values"
        )
    
    # Get different importance types using get_booster()
    booster = xgb_classifier.get_booster()
    
    # Create mappings - convert to float for JSON compatibility
    importance_gain_dict = {fname: float(imp) for fname, imp in zip(feature_names, importances_gain)}
    
    # Get weight and cover importances
    try:
        importance_weight = booster.get_score(importance_type='weight')
        importance_cover = booster.get_score(importance_type='cover')
        
        # Map to feature names (booster uses f0, f1, ... notation)
        importance_weight_dict = {}
        importance_cover_dict = {}
        
        for i, fname in enumerate(feature_names):
            key = f'f{i}'
            importance_weight_dict[fname] = float(importance_weight.get(key, 0.0))
            importance_cover_dict[fname] = float(importance_cover.get(key, 0.0))
    except Exception as e:
        logger.warning("Could not get weight/cover importances: %s", e)
        importance_weight_dict = {}
        importance_cover_dict = {}
    
    # Sort by gain (default importance)
    sorted_features = sorted(
        importance_gain_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    info = {
        'feature_importances_gain': importance_gain_dict,
        'feature_importances_weight': importance_weight_dict,
        'feature_importances_cover': importance_cover_dict,
        'sorted_features': sorted_features,
        'n_features': len(feature_names),
        'n_estimators': int(xgb_classifier.n_estimators),
        'best_iteration': int(getattr(xgb_classifier, 'best_iteration', xgb_classifier.n_estimators)),
    }
    
    # Log top features
    logger.info("XGBoost feature importances (gain, top 5):")
    for i, (feature, importance) in enumerate(sorted_features[:5]):
        logger.info("  %d. %s: %.4f", i+1, feature, importance)
    
    return info
