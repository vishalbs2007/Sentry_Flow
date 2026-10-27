"""
tests/fixtures/synthetic_data.py
---------------------------------
Synthetic data fixtures for integration testing (CN-019).

Creates tiny synthetic datasets for plumbing tests only.
NOT for model performance evaluation (EV-008).

AGENTS.md: "Synthetic/test fixtures are for plumbing only — 
never report model performance from synthetic data."
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple


def create_synthetic_train_test(
    n_train: int = 100,
    n_test: int = 30,
    n_features: int = 9,
    n_classes: int = 4,
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create synthetic train and test datasets.
    
    Parameters
    ----------
    n_train : int
        Number of training samples
    n_test : int
        Number of test samples
    n_features : int
        Number of features
    n_classes : int
        Number of classes
    random_seed : int
        Random seed for reproducibility
        
    Returns
    -------
    train_df : pd.DataFrame
        Training data with features + 'label' column
    test_df : pd.DataFrame
        Test data with features + 'label' column
        
    Notes
    -----
    This is SYNTHETIC data for plumbing tests only.
    Do NOT use for model performance evaluation.
    """
    np.random.seed(random_seed)
    
    # Feature names matching real schema
    feature_names = [
        'duration',
        'flowBytesPerSecond',
        'mean_fiat',
        'mean_flowiat',
        'max_flowiat',
        'min_flowiat',
        'std_flowiat',
        'mean_active',
        'mean_idle',
    ][:n_features]
    
    # Class names matching real data
    class_names = ['File Transfer', 'Streaming', 'VoIP', 'Web Browsing'][:n_classes]
    
    # Generate train data
    X_train = np.random.randn(n_train, n_features).astype(np.float64)
    y_train = np.random.choice(class_names, n_train)
    
    train_df = pd.DataFrame(X_train, columns=feature_names)
    train_df['label'] = y_train
    
    # Generate test data (different distribution to test generalization)
    X_test = np.random.randn(n_test, n_features).astype(np.float64) + 0.5
    y_test = np.random.choice(class_names, n_test)
    
    test_df = pd.DataFrame(X_test, columns=feature_names)
    test_df['label'] = y_test
    
    return train_df, test_df


def save_synthetic_split(
    output_dir: Path,
    n_train: int = 100,
    n_test: int = 30,
    random_seed: int = 42,
) -> None:
    """Save synthetic train/test split to disk.
    
    Parameters
    ----------
    output_dir : Path
        Directory to save train and test CSV files
    n_train : int
        Number of training samples
    n_test : int
        Number of test samples  
    random_seed : int
        Random seed
    """
    output_dir = Path(output_dir)
    train_dir = output_dir / 'train'
    test_dir = output_dir / 'test'
    
    train_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    train_df, test_df = create_synthetic_train_test(
        n_train=n_train,
        n_test=n_test,
        random_seed=random_seed
    )
    
    train_df.to_csv(train_dir / 'train.csv', index=False)
    test_df.to_csv(test_dir / 'test.csv', index=False)


def create_synthetic_label_mapping() -> dict:
    """Create synthetic label mapping config.
    
    Returns
    -------
    dict
        Label mapping dictionary ready for YAML
    """
    return {
        'version': '1.0',
        'status': 'approved',
        'mapping': {
            'File Transfer': 'File Transfer',
            'Streaming': 'Streaming',
            'VoIP': 'VoIP',
            'Web Browsing': 'Web Browsing',
        },
        'drop': [],
    }


def create_synthetic_feature_schema() -> dict:
    """Create synthetic feature schema config.
    
    Returns
    -------
    dict
        Feature schema dictionary ready for YAML
    """
    return {
        'version': '1.0',
        'status': 'approved',
        'features': [
            'duration',
            'flowBytesPerSecond',
            'mean_fiat',
            'mean_flowiat',
            'max_flowiat',
            'min_flowiat',
            'std_flowiat',
            'mean_active',
            'mean_idle',
        ],
        'metadata': [],
        'excluded': [],
        'groups': {
            'time': ['duration', 'mean_fiat', 'mean_flowiat', 'max_flowiat', 'min_flowiat', 'std_flowiat', 'mean_active', 'mean_idle'],
            'volume': ['flowBytesPerSecond'],
            'tcp_flags': [],
            'directional': [],
        },
        'alias_map': {},
    }
