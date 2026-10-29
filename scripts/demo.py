"""
scripts/demo.py
---------------
FlowSentry Demo Script

Demonstrates the ML-based network traffic classification pipeline:
1. Show dataset statistics
2. Display trained models
3. Show model performance
4. Demonstrate classification (if models are trained)

Usage:
    python scripts/demo.py
"""

import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.logging_setup import setup_logging
from common.paths import ProjectPaths
from common.config import load_config
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print('─' * 80)


def demo_dataset_info(paths: ProjectPaths):
    """Show dataset information."""
    print_section("1. Dataset Information")
    
    train_path = paths.data_processed / 'train' / 'train.csv'
    test_path = paths.data_processed / 'test' / 'test.csv'
    
    if not train_path.exists():
        print("❌ Training data not found. Run preprocessing first.")
        return
    
    # Load data
    print("Loading dataset...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # Get target column (assuming 'label' or last column)
    label_col = 'label' if 'label' in train_df.columns else train_df.columns[-1]
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Training samples:   {len(train_df):,}")
    print(f"   Test samples:       {len(test_df):,}")
    print(f"   Total samples:      {len(train_df) + len(test_df):,}")
    print(f"   Features:           {train_df.shape[1] - 1}")
    
    print(f"\n🏷️  Class Distribution (Training):")
    class_counts = train_df[label_col].value_counts()
    for class_name, count in class_counts.items():
        percentage = (count / len(train_df)) * 100
        bar = '█' * int(percentage / 2)
        print(f"   {class_name:20s}: {count:6,} ({percentage:5.1f}%)  {bar}")


def demo_trained_models(paths: ProjectPaths):
    """Show trained models information."""
    print_section("2. Trained Models")
    
    runs_dir = paths.artifacts / 'runs'
    
    if not runs_dir.exists() or not list(runs_dir.iterdir()):
        print("❌ No trained models found. Train models first with:")
        print("   python -m models.train --model decision_tree")
        print("   python -m models.train --model random_forest")
        print("   python -m models.train --model svm")
        print("   python -m models.train --model xgboost")
        return
    
    # Find all model runs
    models = {}
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir():
            metrics_file = run_dir / 'metrics_cv.json'
            train_info_file = run_dir / 'train_info.json'
            
            if metrics_file.exists() and train_info_file.exists():
                with open(metrics_file) as f:
                    metrics = json.load(f)
                with open(train_info_file) as f:
                    train_info = json.load(f)
                
                model_name = train_info.get('model_name', 'unknown')
                if model_name not in models or metrics['best_score'] > models[model_name]['score']:
                    models[model_name] = {
                        'run_id': run_dir.name,
                        'score': metrics['best_score'],
                        'train_time': train_info.get('train_time_seconds', 0),
                        'train_samples': train_info.get('train_samples', 0),
                        'params': metrics.get('best_params', {}),
                        'timestamp': train_info.get('timestamp', ''),
                    }
    
    if not models:
        print("❌ No valid model runs found.")
        return
    
    print(f"\n🤖 Trained Models: {len(models)}")
    print()
    
    # Sort by score descending
    sorted_models = sorted(models.items(), key=lambda x: x[1]['score'], reverse=True)
    
    for rank, (model_name, info) in enumerate(sorted_models, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{medal} {rank}. {model_name.upper().replace('_', ' ')}")
        print(f"      CV Macro-F1:     {info['score']:.4f} ({info['score']*100:.2f}%)")
        print(f"      Training Time:   {info['train_time']:.1f}s")
        print(f"      Training Samples: {info['train_samples']:,}")
        print(f"      Run ID:          {info['run_id']}")
        
        # Show key parameters
        if info['params']:
            params_str = ', '.join(f"{k.split('__')[-1]}={v}" for k, v in list(info['params'].items())[:3])
            print(f"      Parameters:      {params_str}...")
        print()


def demo_model_comparison(paths: ProjectPaths):
    """Show model comparison."""
    print_section("3. Model Performance Comparison")
    
    runs_dir = paths.artifacts / 'runs'
    
    if not runs_dir.exists():
        print("❌ No models trained yet.")
        return
    
    # Collect model performance
    models_data = []
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir():
            metrics_file = run_dir / 'metrics_cv.json'
            train_info_file = run_dir / 'train_info.json'
            
            if metrics_file.exists() and train_info_file.exists():
                with open(metrics_file) as f:
                    metrics = json.load(f)
                with open(train_info_file) as f:
                    train_info = json.load(f)
                
                models_data.append({
                    'Model': train_info['model_name'].replace('_', ' ').title(),
                    'CV F1': metrics['best_score'],
                    'Time (s)': train_info.get('train_time_seconds', 0),
                    'Samples': train_info.get('train_samples', 0),
                })
    
    if not models_data:
        print("❌ No valid models found.")
        return
    
    # Create comparison table
    df = pd.DataFrame(models_data)
    
    # Get best score per model
    df = df.sort_values('CV F1', ascending=False).drop_duplicates('Model')
    
    print("\n📈 Performance Summary:\n")
    print(df.to_string(index=False))
    
    # Show performance chart
    print("\n\n📊 CV Macro-F1 Score (%):\n")
    max_score = df['CV F1'].max()
    for _, row in df.iterrows():
        score_pct = row['CV F1'] * 100
        bar_length = int((row['CV F1'] / max_score) * 50)
        bar = '█' * bar_length
        print(f"   {row['Model']:20s} {bar} {score_pct:.2f}%")


def demo_registry(paths: ProjectPaths):
    """Show model registry."""
    print_section("4. Model Registry")
    
    registry_file = paths.artifacts / 'registry' / 'registry.json'
    
    if not registry_file.exists():
        print("❌ No models registered yet. Register a model with:")
        print("   python -m models.registry register --run-id <run_id> --model-name <name>")
        return
    
    with open(registry_file) as f:
        registry = json.load(f)
    
    if not registry.get('entries'):
        print("❌ Registry is empty.")
        return
    
    print(f"\n🗂️  Registered Models: {len(registry['entries'])}\n")
    
    active_id = registry.get('active_model_id')
    
    for entry in registry['entries']:
        is_active = entry['model_id'] == active_id
        marker = "✅ ACTIVE" if is_active else "  "
        
        print(f"{marker} {entry['model_name']}")
        print(f"      Model ID:     {entry['model_id']}")
        print(f"      Registered:   {entry['registered_at'][:10]}")
        
        # Load metrics if available
        entry_dir = paths.artifacts / 'registry' / entry['model_id']
        metrics_file = entry_dir / 'metrics.json'
        if metrics_file.exists():
            with open(metrics_file) as f:
                metrics = json.load(f)
            cv_metrics = metrics.get('cv', {})
            if cv_metrics:
                print(f"      CV Macro-F1:  {cv_metrics.get('best_score', 0):.4f}")
        print()


def demo_feature_importances(paths: ProjectPaths):
    """Show feature importances from Random Forest."""
    print_section("5. Feature Importance (Random Forest)")
    
    # Find Random Forest run
    runs_dir = paths.artifacts / 'runs'
    rf_run = None
    
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir() and 'random_forest' in run_dir.name:
            if (run_dir / 'feature_importances.json').exists():
                rf_run = run_dir
                break
    
    if not rf_run:
        print("❌ Random Forest not trained or feature importances not available.")
        return
    
    with open(rf_run / 'feature_importances.json') as f:
        importances = json.load(f)
    
    print("\n🌲 Random Forest Feature Importances:\n")
    print("   Top features for traffic classification:\n")
    
    sorted_features = importances.get('sorted_features', [])[:10]
    max_importance = sorted_features[0][1] if sorted_features else 1.0
    
    for rank, (feature, importance) in enumerate(sorted_features, 1):
        bar_length = int((importance / max_importance) * 40)
        bar = '█' * bar_length
        print(f"   {rank:2d}. {feature:25s} {bar} {importance:.4f}")
    
    print("\n   💡 Insight: Timing features (IAT) dominate traffic classification!")


def demo_project_overview():
    """Show project overview."""
    print_header("FlowSentry - ML-Based Network Traffic Classification")
    
    print("""
🎯 Project Goal:
   Classify network traffic by flow behavior (timing, volume, patterns)
   WITHOUT inspecting packet payloads.

🔬 Approach:
   • Extract flow-level statistical features from network traffic
   • Train machine learning models on labeled dataset (ISCX-VPN2016)
   • Classify traffic into 4 categories:
     - Web Browsing
     - VoIP (Voice over IP)
     - Streaming (Video/Audio)
     - File Transfer

📊 Models:
   • Decision Tree (interpretable baseline)
   • Random Forest (ensemble of trees)
   • SVM (kernel method)
   • XGBoost (gradient boosting)

🎓 Academic Project:
   Computer Networks - Phase 3 (ML Training) complete
   Team: Sudir Niranj R, Vishal B S
    """)


def main():
    """Run FlowSentry demo."""
    # Windows subprocess pipes can default to CP1252, which cannot encode the
    # Unicode symbols used by this presentation script.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")

    try:
        # Load config
        config = load_config('config/default.yaml')
        paths = ProjectPaths(config)
        
        # Show project overview
        demo_project_overview()
        
        # Show dataset info
        demo_dataset_info(paths)
        
        # Show trained models
        demo_trained_models(paths)
        
        # Show model comparison
        demo_model_comparison(paths)
        
        # Show registry
        demo_registry(paths)
        
        # Show feature importances
        demo_feature_importances(paths)
        
        # Final message
        print_header("Demo Complete!")
        
        print("""
✅ What We've Built:

   1. ✅ Dataset Pipeline (ingestion, preprocessing, split)
   2. ✅ ML Models Trained (Decision Tree, Random Forest, SVM)
   3. ✅ Model Registry (persist and load models)
   4. ⏳ Evaluation (test set evaluation - coming next)
   5. ⏳ PCAP Classification (classify real network traffic)
   6. ⏳ Dashboard (visualization)

📈 Next Steps:

   1. Train XGBoost model:
      python -m models.train --model xgboost

   2. Evaluate all models on test set:
      python -m evaluation.evaluate --run-id <run_id>

   3. Compare models and select best:
      python -m evaluation.compare

   4. Classify PCAPs:
      python -m inference.pcap_classifier --pcap <file.pcap>

🎓 For Viva Demonstration:

   • Show network topology (Cisco Packet Tracer)
   • Generate sample traffic
   • Capture PCAP files
   • Run FlowSentry classification
   • Display results in dashboard

📚 Documentation: See README.md and DEMO_SETUP_GUIDE.md
        """)
        
        print("=" * 80)
        
    except Exception as e:
        logger.exception("Demo failed: %s", e)
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
