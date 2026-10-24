"""
tests/unit/test_xgboost.py
---------------------------
Unit tests for XGBoost model specification (CN-009, Phase 3).

Tests the XGBoost model spec, parameter validation, and feature importance export.

TRD §16, FR-005, ML-001, CN-009.
"""

import numpy as np
import pytest
from sklearn.datasets import make_classification
import xgboost as xgb

from models.base import ModelSpec
from models.xgboost_model import get_xgboost_spec, export_xgboost_info


class TestXGBoostSpec:
    """Test XGBoost model specification."""
    
    def test_get_spec(self):
        """Test getting XGBoost spec."""
        spec = get_xgboost_spec(random_state=42)
        
        assert spec.name == 'xgboost'
        assert callable(spec.estimator_factory)
        assert isinstance(spec.param_space, dict)
        
        # Check that param names are prefixed with 'classifier__'
        for key in spec.param_space.keys():
            assert key.startswith('classifier__'), f"Parameter {key} not prefixed"
    
    def test_estimator_factory(self):
        """Test that factory creates XGBClassifier."""
        spec = get_xgboost_spec(random_state=42)
        estimator = spec.estimator_factory()
        
        assert isinstance(estimator, xgb.XGBClassifier)
        assert estimator.random_state == 42
        assert estimator.n_jobs == -1  # Should use all CPUs
        assert estimator.objective == 'multi:softprob'  # Multi-class
        assert estimator.verbosity == 0  # Silent
    
    def test_param_space_valid(self):
        """Test that param space contains valid xgboost parameters."""
        spec = get_xgboost_spec()
        
        # Get valid param names from XGBClassifier
        valid_params = set(xgb.XGBClassifier().get_params().keys())
        
        # Check each param in spec (remove 'classifier__' prefix)
        for key in spec.param_space.keys():
            param_name = key.replace('classifier__', '')
            assert param_name in valid_params, f"Invalid parameter: {param_name}"
    
    def test_param_values_valid(self):
        """Test that parameter values are valid for xgboost."""
        spec = get_xgboost_spec()
        
        # Test some specific combinations that should work
        test_params = [
            {'n_estimators': 50, 'max_depth': 3, 'learning_rate': 0.01},
            {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1},
            {'n_estimators': 200, 'max_depth': 10, 'learning_rate': 0.3, 'subsample': 0.8},
        ]
        
        for params in test_params:
            # Should not raise an exception
            xgb_clf = xgb.XGBClassifier(**params, random_state=42)
            assert isinstance(xgb_clf, xgb.XGBClassifier)


class TestXGBoostInfo:
    """Test XGBoost info export."""
    
    def test_export_info_basic(self):
        """Test basic info export."""
        # Create and train XGBoost
        X, y = make_classification(
            n_samples=100,
            n_features=5,
            n_informative=3,
            n_redundant=0,
            n_classes=4,
            n_clusters_per_class=1,
            random_state=42
        )
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        xgb_clf = xgb.XGBClassifier(n_estimators=10, random_state=42)
        xgb_clf.fit(X, y)
        
        # Export info
        info = export_xgboost_info(xgb_clf, feature_names)
        
        # Check structure
        assert 'feature_importances_gain' in info
        assert 'sorted_features' in info
        assert 'n_features' in info
        assert 'n_estimators' in info
        
        # Check values
        assert info['n_features'] == 5
        assert info['n_estimators'] == 10
        assert len(info['feature_importances_gain']) == 5
        assert len(info['sorted_features']) == 5
        
        # All importances should be non-negative
        for importance in info['feature_importances_gain'].values():
            assert importance >= 0
        
        # Sorted features should be in descending order
        importances_sorted = [imp for _, imp in info['sorted_features']]
        assert importances_sorted == sorted(importances_sorted, reverse=True)
    
    def test_export_unfitted_raises_error(self):
        """Test that exporting from unfitted classifier raises error."""
        xgb_clf = xgb.XGBClassifier(random_state=42)
        feature_names = ['feat1', 'feat2']
        
        with pytest.raises(ValueError, match="must be fitted"):
            export_xgboost_info(xgb_clf, feature_names)
    
    def test_export_mismatch_features_raises_error(self):
        """Test that mismatched feature names raise error."""
        # Create and train XGBoost
        X, y = make_classification(
            n_samples=50,
            n_features=3,
            n_informative=2,
            n_redundant=0,
            n_classes=2,
            random_state=42
        )
        xgb_clf = xgb.XGBClassifier(n_estimators=5, random_state=42)
        xgb_clf.fit(X, y)
        
        # Wrong number of feature names
        wrong_names = ['feat1', 'feat2']  # Only 2 names for 3 features
        
        with pytest.raises(ValueError, match="Mismatch"):
            export_xgboost_info(xgb_clf, wrong_names)
    
    def test_export_with_real_feature_names(self):
        """Test export with realistic flow feature names."""
        # Simulate flow features
        feature_names = [
            'duration',
            'flowBytesPerSecond',
            'mean_fiat',
            'mean_biat',
            'max_flowiat'
        ]
        
        # Create synthetic data
        X = np.random.rand(100, 5)
        y = np.random.randint(0, 4, 100)  # 4 classes like our data
        
        xgb_clf = xgb.XGBClassifier(n_estimators=10, random_state=42)
        xgb_clf.fit(X, y)
        
        info = export_xgboost_info(xgb_clf, feature_names)
        
        # Check that feature names are preserved
        assert set(info['feature_importances_gain'].keys()) == set(feature_names)
        
        # Check sorted features have correct names
        sorted_names = [name for name, _ in info['sorted_features']]
        assert set(sorted_names) == set(feature_names)


class TestXGBoostIntegration:
    """Test XGBoost integration with training pipeline."""
    
    def test_spec_in_modelspec_interface(self):
        """Test that XGBoost spec follows ModelSpec interface."""
        spec = get_xgboost_spec()
        
        # Should be a valid ModelSpec
        assert isinstance(spec, ModelSpec)
        
        # Should pass ModelSpec validation
        assert spec.name in {'decision_tree', 'random_forest', 'svm', 'xgboost'}
        
        # Factory should work
        estimator = spec.estimator_factory()
        assert hasattr(estimator, 'fit')
        assert hasattr(estimator, 'predict')
    
    def test_xgboost_with_multiclass(self):
        """Test XGBoost handles multi-class classification."""
        X, y = make_classification(
            n_samples=100,
            n_features=5,
            n_informative=3,
            n_redundant=0,
            n_classes=4,  # 4 classes like our data
            n_clusters_per_class=1,
            random_state=42
        )
        
        spec = get_xgboost_spec(random_state=42)
        xgb_clf = spec.estimator_factory()
        
        # Should fit without errors
        xgb_clf.fit(X, y)
        
        # Should predict
        predictions = xgb_clf.predict(X)
        assert len(predictions) == len(y)
        assert set(predictions).issubset(set(y))  # Predictions should be valid classes
        
        # Should have predict_proba
        proba = xgb_clf.predict_proba(X)
        assert proba.shape == (len(X), 4)  # 4 classes
        assert np.allclose(proba.sum(axis=1), 1.0)  # Probabilities sum to 1
    
    def test_xgboost_with_integer_labels(self):
        """Test XGBoost with integer-encoded labels."""
        X = np.random.rand(100, 5)
        y = np.array([0, 1, 2, 3] * 25)  # Integer labels
        
        spec = get_xgboost_spec(random_state=42)
        xgb_clf = spec.estimator_factory()
        
        # Should fit without errors
        xgb_clf.fit(X, y)
        
        # Should predict correctly
        predictions = xgb_clf.predict(X)
        assert predictions.dtype in [np.int32, np.int64]
    
    def test_reproducibility(self):
        """Test that XGBoost with same seed gives same results."""
        X, y = make_classification(n_samples=50, n_features=4, n_classes=3, 
                                   n_informative=3, n_redundant=0,
                                   n_clusters_per_class=1, random_state=42)
        
        # Train two XGBoost models with same seed
        spec1 = get_xgboost_spec(random_state=42)
        spec2 = get_xgboost_spec(random_state=42)
        
        xgb1 = spec1.estimator_factory()
        xgb2 = spec2.estimator_factory()
        
        xgb1.fit(X, y)
        xgb2.fit(X, y)
        
        # Predictions should be identical
        pred1 = xgb1.predict(X)
        pred2 = xgb2.predict(X)
        
        np.testing.assert_array_equal(pred1, pred2)
        
        # Feature importances should be identical
        np.testing.assert_array_almost_equal(
            xgb1.feature_importances_,
            xgb2.feature_importances_
        )
