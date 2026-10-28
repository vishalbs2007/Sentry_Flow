#!/usr/bin/env python3
"""Simple test of Scapy extractor without CICFlowMeter."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing Scapy extractor...")

try:
    from flow.scapy_extractor import ScapyFlowExtractor
    from scapy.all import IP, TCP, wrpcap, Ether
    
    # Create test PCAP
    print("1. Creating test PCAP...")
    test_pcap = Path("data/sample/scapy_test.pcap")
    test_pcap.parent.mkdir(parents=True, exist_ok=True)
    
    packets = [
        Ether() / IP(src="192.168.1.100", dst="10.0.0.1") / TCP(sport=12345, dport=80)
        for _ in range(5)
    ]
    
    wrpcap(str(test_pcap), packets)
    print(f"   Created: {test_pcap}")
    
    # Extract with Scapy
    print("\n2. Extracting flows...")
    extractor = ScapyFlowExtractor()
    csv_path = extractor.extract(test_pcap, Path("data/sample"))
    
    print(f"   CSV created: {csv_path}")
    
    # Read results
    import pandas as pd
    df = pd.read_csv(csv_path)
    
    print(f"\n✅ SUCCESS!")
    print(f"   Flows: {len(df)}")
    print(f"   Features: {len(df.columns)}")
    print(f"   Columns: {list(df.columns[:5])}")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
