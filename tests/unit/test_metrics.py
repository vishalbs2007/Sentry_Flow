"""
tests/unit/test_metrics.py
---------------------------
Unit tests for evaluation metrics (CN-010).

Tests metrics computation on hand-checkable examples.
"""

import numpy as np
import pytest

from evaluation.metrics import compute_metrics, measure_inference_time, format_classification_report
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
import pandas as pd


def test_compute_metrics_perfect_classification():
    """Test metrics on perfect classification."""
    y_true = np.array([0, 0, 1, 1, 2, 2])
    y_pred = np.array([0, 0, 1, 1, 2, 2])
    class_names = ['A', 'B', 'C']
    
    metrics = compute_metrics(y_true, y_pred, class_names)
    
    # Perfect classification
    assert metrics['accuracy'] == 1.0
    assert metrics['macro']['f1'] == 1.0
    assert metrics['weighted']['f1'] == 1.0
    
    # All per-class metrics perfect
    for class_name in class_names:
        assert metrics['per_class'][class_name]['f1'] == 1.0
        assert metrics['per_class'][class_name]['precision'] == 1.0
        assert metrics['per_class'][class_name]['recall'] == 1.0


def test_compute_metrics_known_confusion():
    """Test metrics on known confusion matrix.
    
    True:      [0, 0, 1, 1]
    Predicted: [0, 1, 1, 1]
    
    Class 0: TP=1, FP=0, FN=1 → Precision=1.0, Recall=0.5, F1=0.667
    Class 1: TP=2, FP=1, FN=0 → Precision=0.667, Recall=1.0, F1=0.8
    Accuracy: 3/4 = 0.75
    """
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    class_names = ['A', 'B']
    
    metrics = compute_metrics(y_true, y_pred, class_names)
    
    # Accuracy
    assert abs(metrics['accuracy'] - 0.75) < 0.001
    
    # Class A (0)
    assert abs(metrics['per_class']['A']['precision'] - 1.0) < 0.001
    assert abs(metrics['per_class']['A']['recall'] - 0.5) < 0.001
    assert abs(metrics['per_class']['A']['f1'] - 0.667) < 0.01
    
    # Class B (1)
    assert abs(metrics['per_class']['B']['precision'] - 0.667) < 0.01
    assert abs(metrics['per_class']['B']['recall'] - 1.0) < 0.001
    assert abs(metrics['per_class']['B']['f1'] - 0.8) < 0.01
    
    # Confusion matrix
    cm = np.array(metrics['confusion_matrix'])
    assert cm[0, 0] == 1  # TP for class 0
    assert cm[0, 1] == 1  # FN for class 0
    assert cm[1, 0] == 0  # FP for class 0
    assert cm[1, 1] == 2  # TP for class 1


def test_compute_metrics_multiclass():
    """Test metrics on multiclass classification."""
    # 3 classes, some misclassifications
    y_true = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
    y_pred = np.array([0, 0, 1, 1, 1, 2, 2, 2, 0])
    class_names = ['Class0', 'Class1', 'Class2']
    
    metrics = compute_metrics(y_true, y_pred, class_names)
    
    # Check structure
    assert 'accuracy' in metrics
    assert 'per_class' in metrics
    assert 'macro' in metrics
    assert 'weighted' in metrics
    assert 'confusion_matrix' in metrics
    
    # Check all classes present
    assert set(metrics['per_class'].keys()) == set(class_names)
    
    # Check confusion matrix dimensions
    cm = np.array(metrics['confusion_matrix'])
    assert cm.shape == (3, 3)
    
    # Accuracy = 6/9 (6 correct: 0,0,1,1,2,2)
    assert abs(metrics['accuracy'] - 6/9) < 0.001


def test_compute_metrics_support_counts():
    """Test support counts match true label counts."""
    y_true = np.array([0, 0, 0, 1, 1, 2])
    y_pred = np.array([0, 0, 1, 1, 1, 2])
    class_names = ['A', 'B', 'C']
    
    metrics = compute_metrics(y_true, y_pred, class_names)
    
    assert metrics['per_class']['A']['support'] == 3
    assert metrics['per_class']['B']['support'] == 2
    assert metrics['per_class']['C']['support'] == 1
    assert metrics['n_samples'] == 6


def test_measure_inference_time():
    """Test inference timing measurement."""
    # Create simple pipeline
    pipeline = Pipeline([
        ('classifier', DecisionTreeClassifier(max_depth=2, random_state=42))
    ])
    
    # Train on dummy data
    X_train = pd.DataFrame(np.random.randn(100, 5))
    y_train = np.random.randint(0, 3, 100)
    pipeline.fit(X_train, y_train)
    
    # Measure timing
    X_test = pd.DataFrame(np.random.randn(50, 5))
    timing = measure_inference_time(pipeline, X_test, n_iterations=5)
    
    # Check structure
    assert 'mean_time_per_flow_ms' in timing
    assert 'median_time_per_flow_ms' in timing
    assert 'median_total_time_s' in timing
    assert 'n_flows' in timing
    assert 'n_iterations' in timing
    
    # Check values reasonable
    assert timing['n_flows'] == 50
    assert timing['n_iterations'] == 5
    assert timing['mean_time_per_flow_ms'] > 0
    assert timing['mean_time_per_flow_ms'] < 100  # Should be very fast for small tree


def test_format_classification_report():
    """Test formatting of classification report."""
    metrics = {
        'accuracy': 0.95,
        'per_class': {
            'ClassA': {'precision': 0.96, 'recall': 0.94, 'f1': 0.95, 'support': 100},
            'ClassB': {'precision': 0.94, 'recall': 0.96, 'f1': 0.95, 'support': 100},
        },
        'macro': {'precision': 0.95, 'recall': 0.95, 'f1': 0.95},
        'weighted': {'precision': 0.95, 'recall': 0.95, 'f1': 0.95},
        'n_samples': 200,
    }
    
    report = format_classification_report(metrics)
    
    # Check it's a string
    assert isinstance(report, str)
    
    # Check key elements present
    assert 'Overall Accuracy' in report
    assert '0.9500' in report
    assert 'ClassA' in report
    assert 'ClassB' in report
    assert 'Macro Average' in report
    assert 'Weighted Average' in report


def test_compute_metrics_zero_division():
    """Test metrics handle zero division gracefully (e.g., empty class)."""
    # Class 2 never predicted
    y_true = np.array([0, 0, 1, 1, 2, 2])
    y_pred = np.array([0, 0, 1, 1, 0, 0])
    class_names = ['A', 'B', 'C']
    
    # Should not crash
    metrics = compute_metrics(y_true, y_pred, class_names)
    
    # Class C has 0 TP and 0 FP, so precision is undefined
    # sklearn returns 0.0 with zero_division=0
    assert metrics['per_class']['C']['precision'] == 0.0
