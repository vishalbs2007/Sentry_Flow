"""Convert an NS-2 trace (out.tr) to a PCAP FlowSentry can read.

Packets are taken where they arrive at the router (one record per packet, so
nothing is counted twice). Headers are synthesised from the trace; see notes.

Usage: python tr_to_pcap.py out.tr out.pcap [--router 4]
"""
import argparse
from scapy.all import Ether, IP, TCP, UDP, Raw, wrpcap

# fid -> (class name, protocol, server port)
FLOWS = {1: ("Web Browsing", "tcp", 80), 2: ("VoIP", "udp", 5004),
         3: ("Streaming", "udp", 5005), 4: ("File Transfer", "tcp", 21)}


def node_ip(n):
    # clients 0-3 -> 10.0.0.10-13 ; servers 5-8 -> 10.0.1.100-103
    return f"10.0.0.{10 + n}" if n <= 3 else f"10.0.1.{100 + (n - 5)}"


def convert(tr_path, pcap_path, router):
    pkts, labels = [], {}
    with open(tr_path) as f:
        for line in f:
            p = line.split()
            if len(p) < 12 or p[0] != "r":
                continue
            # Handle both formats: "_4_" and "4"
            dst_node = p[3].strip('_')
            try:
                if int(dst_node) != router:
                    continue                                   # only arrivals at router
            except ValueError:
                continue
            t, ptype, size, fid = float(p[1]), p[4], int(p[5]), int(p[7])
            if fid not in FLOWS:
                continue
            # Handle both formats for source/dest: "_0_" and "0"
            src_str = p[8].strip('_')
            dst_str = p[9].strip('_')
            src, dst = int(float(src_str)), int(float(dst_str))
            cls, proto, sport_srv = FLOWS[fid]
            to_server = src <= 3
            cport = 40000 + fid
            sp, dp = (cport, sport_srv) if to_server else (sport_srv, cport)
            ip = IP(src=node_ip(src), dst=node_ip(dst))
            if proto == "tcp":
                payload = 0 if ptype == "ack" else max(size - 40, 0)
                flags = "A" if payload == 0 else "PA"
                l4 = TCP(sport=sp, dport=dp, flags=flags)
            else:
                payload = size
                l4 = UDP(sport=sp, dport=dp)
            pkt = Ether() / ip / l4 / Raw(b"\x00" * payload)
            pkt.time = t
            pkts.append(pkt)
            labels[(node_ip(src if to_server else dst), cport, sport_srv, proto)] = cls
    wrpcap(pcap_path, pkts)
    with open(pcap_path.rsplit(".", 1)[0] + "_labels.csv", "w") as f:
        f.write("client_ip,client_port,server_port,proto,true_class\n")
        for (ip, cp, sp, pr), cls in labels.items():
            f.write(f"{ip},{cp},{sp},{pr},{cls}\n")
    return len(pkts), labels


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("trace"); ap.add_argument("pcap")
    ap.add_argument("--router", type=int, default=4)
    a = ap.parse_args()
    n, lab = convert(a.trace, a.pcap, a.router)
    print(f"Wrote {n} packets, {len(lab)} flows -> {a.pcap}")
