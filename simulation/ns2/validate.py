"""
Validate FlowSentry classification results against NS2 ground truth labels.

Usage:
    python validate.py <classification_results.txt> <ns2_traffic_labels.csv>

This script:
1. Loads ground truth labels from NS2 conversion
2. Loads FlowSentry classification predictions
3. Compares them and reports accuracy metrics
4. Identifies misclassifications for debugging
"""

import sys
import re
from pathlib import Path
from collections import defaultdict, Counter


def parse_labels_csv(csv_path):
    """Parse NS2 ground truth labels CSV.
    
    Returns: dict mapping (client_ip, client_port, server_port, proto) -> true_class
    """
    labels = {}
    with open(csv_path) as f:
        lines = f.readlines()
        if not lines:
            return labels
        
        # Skip header
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',')
            if len(parts) >= 5:
                client_ip = parts[0].strip()
                client_port = parts[1].strip()
                server_port = parts[2].strip()
                proto = parts[3].strip()
                true_class = parts[4].strip()
                
                # Create flow key
                key = (client_ip, client_port, server_port, proto)
                labels[key] = true_class
    
    return labels


def parse_classification_results(results_path):
    """Parse FlowSentry classification results.
    
    Returns: dict mapping flow_key -> predicted_class
    """
    predictions = {}
    
    with open(results_path) as f:
        content = f.read()
    
    # Look for flow classification patterns
    # Example: "Flow 1: 10.0.0.10:40001 -> 10.0.1.100:80 (TCP) => Web Browsing (95.2%)"
    
    pattern = r'Flow \d+:\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+->\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+\((\w+)\)\s+=>\s+([^(]+)'
    
    for match in re.finditer(pattern, content):
        src_ip = match.group(1)
        src_port = match.group(2)
        dst_ip = match.group(3)
        dst_port = match.group(4)
        proto = match.group(5).lower()
        predicted_class = match.group(6).strip()
        
        # Determine which is client/server based on IP ranges
        # Clients: 10.0.0.x, Servers: 10.0.1.x
        if src_ip.startswith('10.0.0.'):
            client_ip, client_port = src_ip, src_port
            server_port = dst_port
        else:
            client_ip, client_port = dst_ip, dst_port
            server_port = src_port
        
        key = (client_ip, client_port, server_port, proto)
        predictions[key] = predicted_class
    
    return predictions


def validate(labels, predictions):
    """Compare labels vs predictions and print metrics."""
    
    if not labels:
        print("[ERROR] No ground truth labels found!")
        return False
    
    if not predictions:
        print("[ERROR] No predictions found in classification results!")
        return False
    
    print(f"\n{'='*60}")
    print(f"  VALIDATION RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Ground Truth Flows:  {len(labels)}")
    print(f"Predicted Flows:     {len(predictions)}")
    print()
    
    # Match flows
    correct = 0
    incorrect = 0
    missing = 0
    misclassifications = []
    
    for flow_key, true_class in labels.items():
        client_ip, client_port, server_port, proto = flow_key
        
        if flow_key in predictions:
            pred_class = predictions[flow_key]
            
            # Normalize class names for comparison
            true_normalized = true_class.lower().replace(' ', '').replace('_', '')
            pred_normalized = pred_class.lower().replace(' ', '').replace('_', '')
            
            if true_normalized in pred_normalized or pred_normalized in true_normalized:
                correct += 1
                print(f"✓ {client_ip}:{client_port} -> :{server_port} ({proto.upper()})")
                print(f"  Expected: {true_class} | Got: {pred_class}")
            else:
                incorrect += 1
                print(f"✗ {client_ip}:{client_port} -> :{server_port} ({proto.upper()})")
                print(f"  Expected: {true_class} | Got: {pred_class}")
                misclassifications.append((flow_key, true_class, pred_class))
        else:
            missing += 1
            print(f"? {client_ip}:{client_port} -> :{server_port} ({proto.upper()})")
            print(f"  Expected: {true_class} | Got: NOT FOUND")
    
    # Calculate metrics
    total = len(labels)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}\n")
    print(f"Total Flows:         {total}")
    print(f"Correct:             {correct} ({correct/total*100:.1f}%)")
    print(f"Incorrect:           {incorrect} ({incorrect/total*100:.1f}%)")
    print(f"Missing:             {missing} ({missing/total*100:.1f}%)")
    print(f"\nFlow-Level Accuracy: {accuracy:.2f}%\n")
    
    # Class-wise breakdown
    print(f"{'='*60}")
    print(f"  CLASS BREAKDOWN")
    print(f"{'='*60}\n")
    
    class_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    for flow_key, true_class in labels.items():
        class_stats[true_class]['total'] += 1
        if flow_key in predictions:
            pred_class = predictions[flow_key]
            true_normalized = true_class.lower().replace(' ', '').replace('_', '')
            pred_normalized = pred_class.lower().replace(' ', '').replace('_', '')
            if true_normalized in pred_normalized or pred_normalized in true_normalized:
                class_stats[true_class]['correct'] += 1
    
    for class_name, stats in sorted(class_stats.items()):
        total = stats['total']
        correct = stats['correct']
        acc = (correct / total * 100) if total > 0 else 0
        print(f"{class_name:20s}: {correct}/{total} ({acc:.1f}%)")
    
    # Misclassification analysis
    if misclassifications:
        print(f"\n{'='*60}")
        print(f"  MISCLASSIFICATIONS")
        print(f"{'='*60}\n")
        for flow_key, true_class, pred_class in misclassifications:
            client_ip, client_port, server_port, proto = flow_key
            print(f"Flow: {client_ip}:{client_port} -> :{server_port} ({proto.upper()})")
            print(f"  Expected: {true_class}")
            print(f"  Got:      {pred_class}")
            print()
    
    print(f"{'='*60}\n")
    
    # Interpretation
    if accuracy >= 95:
        print("🎉 EXCELLENT! Model is performing very well on NS2 traffic.")
    elif accuracy >= 80:
        print("✓ GOOD! Model is working correctly with minor errors.")
    elif accuracy >= 60:
        print("⚠ FAIR! Model needs improvement or feature engineering.")
    else:
        print("✗ POOR! Model may need retraining or debugging.")
    
    print()
    return accuracy >= 80


def main():
    if len(sys.argv) != 3:
        print("Usage: python validate.py <classification_results.txt> <ns2_traffic_labels.csv>")
        print()
        print("Example:")
        print("  python validate.py artifacts/ns2_demo/classification_results.txt simulation/pcaps/ns2_traffic_labels.csv")
        sys.exit(1)
    
    results_path = Path(sys.argv[1])
    labels_path = Path(sys.argv[2])
    
    # Check files exist
    if not results_path.exists():
        print(f"[ERROR] Classification results not found: {results_path}")
        sys.exit(1)
    
    if not labels_path.exists():
        print(f"[ERROR] Ground truth labels not found: {labels_path}")
        sys.exit(1)
    
    print(f"\n[INFO] Loading ground truth from: {labels_path}")
    labels = parse_labels_csv(labels_path)
    print(f"[OK] Loaded {len(labels)} ground truth flows")
    
    print(f"[INFO] Loading predictions from: {results_path}")
    predictions = parse_classification_results(results_path)
    print(f"[OK] Loaded {len(predictions)} predicted flows")
    
    # Validate
    success = validate(labels, predictions)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
