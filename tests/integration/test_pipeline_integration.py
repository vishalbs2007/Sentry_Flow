"""
tests/integration/test_pipeline_integration.py
----------------------------------------------
Integration tests for dataset→train→evaluate→register pipeline (CN-019).

Tests module boundaries and cross-component contracts using synthetic data.

IMPORTANT: These tests use SYNTHETIC data for plumbing only.
Do NOT report model performance from these tests (AGENTS.md).
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml
import json
import numpy as np

from tests.fixtures.synthetic_data import (
    create_synthetic_train_test,
    create_synthetic_label_mapping,
    create_synthetic_feature_schema,
    save_synthetic_split,
)
from preprocessing.pipeline import build_preprocessor
from models.decision_tree import get_decision_tree_spec
from evaluation.metrics import compute_metrics
from models.registry import register_model, load_model
from common.config import load_config
from common.paths import ProjectPaths


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project structure for testing."""
    project_dir = tmp_path / 'flowsentry_test'
    project_dir.mkdir()
    
    # Create directory structure
    (project_dir / 'config').mkdir()
    (project_dir / 'data' / 'processed').mkdir(parents=True)
    (project_dir / 'artifacts' / 'runs').mkdir(parents=True)
    (project_dir / 'artifacts' / 'registry').mkdir(parents=True)
    (project_dir / 'artifacts' / 'reports').mkdir(parents=True)
    
    # Create synthetic data
    save_synthetic_split(project_dir / 'data' / 'processed', n_train=100, n_test=30)
    
    # Create label mapping
    label_mapping = create_synthetic_label_mapping()
    with open(project_dir / 'config' / 'label_mapping.yaml', 'w') as f:
        yaml.dump(label_mapping, f)
    
    # Create feature schema
    feature_schema = create_synthetic_feature_schema()
    with open(project_dir / 'config' / 'feature_schema.yaml', 'w') as f:
        yaml.dump(feature_schema, f)
    
    # Create minimal config
    config = {
        'paths': {
            'data_root': str(project_dir / 'data'),
            'artifacts': str(project_dir / 'artifacts'),
            'config': str(project_dir / 'config'),
        },
        'preprocessing': {
            'split': {
                'test_size': 0.2,
                'random_state': 42,
            },
            'imputer': {
                'strategy': 'median',
            },
            'scaler': {
                'feature_range': [0, 1],
            },
            'selector': {
                'variance_threshold': 0.01,
                'correlation_threshold': 0.95,
                'importance_k': 9,
            },
        },
        'training': {
            'cv_folds': 2,  # Minimal for speed
            'random_state': 42,
            'scoring': 'f1_macro',
        },
        'models': {
            'decision_tree': {
                'param_grid': {
                    'classifier__max_depth': [3, 5],
                    'classifier__min_samples_split': [2],
                },
            },
        },
    }
    
    with open(project_dir / 'config' / 'default.yaml', 'w') as f:
        yaml.dump(config, f)
    
    yield project_dir
    
    # Cleanup
    shutil.rmtree(project_dir, ignore_errors=True)


def test_dataset_to_preprocessing_integration(temp_project_dir):
    """Test dataset loading → preprocessing pipeline."""
    import pandas as pd
    
    # Load synthetic data
    train_path = temp_project_dir / 'data' / 'processed' / 'train' / 'train.csv'
    train_df = pd.read_csv(train_path)
    
    # Check data loaded correctly
    assert len(train_df) == 100  # n_train from fixture
    assert 'label' in train_df.columns
    
    # Separate features and labels
    X = train_df.drop('label', axis=1)
    y = train_df['label']
    
    # Build preprocessor
    preprocessor = build_preprocessor()
    
    # Fit and transform
    X_transformed = preprocessor.fit_transform(X)
    
    # Check transformation succeeded
    assert X_transformed.shape[0] == len(X)
    assert X_transformed.shape[1] > 0  # Some features selected
    assert not np.isnan(X_transformed).any()  # No NaNs after imputation
    assert X_transformed.min() >= -0.01  # MinMax scaling (with tolerance)
    assert X_transformed.max() <= 1.01  # MinMax scaling (with tolerance)


def test_preprocessing_to_training_integration(temp_project_dir):
    """Test preprocessing → model training pipeline."""
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    
    # Load data
    train_path = temp_project_dir / 'data' / 'processed' / 'train' / 'train.csv'
    train_df = pd.read_csv(train_path)
    
    X = train_df.drop('label', axis=1)
    y = train_df['label']
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Build preprocessor
    preprocessor = build_preprocessor()
    
    # Get model spec
    model_spec = get_decision_tree_spec()
    
    # Build full pipeline
    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model_spec.estimator),
    ])
    
    # Fit pipeline (minimal CV for speed)
    from sklearn.model_selection import cross_val_score
    scores = cross_val_score(
        pipeline, X, y_encoded,
        cv=2,
        scoring='f1_macro',
    )
    
    # Check training succeeded (synthetic data, so score may be low)
    assert len(scores) == 2
    assert all(score >= 0 for score in scores)  # Valid scores
    assert all(score <= 1 for score in scores)


def test_training_to_evaluation_integration(temp_project_dir):
    """Test model training → evaluation pipeline."""
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    import joblib
    
    # Load train and test data
    train_path = temp_project_dir / 'data' / 'processed' / 'train' / 'train.csv'
    test_path = temp_project_dir / 'data' / 'processed' / 'test' / 'test.csv'
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    X_train = train_df.drop('label', axis=1)
    y_train = train_df['label']
    X_test = test_df.drop('label', axis=1)
    y_test = test_df['label']
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    y_test_encoded = label_encoder.transform(y_test)
    
    # Train pipeline
    preprocessor = build_preprocessor()
    model_spec = get_decision_tree_spec()
    
    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model_spec.estimator),
    ])
    
    pipeline.fit(X_train, y_train_encoded)
    
    # Save pipeline temporarily
    pipeline_path = temp_project_dir / 'test_pipeline.joblib'
    joblib.dump(pipeline, pipeline_path)
    
    # Load pipeline (simulating evaluation module)
    loaded_pipeline = joblib.load(pipeline_path)
    
    # Predict on test set
    y_pred = loaded_pipeline.predict(X_test)
    
    # Compute metrics
    metrics = compute_metrics(
        y_test_encoded,
        y_pred,
        label_encoder.classes_.tolist()
    )
    
    # Check metrics structure
    assert 'accuracy' in metrics
    assert 'per_class' in metrics
    assert 'macro' in metrics
    assert 'weighted' in metrics
    assert 'confusion_matrix' in metrics
    
    # Check metrics are valid (synthetic data, so performance may be poor)
    assert 0 <= metrics['accuracy'] <= 1
    assert 0 <= metrics['macro']['f1'] <= 1
    assert len(metrics['per_class']) == len(label_encoder.classes_)


def test_evaluation_to_registry_integration(temp_project_dir):
    """Test evaluation → model registry pipeline."""
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    import joblib
    import json
    from datetime import datetime
    
    # Train a simple pipeline
    train_path = temp_project_dir / 'data' / 'processed' / 'train' / 'train.csv'
    train_df = pd.read_csv(train_path)
    
    X_train = train_df.drop('label', axis=1)
    y_train = train_df['label']
    
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    
    preprocessor = build_preprocessor()
    model_spec = get_decision_tree_spec()
    
    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model_spec.estimator),
    ])
    
    pipeline.fit(X_train, y_train_encoded)
    
    # Create run directory
    run_id = f'test_dt_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    run_dir = temp_project_dir / 'artifacts' / 'runs' / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Save artifacts
    joblib.dump(pipeline, run_dir / 'pipeline.joblib')
    joblib.dump(label_encoder, run_dir / 'label_encoder.joblib')
    
    train_info = {
        'model_name': 'decision_tree',
        'train_samples': len(X_train),
        'train_time_seconds': 1.0,
        'timestamp': datetime.now().isoformat(),
    }
    
    with open(run_dir / 'train_info.json', 'w') as f:
        json.dump(train_info, f)
    
    metrics_cv = {
        'best_score': 0.8,
        'best_params': {},
    }
    
    with open(run_dir / 'metrics_cv.json', 'w') as f:
        json.dump(metrics_cv, f)
    
    # Register model
    registry_dir = temp_project_dir / 'artifacts' / 'registry'
    
    model_id = register_model(
        run_id=run_id,
        model_name='Test Decision Tree',
        runs_dir=temp_project_dir / 'artifacts' / 'runs',
        registry_dir=registry_dir,
        feature_schema_path=temp_project_dir / 'config' / 'feature_schema.yaml',
        label_mapping_path=temp_project_dir / 'config' / 'label_mapping.yaml',
    )
    
    # Check registry entry created
    assert model_id is not None
    assert (registry_dir / model_id).exists()
    assert (registry_dir / model_id / 'pipeline.joblib').exists()
    assert (registry_dir / model_id / 'metadata.json').exists()
    
    # Load model from registry
    loaded_pipeline, metadata = load_model(
        registry_dir=registry_dir,
        model_id=model_id,
    )
    
    # Check loaded pipeline works
    y_pred = loaded_pipeline.predict(X_train)
    assert len(y_pred) == len(X_train)
    assert all(0 <= p < len(label_encoder.classes_) for p in y_pred)


@pytest.mark.requires_dataset
def test_leakage_guard_train_test_disjoint():
    """Test that train and test sets are disjoint (leakage guard)."""
    import pandas as pd
    from common.config import load_config
    from common.paths import ProjectPaths
    
    # Load real config and paths
    config = load_config('config/default.yaml')
    paths = ProjectPaths(config)
    
    # Load train and test sets
    train_path = paths.data_processed / 'train' / 'train.csv'
    test_path = paths.data_processed / 'test' / 'test.csv'
    
    if not train_path.exists() or not test_path.exists():
        pytest.skip("Real dataset not available")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # Check no row overlap (using all columns as identifier)
    train_tuples = set(train_df.itertuples(index=False, name=None))
    test_tuples = set(test_df.itertuples(index=False, name=None))
    
    overlap = train_tuples & test_tuples
    
    assert len(overlap) == 0, f"Train/test overlap detected: {len(overlap)} rows"


def test_leakage_guard_models_cannot_import_test_loader():
    """Test that models/ cannot import test_loader (structural leakage guard)."""
    import sys
    import importlib
    
    # Try to import from models package
    try:
        # This should work
        from models import train
        from models import decision_tree
        
        # This should NOT be possible from models/
        # (test_loader should only be imported by evaluation/)
        # We check that test_loader is not accidentally imported
        
        # Check models/ modules don't have test_loader in their namespace
        assert not hasattr(train, 'load_test_set'), "train module should not have test loader"
        assert not hasattr(decision_tree, 'load_test_set'), "decision_tree should not have test loader"
        
    except ImportError as e:
        pytest.fail(f"Failed to import models modules: {e}")


def test_registry_to_predictor_integration(temp_project_dir):
    """Test model registry → predictor pipeline."""
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    import joblib
    import json
    from datetime import datetime
    
    # Setup: Train and register a model
    train_path = temp_project_dir / 'data' / 'processed' / 'train' / 'train.csv'
    train_df = pd.read_csv(train_path)
    
    X_train = train_df.drop('label', axis=1)
    y_train = train_df['label']
    
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    
    preprocessor = build_preprocessor()
    model_spec = get_decision_tree_spec()
    
    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model_spec.estimator),
    ])
    
    pipeline.fit(X_train, y_train_encoded)
    
    # Create run and register
    run_id = f'test_pred_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    run_dir = temp_project_dir / 'artifacts' / 'runs' / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(pipeline, run_dir / 'pipeline.joblib')
    joblib.dump(label_encoder, run_dir / 'label_encoder.joblib')
    
    train_info = {
        'model_name': 'decision_tree',
        'train_samples': len(X_train),
        'train_time_seconds': 1.0,
        'timestamp': datetime.now().isoformat(),
    }
    
    with open(run_dir / 'train_info.json', 'w') as f:
        json.dump(train_info, f)
    
    with open(run_dir / 'metrics_cv.json', 'w') as f:
        json.dump({'best_score': 0.8, 'best_params': {}}, f)
    
    registry_dir = temp_project_dir / 'artifacts' / 'registry'
    
    model_id = register_model(
        run_id=run_id,
        model_name='Test Predictor Model',
        runs_dir=temp_project_dir / 'artifacts' / 'runs',
        registry_dir=registry_dir,
        feature_schema_path=temp_project_dir / 'config' / 'feature_schema.yaml',
        label_mapping_path=temp_project_dir / 'config' / 'label_mapping.yaml',
    )
    
    # Load model from registry (simulating predictor)
    loaded_pipeline, metadata = load_model(
        registry_dir=registry_dir,
        model_id=model_id,
    )
    
    # Create new data for prediction
    test_path = temp_project_dir / 'data' / 'processed' / 'test' / 'test.csv'
    test_df = pd.read_csv(test_path)
    X_test = test_df.drop('label', axis=1)
    
    # Predict using loaded model
    predictions = loaded_pipeline.predict(X_test)
    
    # Check predictions are valid
    assert len(predictions) == len(X_test)
    assert all(0 <= p < len(label_encoder.classes_) for p in predictions)
    
    # Check we can decode predictions
    class_names = label_encoder.classes_
    pred_labels = [class_names[p] for p in predictions]
    
    assert all(label in class_names for label in pred_labels)
