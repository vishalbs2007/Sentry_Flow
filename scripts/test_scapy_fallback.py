#!/usr/bin/env python3
"""
Quick test of Scapy fallback extractor (bypasses CICFlowMeter).
"""

from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flow.cicflowmeter_adapter import CICFlowMeterAdapter
from scapy.all import IP, TCP, wrpcap, Ether

print("=" * 70)
print("TESTING SCAPY FALLBACK EXTRACTOR")
print("=" * 70)

# Create minimal test PCAP
print("\n1. Creating minimal test PCAP...")
test_pcap = Path("data/sample/minimal_test.pcap")
test_pcap.parent.mkdir(parents=True, exist_ok=True)

packets = []
for i in range(5):
    pkt = Ether() / IP(src="192.168.1.100", dst="10.0.0.1") / TCP(sport=12345, dport=80)
    packets.append(pkt)

wrpcap(str(test_pcap), packets)
print(f"✅ Created: {test_pcap} ({len(packets)} packets)")

# Test with adapter (should fallback to Scapy)
print("\n2. Testing CICFlowMeterAdapter (will fallback to Scapy)...")
try:
    adapter = CICFlowMeterAdapter()
    print(f"   Adapter: {adapter}")
    
    print(f"   Extracting flows from {test_pcap}...")
    df = adapter.extract_flows(test_pcap)
    
    print(f"\n✅ SUCCESS!")
    print(f"   Extracted {len(df)} flows")
    print(f"   Features: {len(df.columns)} columns")
    print(f"\n   Columns: {', '.join(df.columns[:10])}...")
    
    if len(df) > 0:
        print(f"\n   First flow:")
        for col in list(df.columns)[:10]:
            print(f"      {col}: {df[col].iloc[0]}")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ SCAPY FALLBACK WORKING!")
print("=" * 70)
print("\nYou can now use PCAP classification WITHOUT WinDump!")
print("The system automatically falls back to pure-Python extraction.")
