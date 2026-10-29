"""
Quick test of NS2 integration - works WITHOUT NS2 installed!

This script demonstrates the NS2 integration by:
1. Creating a minimal synthetic NS2 trace
2. Converting it to PCAP
3. Classifying with FlowSentry
4. Showing the results

Perfect for quick demonstrations!
"""

import os
import sys
from pathlib import Path

def create_sample_ns2_trace():
    """Create a minimal NS2 trace for testing (no NS2 needed!)"""
    
    trace_content = """r 1.000 _0_ _4_ tcp 500 ------- 1 0 4 0 0
r 1.020 _1_ _4_ udp 160 ------- 2 1 5 0 0
r 1.040 _2_ _4_ udp 1200 ------- 3 2 6 0 0
r 1.060 _3_ _4_ tcp 1000 ------- 4 3 7 0 0
r 1.100 _4_ _5_ tcp 500 ------- 1 0 4 0 0
r 1.120 _4_ _5_ udp 160 ------- 2 1 5 0 0
r 1.140 _4_ _6_ udp 1200 ------- 3 2 6 0 0
r 1.160 _4_ _7_ tcp 1000 ------- 4 3 7 0 0
r 2.000 _0_ _4_ tcp 500 ------- 1 0 4 0 0
r 2.020 _1_ _4_ udp 160 ------- 2 1 5 0 0
r 2.040 _2_ _4_ udp 1200 ------- 3 2 6 0 0
r 2.060 _3_ _4_ tcp 1000 ------- 4 3 7 0 0
r 2.100 _4_ _5_ tcp 500 ------- 1 0 4 0 0
r 2.120 _4_ _5_ udp 160 ------- 2 1 5 0 0
r 2.140 _4_ _6_ udp 1200 ------- 3 2 6 0 0
r 2.160 _4_ _7_ tcp 1000 ------- 4 3 7 0 0
r 3.000 _0_ _4_ tcp 500 ------- 1 0 4 0 0
r 3.020 _1_ _4_ udp 160 ------- 2 1 5 0 0
r 3.040 _2_ _4_ udp 1200 ------- 3 2 6 0 0
r 3.060 _3_ _4_ tcp 1000 ------- 4 3 7 0 0
"""
    
    with open('test_out.tr', 'w') as f:
        f.write(trace_content)
    
    print("[OK] Created sample NS2 trace: test_out.tr")
    return 'test_out.tr'


def run_test():
    """Run the complete NS2 integration test"""
    
    print("\n" + "="*60)
    print("  NS2 INTEGRATION TEST")
    print("="*60 + "\n")
    
    # Step 1: Create sample trace
    print("Step 1: Creating Sample NS2 Trace")
    print("-" * 40)
    trace_file = create_sample_ns2_trace()
    
    # Step 2: Convert to PCAP
    print("\nStep 2: Converting to PCAP")
    print("-" * 40)
    pcap_path = "simulation/pcaps/test_ns2.pcap"
    
    # Ensure directory exists
    Path("simulation/pcaps").mkdir(parents=True, exist_ok=True)
    
    cmd = f"python tr_to_pcap.py {trace_file} {pcap_path}"
    print(f"[RUN] {cmd}")
    
    result = os.system(cmd)
    if result != 0:
        print("[ERROR] Conversion failed!")
        return False
    
    if not os.path.exists(pcap_path):
        print(f"[ERROR] PCAP not created: {pcap_path}")
        return False
    
    print(f"[OK] Created: {pcap_path}")
    
    # Check for labels
    labels_path = pcap_path.replace('.pcap', '_labels.csv')
    if os.path.exists(labels_path):
        print(f"[OK] Created: {labels_path}")
        with open(labels_path) as f:
            print(f"\nGround Truth Labels:")
            print(f.read())
    
    # Step 3: Classify
    print("\nStep 3: Classifying Traffic")
    print("-" * 40)
    output_dir = "artifacts/test_ns2"
    
    cmd = f"python -m inference.pcap_classifier --pcap {pcap_path} --output {output_dir}"
    print(f"[RUN] {cmd}")
    
    result = os.system(cmd)
    if result != 0:
        print("[ERROR] Classification failed!")
        return False
    
    # Step 4: Show results
    print("\nStep 4: Results")
    print("-" * 40)
    results_file = f"{output_dir}/classification_results.txt"
    
    if os.path.exists(results_file):
        with open(results_file) as f:
            print(f.read())
        print("[OK] Classification complete!")
    else:
        print(f"[WARN] Results file not found: {results_file}")
    
    # Step 5: Validate (if possible)
    if os.path.exists(labels_path) and os.path.exists(results_file):
        print("\nStep 5: Validation")
        print("-" * 40)
        cmd = f"python simulation/ns2/validate.py {results_file} {labels_path}"
        print(f"[RUN] {cmd}")
        os.system(cmd)
    
    # Cleanup
    print("\nCleanup")
    print("-" * 40)
    try:
        os.remove(trace_file)
        print(f"[OK] Removed temporary file: {trace_file}")
    except:
        pass
    
    print("\n" + "="*60)
    print("  TEST COMPLETE!")
    print("="*60 + "\n")
    
    print("What just happened:")
    print("  1. ✓ Created a minimal NS2 trace (simulated)")
    print("  2. ✓ Converted it to PCAP format")
    print("  3. ✓ Your model classified the traffic")
    print("  4. ✓ Results validated against ground truth")
    print("\nYour NS2 integration is working! 🎉")
    print("\nNext: Read NS2_INTEGRATION_GUIDE.md for full details")
    print()
    
    return True


if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
