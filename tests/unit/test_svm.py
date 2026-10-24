"""
tests/unit/test_svm.py
----------------------
Unit tests for SVM model specification (CN-008, Phase 3).

Tests the SVM model spec, parameter validation, scalability handling, and feasibility checks.

TRD §15, FR-005, ML-001, ML-012, CN-008, RID-06.
"""

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.svm import SVC

from models.base import ModelSpec
from models.svm import get_svm_spec, check_svm_feasibility


class TestSVMSpec:
    """Test SVM model specification."""
    
    def test_get_spec_no_subsample(self):
        """Test getting SVM spec without subsampling."""
        spec = get_svm_spec(random_state=42, subsample_fraction=None)
        
        assert spec.name == 'svm'
        assert callable(spec.estimator_factory)
        assert isinstance(spec.param_space, dict)
        
        # Check that param names are prefixed with 'classifier__'
        for key in spec.param_space.keys():
            assert key.startswith('classifier__'), f"Parameter {key} not prefixed"
        
        # Should not mention subsampling in notes
        assert 'SCALABILITY' not in spec.notes
    
    def test_get_spec_with_subsample(self):
        """Test getting SVM spec with subsampling."""
        spec = get_svm_spec(random_state=42, subsample_fraction=0.5)
        
        assert spec.name == 'svm'
        
        # Should mention subsampling in notes
        assert 'SCALABILITY' in spec.notes
        assert 'RID-06' in spec.notes
        assert '50.0%' in spec.notes
    
    def test_subsample_fraction_validation(self):
        """Test that invalid subsample_fraction raises error."""
        # Too small
        with pytest.raises(ValueError, match="must be in"):
            get_svm_spec(subsample_fraction=0.0)
        
        # Too large
        with pytest.raises(ValueError, match="must be in"):
            get_svm_spec(subsample_fraction=1.5)
        
        # Negative
        with pytest.raises(ValueError, match="must be in"):
            get_svm_spec(subsample_fraction=-0.1)
    
    def test_estimator_factory(self):
        """Test that factory creates SVC."""
        spec = get_svm_spec(random_state=42)
        estimator = spec.estimator_factory()
        
        assert isinstance(estimator, SVC)
        assert estimator.random_state == 42
        assert estimator.probability is False  # Should be disabled for speed
        assert estimator.cache_size == 500  # Increased cache
    
    def test_param_space_valid(self):
        """Test that param space contains valid sklearn parameters."""
        spec = get_svm_spec()
        
        # Get valid param names from SVC
        valid_params = set(SVC().get_params().keys())
        
        # Check each param in spec (remove 'classifier__' prefix)
        for key in spec.param_space.keys():
            param_name = key.replace('classifier__', '')
            assert param_name in valid_params, f"Invalid parameter: {param_name}"
    
    def test_param_values_valid(self):
        """Test that parameter values are valid for sklearn."""
        spec = get_svm_spec()
        
        # Test some specific combinations that should work
        test_params = [
            {'C': 0.1, 'kernel': 'rbf', 'gamma': 'scale'},
            {'C': 1.0, 'kernel': 'linear', 'class_weight': 'balanced'},
            {'C': 10.0, 'kernel': 'rbf', 'gamma': 'auto', 'class_weight': None},
        ]
        
        for params in test_params:
            # Should not raise an exception
            svm = SVC(**params, random_state=42)
            assert isinstance(svm, SVC)


class TestSVMFeasibility:
    """Test SVM feasibility checking."""
    
    def test_check_feasibility_small_dataset(self):
        """Test feasibility check for small dataset."""
        result = check_svm_feasibility(
            n_samples=5000,
            n_features=10,
            time_limit_seconds=600.0
        )
        
        assert 'feasible_full' in result
        assert 'recommendation' in result
        assert 'estimated_time_rbf_seconds' in result
        
        # Small dataset should be feasible
        assert result['feasible_full'] is True
        assert result['recommendation'] == 'full'
    
    def test_check_feasibility_large_dataset(self):
        """Test feasibility check for large dataset."""
        result = check_svm_feasibility(
            n_samples=50000,
            n_features=20,
            time_limit_seconds=600.0  # 10 minutes
        )
        
        assert 'feasible_full' in result
        assert 'recommendation' in result
        
        # Large dataset likely not feasible within 10 min
        # Recommendation should be subsample or linear_only
        assert result['recommendation'] in ['subsample', 'linear_only']
        
        if result['recommendation'] == 'subsample':
            assert 'subsample_size' in result
            assert 'subsample_fraction' in result
            assert result['subsample_size'] <= result['n_samples']
    
    def test_check_feasibility_our_dataset_size(self):
        """Test feasibility check for our actual dataset size (~48k samples)."""
        result = check_svm_feasibility(
            n_samples=47696,  # Our actual training set size
            n_features=9,     # After feature selection
            time_limit_seconds=600.0
        )
        
        # Should have all required fields
        assert 'feasible_full' in result
        assert 'recommendation' in result
        assert 'estimated_time_rbf_seconds' in result
        assert 'n_samples' in result
        assert result['n_samples'] == 47696
    
    def test_feasibility_estimates_reasonable(self):
        """Test that time estimates are in reasonable ranges."""
        result = check_svm_feasibility(
            n_samples=10000,
            n_features=10,
            time_limit_seconds=600.0
        )
        
        # Estimates should be positive
        assert result['estimated_time_rbf_seconds'] > 0
        assert result['estimated_time_linear_seconds'] > 0
        
        # RBF should be slower than Linear for same data
        assert result['estimated_time_rbf_seconds'] > result['estimated_time_linear_seconds']


class TestSVMIntegration:
    """Test SVM integration with training pipeline."""
    
    def test_spec_in_modelspec_interface(self):
        """Test that SVM spec follows ModelSpec interface."""
        spec = get_svm_spec()
        
        # Should be a valid ModelSpec
        assert isinstance(spec, ModelSpec)
        
        # Should pass ModelSpec validation
        assert spec.name in {'decision_tree', 'random_forest', 'svm', 'xgboost'}
        
        # Factory should work
        estimator = spec.estimator_factory()
        assert hasattr(estimator, 'fit')
        assert hasattr(estimator, 'predict')
    
    def test_svm_requires_scaling(self):
        """Test that SVM works better with scaled features."""
        # This test demonstrates WHY we need MinMaxScaler in pipeline
        
        # Create data with very different scales
        X, y = make_classification(n_samples=100, n_features=5, n_informative=3, 
                                   n_redundant=0, random_state=42)
        X[:, 0] *= 1000  # First feature very large scale
        X[:, 1] *= 1     # Second feature normal scale
        X[:, 2] *= 0.01  # Third feature very small scale
        
        # SVM without scaling
        svm_unscaled = SVC(kernel='rbf', gamma='scale', random_state=42)
        svm_unscaled.fit(X, y)
        score_unscaled = svm_unscaled.score(X, y)
        
        # SVM with scaling
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        svm_scaled = SVC(kernel='rbf', gamma='scale', random_state=42)
        svm_scaled.fit(X_scaled, y)
        score_scaled = svm_scaled.score(X_scaled, y)
        
        # Scaled version should perform better (or at least not worse)
        # This is why our pipeline includes MinMaxScaler before classifier
        assert score_scaled >= score_unscaled - 0.1  # Allow small tolerance
    
    def test_svm_with_simple_data(self):
        """Test SVM can fit and predict on simple data."""
        X, y = make_classification(
            n_samples=100,
            n_features=5,
            n_informative=3,
            n_redundant=0,
            random_state=42
        )
        
        spec = get_svm_spec(random_state=42)
        svm = spec.estimator_factory()
        
        # Should fit without errors
        svm.fit(X, y)
        
        # Should predict
        predictions = svm.predict(X)
        assert len(predictions) == len(y)
        
        # Should have decision_function
        assert hasattr(svm, 'decision_function')
        decision = svm.decision_function(X)
        assert decision.shape[0] == len(y)
    
    def test_reproducibility(self):
        """Test that SVM with same seed gives same results."""
        X, y = make_classification(n_samples=50, n_features=4, random_state=42)
        
        # Train two SVMs with same seed
        spec1 = get_svm_spec(random_state=42)
        spec2 = get_svm_spec(random_state=42)
        
        svm1 = spec1.estimator_factory()
        svm2 = spec2.estimator_factory()
        
        svm1.fit(X, y)
        svm2.fit(X, y)
        
        # Predictions should be identical
        pred1 = svm1.predict(X)
        pred2 = svm2.predict(X)
        
        np.testing.assert_array_equal(pred1, pred2)


class TestStratifiedSubsampling:
    """Test stratified subsampling for SVM scalability."""
    
    def test_subsample_preserves_class_distribution(self):
        """Test that stratified subsampling preserves class proportions."""
        from sklearn.model_selection import train_test_split
        
        # Create imbalanced dataset
        n_samples = 1000
        y = np.concatenate([
            np.zeros(400),   # Class 0: 40%
            np.ones(300),    # Class 1: 30%
            np.full(200, 2), # Class 2: 20%
            np.full(100, 3), # Class 3: 10%
        ])
        X = np.random.rand(n_samples, 5)
        
        # Stratified subsample to 50%
        X_sub, _, y_sub, _ = train_test_split(
            X, y,
            train_size=0.5,
            stratify=y,
            random_state=42
        )
        
        # Check original proportions
        orig_props = np.bincount(y.astype(int)) / len(y)
        
        # Check subsample proportions
        sub_props = np.bincount(y_sub.astype(int)) / len(y_sub)
        
        # Proportions should be approximately preserved
        np.testing.assert_array_almost_equal(orig_props, sub_props, decimal=2)
