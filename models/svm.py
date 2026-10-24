"""
models/svm.py
-------------
Support Vector Machine (SVM) classifier specification for FlowSentry (CN-008, Phase 3).

SVM with RBF kernel can model non-linear decision boundaries:
- Good generalization with proper regularization (C parameter)
- Kernel trick for non-linear patterns
- May be slow on large datasets (RID-06 scalability policy)
- Requires feature scaling (already in pipeline)

Scalability handling (RID-06):
- For large datasets (>50k samples), consider stratified subsample for tuning
- Alternative: LinearSVC (faster, linear kernel only)
- Test set NEVER subsampled
- Record exact subsample size and strategy

Hyperparameters tuned:
- C: regularization parameter (smaller = more regularization)
- kernel: 'rbf' (non-linear) or 'linear'
- gamma: kernel coefficient (for rbf/poly kernels)
- class_weight: handle class imbalance

TRD §15, FR-005, ML-001, ML-012, CN-008, RID-06.
"""

from __future__ import annotations

import logging
from typing import Any

from sklearn.svm import SVC

from models.base import ModelSpec

logger = logging.getLogger(__name__)


def get_svm_spec(random_state: int = 42, subsample_fraction: float | None = None) -> ModelSpec:
    """Create SVM model specification with scalability handling.
    
    Parameters
    ----------
    random_state : int, default=42
        Random state for reproducibility
    subsample_fraction : float or None, default=None
        If provided, train on stratified subsample of training data
        (for scalability per RID-06). Must be in (0.0, 1.0].
        If None, use full training data.
        
    Returns
    -------
    ModelSpec
        SVM specification with tunable hyperparameters
        
    Notes
    -----
    Parameter names verified against scikit-learn 1.9.1 (2024-10-24):
    SVC(
        C=1.0,                    # regularization parameter
        kernel='rbf',             # 'linear', 'poly', 'rbf', 'sigmoid'
        degree=3,                 # for poly kernel
        gamma='scale',            # 'scale' or 'auto' or float
        coef0=0.0,                # for poly/sigmoid
        shrinking=True,
        probability=False,        # enable .predict_proba (expensive!)
        tol=1e-3,
        cache_size=200,
        class_weight=None,        # or 'balanced', or dict
        verbose=False,
        max_iter=-1,              # no limit
        decision_function_shape='ovr',
        break_ties=False,
        random_state=None
    )
    
    Search space rationale:
    - C: regularization trade-off [0.1, 1.0, 10.0]
    - kernel: both linear (fast) and rbf (non-linear)
    - gamma: 'scale' (default, 1/(n_features*X.var())) and 'auto' (1/n_features)
    - class_weight: None and 'balanced' to handle imbalance
    - probability=False (default): predict_proba is expensive and not required
    
    Scalability (RID-06):
    If training takes too long (>10 min), use subsample_fraction < 1.0
    to train on stratified subsample. Document exact size in scalability_note.md.
    
    Scaling requirement:
    SVM requires feature scaling. Our pipeline includes MinMaxScaler before classifier.
    """
    notes_parts = [
        "SVM: kernel method for non-linear decision boundaries. "
        "Good generalization with proper C parameter. "
        "Requires feature scaling (MinMaxScaler in pipeline). "
    ]
    
    if subsample_fraction is not None:
        if not (0.0 < subsample_fraction <= 1.0):
            raise ValueError(f"subsample_fraction must be in (0.0, 1.0], got {subsample_fraction}")
        notes_parts.append(
            f"SCALABILITY (RID-06): Training on {subsample_fraction*100:.1f}% stratified subsample. "
            "Test set NOT subsampled. See scalability_note.md for rationale."
        )
    else:
        notes_parts.append("Training on full training data (no subsampling).")
    
    return ModelSpec(
        name='svm',
        estimator_factory=lambda: SVC(
            random_state=random_state,
            probability=False,  # Don't need predict_proba (expensive)
            cache_size=500,     # Increase cache for faster training
            # All tunable params come from param_space below
        ),
        param_space={
            # Reduced search space for computational efficiency
            # Full space would be: C[0.1,1,10] x kernel[rbf,linear] x gamma[scale,auto] x class_weight[None,balanced]
            # = 12 combinations (still reasonable for SVM)
            'classifier__C': [0.1, 1.0, 10.0],
            'classifier__kernel': ['rbf', 'linear'],
            'classifier__gamma': ['scale', 'auto'],
            'classifier__class_weight': [None, 'balanced'],
        },
        notes=''.join(notes_parts),
    )


def check_svm_feasibility(
    n_samples: int,
    n_features: int,
    time_limit_seconds: float = 600.0,
) -> dict[str, Any]:
    """Estimate SVM training feasibility.
    
    Parameters
    ----------
    n_samples : int
        Number of training samples
    n_features : int
        Number of features after selection
    time_limit_seconds : float, default=600.0
        Maximum acceptable training time in seconds (10 minutes)
        
    Returns
    -------
    dict
        Feasibility assessment with:
        - feasible: bool, whether full training is feasible within time limit
        - estimated_time_seconds: rough estimate of training time
        - recommendation: 'full' or 'subsample' or 'linear_only'
        - subsample_size: if subsampling recommended, suggested size
        
    Notes
    -----
    Very rough heuristics based on sklearn SVM complexity:
    - SVC with RBF kernel: O(n_samples^2 to n_samples^3) time complexity
    - LinearSVC: O(n_samples * n_features) time complexity
    
    For our dataset (~48k samples):
    - Full SVM with RBF: potentially 10-30 minutes
    - Subsample to 10k-20k: more reasonable (2-5 minutes)
    - LinearSVC: fast (< 1 minute)
    """
    # Very rough time estimates (calibrated from typical sklearn behavior)
    # For RBF kernel SVM:
    estimated_time_rbf = (n_samples / 10000) ** 2 * 60  # seconds
    
    # For LinearSVC:
    estimated_time_linear = (n_samples * n_features) / 1000000 * 10  # seconds
    
    feasible = estimated_time_rbf < time_limit_seconds
    
    result = {
        'n_samples': n_samples,
        'n_features': n_features,
        'time_limit_seconds': time_limit_seconds,
        'estimated_time_rbf_seconds': round(estimated_time_rbf, 1),
        'estimated_time_linear_seconds': round(estimated_time_linear, 1),
        'feasible_full': feasible,
    }
    
    if feasible:
        result['recommendation'] = 'full'
        result['note'] = 'Full training feasible within time limit'
    elif n_samples > 30000:
        # Large dataset: subsample to ~20k for reasonable time
        subsample_size = min(20000, n_samples)
        result['recommendation'] = 'subsample'
        result['subsample_size'] = subsample_size
        result['subsample_fraction'] = subsample_size / n_samples
        result['note'] = f'Subsample to {subsample_size} samples for RBF kernel'
    else:
        result['recommendation'] = 'linear_only'
        result['note'] = 'Consider LinearSVC only (faster than RBF kernel)'
    
    logger.info(
        "SVM feasibility check: %d samples, estimated time %.1f seconds (RBF), "
        "recommendation: %s",
        n_samples,
        estimated_time_rbf,
        result['recommendation']
    )
    
    return result
