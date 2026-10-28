#!/usr/bin/env python3
"""
Generate a minimal test PCAP file using Scapy for testing CICFlowMeter integration.
This creates synthetic network traffic (no real capture needed).
"""

import sys
from pathlib import Path

try:
    from scapy.all import IP, TCP, UDP, wrpcap
    from scapy.layers.inet import Ether
except ImportError:
    print("❌ Scapy not installed. Install with: pip install scapy")
    sys.exit(1)


def generate_test_pcap(output_path: Path) -> None:
    """
    Generate a minimal PCAP with synthetic flows representing different traffic types.
    
    Args:
        output_path: Path where to save the PCAP file
    """
    print(f"Generating test PCAP: {output_path}")
    
    packets = []
    
    # Flow 1: Web browsing (HTTP) - 10 packets
    # Client 192.168.1.100:45678 → Server 10.0.0.1:80
    print("  Creating Web Browsing flow...")
    for i in range(10):
        # Forward direction (client → server)
        pkt = Ether() / IP(src="192.168.1.100", dst="10.0.0.1") / \
              TCP(sport=45678, dport=80, flags="A", seq=1000+i*100)
        packets.append(pkt)
        
        # Backward direction (server → client)
        pkt = Ether() / IP(src="10.0.0.1", dst="192.168.1.100") / \
              TCP(sport=80, dport=45678, flags="A", seq=2000+i*100)
        packets.append(pkt)
    
    # Flow 2: File Transfer (FTP data) - 20 large packets
    # Client 192.168.1.101:56789 → Server 10.0.0.2:21
    print("  Creating File Transfer flow...")
    for i in range(20):
        pkt = Ether() / IP(src="192.168.1.101", dst="10.0.0.2") / \
              TCP(sport=56789, dport=21, flags="A", seq=3000+i*1400) / \
              ("X" * 1400)  # Large payload
        packets.append(pkt)
        
        pkt = Ether() / IP(src="10.0.0.2", dst="192.168.1.101") / \
              TCP(sport=21, dport=56789, flags="A", seq=4000+i*100)
        packets.append(pkt)
    
    # Flow 3: VoIP-like (UDP, small packets, constant rate)
    # Client 192.168.1.102:12345 → Server 10.0.0.3:5060
    print("  Creating VoIP-like flow...")
    for i in range(30):
        pkt = Ether() / IP(src="192.168.1.102", dst="10.0.0.3") / \
              UDP(sport=12345, dport=5060) / ("V" * 160)  # Small payload
        packets.append(pkt)
        
        pkt = Ether() / IP(src="10.0.0.3", dst="192.168.1.102") / \
              UDP(sport=5060, dport=12345) / ("V" * 160)
        packets.append(pkt)
    
    # Flow 4: Streaming (larger packets, sustained)
    # Client 192.168.1.103:54321 → Server 10.0.0.4:8080
    print("  Creating Streaming flow...")
    for i in range(25):
        pkt = Ether() / IP(src="192.168.1.103", dst="10.0.0.4") / \
              TCP(sport=54321, dport=8080, flags="A", seq=5000+i*1200) / \
              ("S" * 1200)
        packets.append(pkt)
        
        pkt = Ether() / IP(src="10.0.0.4", dst="192.168.1.103") / \
              TCP(sport=8080, dport=54321, flags="A", seq=6000+i*100)
        packets.append(pkt)
    
    # Write PCAP
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output_path), packets)
    
    print(f"✅ Generated {len(packets)} packets in {output_path}")
    print(f"   File size: {output_path.stat().st_size:,} bytes")
    print(f"\nFlows created:")
    print(f"  - Web Browsing: 192.168.1.100 → 10.0.0.1:80 (10 bidirectional)")
    print(f"  - File Transfer: 192.168.1.101 → 10.0.0.2:21 (20 bidirectional)")
    print(f"  - VoIP: 192.168.1.102 → 10.0.0.3:5060 (30 bidirectional)")
    print(f"  - Streaming: 192.168.1.103 → 10.0.0.4:8080 (25 bidirectional)")


if __name__ == "__main__":
    output = Path("data/sample/test_traffic.pcap")
    
    try:
        generate_test_pcap(output)
        print(f"\n🎯 You can now test with:")
        print(f"   python -m inference.pcap_classifier --pcap {output} --output artifacts/test_classification")
    except Exception as e:
        print(f"❌ Error generating PCAP: {e}")
        sys.exit(1)
