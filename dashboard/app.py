"""
dashboard/app.py
----------------
FlowSentry Web Dashboard

Simple Flask-based dashboard to visualize:
- Dataset statistics
- Model performance comparison
- Feature importance
- Classification results (PCAP inference)

Usage:
    python -m dashboard.app
    
Then open browser: http://localhost:5000
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, jsonify, send_from_directory
import pandas as pd

from common.logging_setup import setup_logging
from common.paths import ProjectPaths
from common.config import load_config
import logging

# Setup
setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development


# Load project paths
try:
    config = load_config('config/default.yaml')
    paths = ProjectPaths(config)
except Exception as e:
    logger.error(f"Failed to load config: {e}")
    paths = None


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/dataset-info')
def dataset_info():
    """Get dataset statistics."""
    try:
        train_path = paths.data_processed / 'train' / 'train.csv'
        test_path = paths.data_processed / 'test' / 'test.csv'
        
        if not train_path.exists():
            return jsonify({'error': 'Training data not found'}), 404
        
        # Load data
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        # Get target column
        label_col = 'label' if 'label' in train_df.columns else train_df.columns[-1]
        
        # Class distribution
        class_counts = train_df[label_col].value_counts().to_dict()
        class_distribution = [
            {'class': k, 'count': int(v), 'percentage': round((v / len(train_df)) * 100, 2)}
            for k, v in class_counts.items()
        ]
        
        return jsonify({
            'train_samples': len(train_df),
            'test_samples': len(test_df),
            'total_samples': len(train_df) + len(test_df),
            'features': train_df.shape[1] - 1,
            'classes': len(class_counts),
            'class_distribution': class_distribution
        })
    
    except Exception as e:
        logger.exception("Failed to get dataset info")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models')
def get_models():
    """Get trained models information."""
    try:
        runs_dir = paths.artifacts / 'runs'
        
        if not runs_dir.exists():
            return jsonify({'models': []})
        
        models = []
        for run_dir in runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            
            metrics_file = run_dir / 'metrics_cv.json'
            train_info_file = run_dir / 'train_info.json'
            
            if metrics_file.exists() and train_info_file.exists():
                with open(metrics_file) as f:
                    metrics = json.load(f)
                with open(train_info_file) as f:
                    train_info = json.load(f)
                
                models.append({
                    'run_id': run_dir.name,
                    'model_name': train_info.get('model_name', 'unknown'),
                    'cv_score': metrics.get('best_score', 0),
                    'train_time': train_info.get('train_time_seconds', 0),
                    'train_samples': train_info.get('train_samples', 0),
                    'timestamp': train_info.get('timestamp', ''),
                    'best_params': metrics.get('best_params', {})
                })
        
        # Get best score per model type
        best_models = {}
        for model in models:
            model_type = model['model_name']
            if model_type not in best_models or model['cv_score'] > best_models[model_type]['cv_score']:
                best_models[model_type] = model
        
        return jsonify({
            'models': list(best_models.values()),
            'count': len(best_models)
        })
    
    except Exception as e:
        logger.exception("Failed to get models")
        return jsonify({'error': str(e)}), 500


@app.route('/api/feature-importance')
def feature_importance():
    """Get feature importance from Random Forest."""
    try:
        runs_dir = paths.artifacts / 'runs'
        
        # Find Random Forest run with feature importances
        for run_dir in runs_dir.iterdir():
            if run_dir.is_dir() and 'random_forest' in run_dir.name:
                importance_file = run_dir / 'feature_importances.json'
                if importance_file.exists():
                    with open(importance_file) as f:
                        importances = json.load(f)
                    
                    sorted_features = importances.get('sorted_features', [])[:15]
                    
                    return jsonify({
                        'features': [
                            {'name': name, 'importance': float(imp)}
                            for name, imp in sorted_features
                        ]
                    })
        
        return jsonify({'features': []})
    
    except Exception as e:
        logger.exception("Failed to get feature importance")
        return jsonify({'error': str(e)}), 500


@app.route('/api/registry')
def get_registry():
    """Get model registry information."""
    try:
        registry_file = paths.artifacts / 'registry' / 'registry.json'
        
        if not registry_file.exists():
            return jsonify({'entries': [], 'active_model_id': None})
        
        with open(registry_file) as f:
            registry = json.load(f)
        
        return jsonify(registry)
    
    except Exception as e:
        logger.exception("Failed to get registry")
        return jsonify({'error': str(e)}), 500


@app.route('/api/confusion-matrix/<run_id>')
def confusion_matrix(run_id):
    """Get confusion matrix for a specific run."""
    try:
        run_dir = paths.artifacts / 'runs' / run_id
        metrics_file = run_dir / 'metrics_cv.json'
        
        if not metrics_file.exists():
            return jsonify({'error': 'Run not found'}), 404
        
        with open(metrics_file) as f:
            metrics = json.load(f)
        
        # Check if confusion matrix exists
        cm_data = metrics.get('confusion_matrix')
        if cm_data:
            return jsonify({'confusion_matrix': cm_data})
        
        return jsonify({'error': 'Confusion matrix not available'}), 404
    
    except Exception as e:
        logger.exception("Failed to get confusion matrix")
        return jsonify({'error': str(e)}), 500


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('dashboard/static', filename)


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.exception("Server error")
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Run the Flask app."""
    if paths is None:
        print("❌ Failed to load configuration. Check config/default.yaml")
        return 1
    
    print("\n" + "="*80)
    print("  FlowSentry Dashboard")
    print("="*80)
    print("\n🌐 Starting web server...")
    print(f"📂 Project root: {paths.project_root}")
    print(f"\n✅ Dashboard ready!")
    print(f"\n🔗 Open in browser: http://localhost:5000")
    print(f"\n⏹️  Press Ctrl+C to stop\n")
    
    app.run(host='127.0.0.1', port=5000, debug=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
