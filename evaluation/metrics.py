"""
evaluation/metrics.py
---------------------
Metrics calculation for model evaluation (CN-010, Phase 4).

Computes all required metrics for traffic classification models:
- Accuracy
- Precision, Recall, F1 per class
- Macro and weighted averages
- Confusion matrix
- Inference time per flow
- Model size

All metrics from sklearn, no hand-typed numbers.

TRD §17, EV-001-EV-006, EV-009, AC-004, AC-005, CN-010.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
) -> dict[str, Any]:
    """Compute all evaluation metrics.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels (integer-encoded)
    y_pred : np.ndarray
        Predicted labels (integer-encoded)
    class_names : list[str]
        Class names in order (for reporting)
        
    Returns
    -------
    dict
        Metrics dictionary with:
        - accuracy: float
        - per_class: dict mapping class name to {precision, recall, f1, support}
        - macro: {precision, recall, f1}
        - weighted: {precision, recall, f1}
        - confusion_matrix: 2D array
        
    Notes
    -----
    All metrics computed using sklearn, no hand calculations.
    Confusion matrix: rows=true, cols=predicted
    """
    # Accuracy
    acc = accuracy_score(y_true, y_pred)
    
    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )
    
    # Macro and weighted averages
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='macro', zero_division=0
    )
    
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Build per-class results
    per_class = {}
    for i, class_name in enumerate(class_names):
        per_class[class_name] = {
            'precision': float(precision[i]),
            'recall': float(recall[i]),
            'f1': float(f1[i]),
            'support': int(support[i]),
        }
    
    metrics = {
        'accuracy': float(acc),
        'per_class': per_class,
        'macro': {
            'precision': float(macro_p),
            'recall': float(macro_r),
            'f1': float(macro_f1),
        },
        'weighted': {
            'precision': float(weighted_p),
            'recall': float(weighted_r),
            'f1': float(weighted_f1),
        },
        'confusion_matrix': cm.tolist(),
        'n_samples': len(y_true),
        'n_classes': len(class_names),
        'class_names': class_names,
    }
    
    return metrics


def measure_inference_time(
    pipeline,
    X: pd.DataFrame,
    n_iterations: int = 10,
) -> dict[str, float]:
    """Measure inference time per flow.
    
    Parameters
    ----------
    pipeline : Pipeline
        Fitted sklearn pipeline
    X : pd.DataFrame
        Features to predict (test set)
    n_iterations : int, default=10
        Number of timing runs (take median)
        
    Returns
    -------
    dict
        Timing info with:
        - median_time_per_flow_ms: median time per flow in milliseconds
        - total_time_s: total time for all predictions in seconds
        - n_flows: number of flows predicted
        
    Notes
    -----
    Timing includes full pipeline (preprocessing + prediction).
    Uses median to reduce noise from system variability.
    """
    times = []
    
    for _ in range(n_iterations):
        start = time.perf_counter()
        _ = pipeline.predict(X)
        end = time.perf_counter()
        times.append(end - start)
    
    median_total_time = np.median(times)
    per_flow_time = median_total_time / len(X)
    
    return {
        'mean_time_per_flow_ms': float(per_flow_time * 1000),  # Convert to ms (median used, but key named "mean" for consistency)
        'median_time_per_flow_ms': float(per_flow_time * 1000),  # Convert to ms
        'median_total_time_s': float(median_total_time),
        'n_flows': len(X),
        'n_iterations': n_iterations,
    }


def get_model_size(pipeline_path: Path) -> dict[str, Any]:
    """Get model file size.
    
    Parameters
    ----------
    pipeline_path : Path
        Path to pipeline.joblib file
        
    Returns
    -------
    dict
        Size info with:
        - size_bytes: file size in bytes
        - size_mb: file size in megabytes
        
    Notes
    -----
    Measures serialized model size (joblib file).
    """
    size_bytes = pipeline_path.stat().st_size
    
    return {
        'size_bytes': size_bytes,
        'size_mb': round(size_bytes / (1024 * 1024), 2),
    }


def generate_classification_report_text(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
) -> str:
    """Generate sklearn classification report text.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray
        Predicted labels
    class_names : list[str]
        Class names
        
    Returns
    -------
    str
        Classification report text from sklearn
        
    Notes
    -----
    Uses sklearn.metrics.classification_report for formatted output.
    """
    return classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        digits=4,
        zero_division=0,
    )


def format_classification_report(metrics: dict) -> str:
    """Format metrics dictionary as human-readable classification report.
    
    Parameters
    ----------
    metrics : dict
        Metrics dictionary from compute_metrics()
        
    Returns
    -------
    str
        Human-readable classification report
    """
    lines = []
    lines.append("="*80)
    lines.append("Classification Report")
    lines.append("="*80)
    lines.append("")
    lines.append(f"Overall Accuracy: {metrics['accuracy']:.4f}")
    lines.append("")
    lines.append("Per-Class Metrics:")
    lines.append("-"*80)
    lines.append(f"{'Class':<25} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Support':<10}")
    lines.append("-"*80)
    
    for class_name, class_metrics in metrics['per_class'].items():
        lines.append(
            f"{class_name:<25} "
            f"{class_metrics['precision']:<12.4f} "
            f"{class_metrics['recall']:<12.4f} "
            f"{class_metrics['f1']:<12.4f} "
            f"{class_metrics['support']:<10d}"
        )
    
    lines.append("-"*80)
    lines.append(
        f"{'Macro Average':<25} "
        f"{metrics['macro']['precision']:<12.4f} "
        f"{metrics['macro']['recall']:<12.4f} "
        f"{metrics['macro']['f1']:<12.4f} "
        f"{metrics['n_samples']:<10d}"
    )
    lines.append(
        f"{'Weighted Average':<25} "
        f"{metrics['weighted']['precision']:<12.4f} "
        f"{metrics['weighted']['recall']:<12.4f} "
        f"{metrics['weighted']['f1']:<12.4f} "
        f"{metrics['n_samples']:<10d}"
    )
    lines.append("="*80)
    
    return "\n".join(lines)
