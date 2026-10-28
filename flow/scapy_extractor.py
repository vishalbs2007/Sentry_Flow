"""
Pure Python PCAP flow extractor using Scapy directly (no tcpdump dependency).
This is a fallback when CICFlowMeter/WinDump is not available.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import logging

import pandas as pd
from scapy.all import rdpcap, IP, TCP, UDP
from scapy.packet import Packet

from common.errors import ExtractionError

logger = logging.getLogger(__name__)


class ScapyFlowExtractor:
    """
    Extract basic flow features from PCAP using pure Scapy (no tcpdump).
    
    This is a simplified extractor that doesn't require WinDump/tcpdump.
    It provides basic flow statistics compatible with the FlowExtractor protocol.
    """
    
    def __init__(self):
        self.flows: Dict[Tuple[str, int, str, int, int], List[Packet]] = {}
    
    def extract(self, pcap_path: Path, output_dir: Path) -> Path:
        """
        Extract flows from PCAP file.
        
        Args:
            pcap_path: Path to PCAP file
            output_dir: Directory for output CSV
            
        Returns:
            Path to generated CSV file
            
        Raises:
            FlowExtractionError: If extraction fails
        """
        try:
            logger.info(f"Reading PCAP with Scapy: {pcap_path}")
            packets = rdpcap(str(pcap_path))
            
            logger.info(f"Processing {len(packets)} packets...")
            self._process_packets(packets)
            
            logger.info(f"Extracted {len(self.flows)} flows")
            features_df = self._compute_features()
            
            output_dir.mkdir(parents=True, exist_ok=True)
            output_csv = output_dir / f"{pcap_path.stem}_flows.csv"
            features_df.to_csv(output_csv, index=False)
            
            logger.info(f"Saved features to: {output_csv}")
            return output_csv
            
        except Exception as e:
            raise ExtractionError(f"Scapy extraction failed: {e}") from e
    
    def _process_packets(self, packets: List[Packet]) -> None:
        """Group packets into bidirectional flows."""
        for pkt in packets:
            if IP in pkt:
                flow_key = self._get_flow_key(pkt)
                if flow_key:
                    if flow_key not in self.flows:
                        self.flows[flow_key] = []
                    self.flows[flow_key].append(pkt)
    
    def _get_flow_key(self, pkt: Packet) -> Tuple[str, int, str, int, int]:
        """
        Extract five-tuple from packet, normalized for bidirectional flow.
        
        Returns:
            (src_ip, src_port, dst_ip, dst_port, protocol) with src < dst
        """
        if IP not in pkt:
            return None
        
        ip_layer = pkt[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        protocol = ip_layer.proto
        
        src_port = 0
        dst_port = 0
        
        if TCP in pkt:
            src_port = pkt[TCP].sport
            dst_port = pkt[TCP].dport
        elif UDP in pkt:
            src_port = pkt[UDP].sport
            dst_port = pkt[UDP].dport
        
        # Normalize: ensure src < dst for bidirectional flow
        if (src_ip, src_port) > (dst_ip, dst_port):
            src_ip, dst_ip = dst_ip, src_ip
            src_port, dst_port = dst_port, src_port
        
        return (src_ip, src_port, dst_ip, dst_port, protocol)
    
    def _compute_features(self) -> pd.DataFrame:
        """
        Compute basic flow features.
        
        Returns:
            DataFrame with flow features (simplified set)
        """
        features = []
        
        for flow_key, packets in self.flows.items():
            src_ip, src_port, dst_ip, dst_port, protocol = flow_key
            
            # Basic statistics
            n_packets = len(packets)
            total_bytes = sum(len(pkt) for pkt in packets)
            
            # Forward/backward split (simplified: first packet direction is forward)
            if packets:
                first_src = packets[0][IP].src
                fwd_packets = [p for p in packets if p[IP].src == first_src]
                bwd_packets = [p for p in packets if p[IP].src != first_src]
            else:
                fwd_packets = []
                bwd_packets = []
            
            fwd_packet_count = len(fwd_packets)
            bwd_packet_count = len(bwd_packets)
            
            fwd_bytes = sum(len(p) for p in fwd_packets)
            bwd_bytes = sum(len(p) for p in bwd_packets)
            
            # Timing features
            timestamps = [float(pkt.time) for pkt in packets]
            duration = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0
            
            # Inter-arrival times
            iats = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            iat_mean = sum(iats) / len(iats) if iats else 0
            iat_max = max(iats) if iats else 0
            iat_min = min(iats) if iats else 0
            
            # TCP flags (if TCP flow)
            if TCP in packets[0]:
                flags = [pkt[TCP].flags for pkt in packets if TCP in pkt]
                syn_count = sum(1 for f in flags if f & 0x02)  # SYN
                fin_count = sum(1 for f in flags if f & 0x01)  # FIN
                psh_count = sum(1 for f in flags if f & 0x08)  # PSH
                ack_count = sum(1 for f in flags if f & 0x10)  # ACK
            else:
                syn_count = fin_count = psh_count = ack_count = 0
            
            # Build feature dictionary (simplified CICFlowMeter-compatible)
            flow_features = {
                # Basic flow info
                "Src IP": src_ip,
                "Src Port": src_port,
                "Dst IP": dst_ip,
                "Dst Port": dst_port,
                "Protocol": protocol,
                
                # Flow statistics
                "Flow Duration": duration * 1_000_000,  # microseconds
                "Tot Fwd Pkts": fwd_packet_count,
                "Tot Bwd Pkts": bwd_packet_count,
                "TotLen Fwd Pkts": fwd_bytes,
                "TotLen Bwd Pkts": bwd_bytes,
                
                # Packet length features
                "Fwd Pkt Len Max": max((len(p) for p in fwd_packets), default=0),
                "Fwd Pkt Len Min": min((len(p) for p in fwd_packets), default=0),
                "Fwd Pkt Len Mean": fwd_bytes / fwd_packet_count if fwd_packet_count > 0 else 0,
                "Bwd Pkt Len Max": max((len(p) for p in bwd_packets), default=0),
                "Bwd Pkt Len Min": min((len(p) for p in bwd_packets), default=0),
                "Bwd Pkt Len Mean": bwd_bytes / bwd_packet_count if bwd_packet_count > 0 else 0,
                
                # Flow IAT features
                "Flow IAT Mean": iat_mean * 1_000_000,  # microseconds
                "Flow IAT Max": iat_max * 1_000_000,
                "Flow IAT Min": iat_min * 1_000_000,
                
                # TCP flags
                "SYN Flag Cnt": syn_count,
                "FIN Flag Cnt": fin_count,
                "PSH Flag Cnt": psh_count,
                "ACK Flag Cnt": ack_count,
                
                # Packet rate
                "Flow Pkts/s": n_packets / duration if duration > 0 else 0,
                "Flow Bytes/s": total_bytes / duration if duration > 0 else 0,
            }
            
            features.append(flow_features)
        
        return pd.DataFrame(features)


def extract_flows_scapy(pcap_path: Path, output_dir: Path) -> Path:
    """
    Extract flows using Scapy (no tcpdump dependency).
    
    This is a convenience function that creates a ScapyFlowExtractor
    and extracts flows in one call.
    
    Args:
        pcap_path: Path to PCAP file
        output_dir: Directory for output
        
    Returns:
        Path to generated CSV file
    """
    extractor = ScapyFlowExtractor()
    return extractor.extract(pcap_path, output_dir)
