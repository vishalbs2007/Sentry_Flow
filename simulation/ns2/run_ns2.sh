#!/bin/bash
# FlowSentry NS2 Traffic Generation - Linux/Mac Script
# This automates the entire NS2 -> PCAP -> Classification pipeline

set -e  # Exit on error

SKIP_NS2=false
VALIDATE_ONLY=false
OUTPUT_DIR="simulation/pcaps"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-ns2)
            SKIP_NS2=true
            shift
            ;;
        --validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-ns2] [--validate-only] [--output-dir DIR]"
            exit 1
            ;;
    esac
done

echo ""
echo "====================================="
echo "  FlowSentry NS2 Integration"
echo "====================================="
echo ""

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "[INFO] Project root: $PROJECT_ROOT"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[WARN] Virtual environment not activated. Activating..."
    source .venv/bin/activate || source .venv/Scripts/activate
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Step 1: Run NS2 Simulation
if [ "$SKIP_NS2" = false ] && [ "$VALIDATE_ONLY" = false ]; then
    echo ""
    echo "Step 1: NS2 Simulation"
    echo "======================"
    
    NS2_AVAILABLE=false
    
    # Check for NS2
    if command -v ns &> /dev/null; then
        NS2_AVAILABLE=true
        echo "[INFO] NS2 found: Using native 'ns' command"
    else
        echo "[WARN] NS2 not found in PATH"
    fi
    
    # Try Docker
    if [ "$NS2_AVAILABLE" = false ]; then
        if command -v docker &> /dev/null; then
            if docker images hbhzwj/ns2 | grep -q ns2; then
                NS2_AVAILABLE=true
                echo "[INFO] NS2 found: Using Docker"
            fi
        fi
    fi
    
    if [ "$NS2_AVAILABLE" = true ]; then
        echo "[RUN] Executing: ns flowsentry.tcl"
        
        if command -v ns &> /dev/null; then
            ns flowsentry.tcl
        else
            docker run -v "$(pwd):/work" -w /work hbhzwj/ns2 ns flowsentry.tcl
        fi
        
        if [ -f "out.tr" ]; then
            TR_SIZE=$(du -h out.tr | cut -f1)
            echo "[OK] NS2 simulation complete! Generated out.tr ($TR_SIZE)"
        else
            echo "[ERROR] NS2 simulation failed - out.tr not created"
            exit 1
        fi
    else
        echo ""
        echo "[SKIP] NS2 not available. Options:"
        echo "  1. Install NS2: sudo apt-get install ns2"
        echo "  2. Use Docker: docker pull hbhzwj/ns2"
        echo "  3. Use pre-generated files with --skip-ns2 flag"
        echo ""
        echo "[INFO] Checking for existing out.tr..."
        
        if [ ! -f "out.tr" ]; then
            echo "[ERROR] No out.tr file found. Cannot proceed."
            echo "[INFO] Please generate out.tr or use pre-generated PCAPs"
            exit 1
        else
            echo "[OK] Using existing out.tr file"
        fi
    fi
fi

# Step 2: Convert to PCAP
if [ "$VALIDATE_ONLY" = false ]; then
    echo ""
    echo "Step 2: Convert NS2 Trace to PCAP"
    echo "=================================="
    
    if [ ! -f "out.tr" ]; then
        echo "[ERROR] out.tr not found. Run with NS2 first or check file location."
        exit 1
    fi
    
    PCAP_PATH="$OUTPUT_DIR/ns2_traffic.pcap"
    echo "[RUN] Executing: python tr_to_pcap.py out.tr $PCAP_PATH"
    
    python tr_to_pcap.py out.tr "$PCAP_PATH"
    
    if [ -f "$PCAP_PATH" ]; then
        PCAP_SIZE=$(du -h "$PCAP_PATH" | cut -f1)
        echo "[OK] Conversion complete! Generated $PCAP_PATH ($PCAP_SIZE)"
        
        # Check for labels file
        LABELS_PATH="$OUTPUT_DIR/ns2_traffic_labels.csv"
        if [ -f "$LABELS_PATH" ]; then
            LABEL_COUNT=$(( $(wc -l < "$LABELS_PATH") - 1 ))
            echo "[OK] Ground truth labels: $LABELS_PATH ($LABEL_COUNT flows)"
        fi
    else
        echo "[ERROR] PCAP conversion failed"
        exit 1
    fi
fi

# Step 3: Classify with FlowSentry
echo ""
echo "Step 3: Classify Traffic with FlowSentry"
echo "========================================="

PCAP_PATH="$OUTPUT_DIR/ns2_traffic.pcap"
OUTPUT_PATH="artifacts/ns2_demo"

if [ ! -f "$PCAP_PATH" ]; then
    echo "[ERROR] PCAP file not found: $PCAP_PATH"
    echo "[INFO] Run without --validate-only first to generate PCAP"
    exit 1
fi

echo "[RUN] Executing: python -m inference.pcap_classifier --pcap $PCAP_PATH --output $OUTPUT_PATH"

python -m inference.pcap_classifier --pcap "$PCAP_PATH" --output "$OUTPUT_PATH"

if [ $? -eq 0 ]; then
    echo "[OK] Classification complete!"
    
    # Display results
    RESULTS_FILE="$OUTPUT_PATH/classification_results.txt"
    if [ -f "$RESULTS_FILE" ]; then
        echo ""
        echo "========== CLASSIFICATION RESULTS =========="
        cat "$RESULTS_FILE"
        echo "============================================"
    fi
else
    echo "[ERROR] Classification failed"
    exit 1
fi

# Step 4: Validation
echo ""
echo "Step 4: Validate Against Ground Truth"
echo "======================================"

LABELS_PATH="$OUTPUT_DIR/ns2_traffic_labels.csv"
if [ -f "$LABELS_PATH" ]; then
    echo "[RUN] Comparing predictions with ground truth..."
    
    python simulation/ns2/validate.py "$OUTPUT_PATH/classification_results.txt" "$LABELS_PATH"
    
    if [ $? -eq 0 ]; then
        echo "[OK] Validation complete!"
    else
        echo "[WARN] Validation encountered issues (this is normal for probabilistic models)"
    fi
else
    echo "[SKIP] No ground truth labels found. Skipping validation."
fi

# Summary
echo ""
echo "====================================="
echo "  Pipeline Complete!"
echo "====================================="
echo ""
echo "Generated Files:"
echo "  - Trace:    out.tr"
echo "  - PCAP:     $PCAP_PATH"
echo "  - Labels:   $LABELS_PATH"
echo "  - Results:  $OUTPUT_PATH/"
echo ""
echo "Next Steps:"
echo "  1. Check classification results: cat $OUTPUT_PATH/classification_results.txt"
echo "  2. View PCAP in Wireshark: wireshark $PCAP_PATH"
echo "  3. Compare with labels: cat $LABELS_PATH"
echo ""
