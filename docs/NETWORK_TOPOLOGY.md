# 🌐 FlowSentry Network Topology Reference

**Visual guide for Cisco Packet Tracer implementation**

---

## 📊 Complete Network Diagram

```
                    FLOWSENTRY NETWORK TOPOLOGY
                    ===========================

    CLIENT NETWORK (10.0.0.0/24)          SERVER NETWORK (10.0.1.0/24)
    ─────────────────────────────         ─────────────────────────────

         PC-Web                                Server-Web
        10.0.0.10                              10.0.1.100
           │                                       │
           │ Fa0                                Fa0│
           │                                       │
        ┌──▼───┐                              ┌───▼──┐
        │  Fa  │                              │  Gi  │
        │ 0/1  │                              │ 0/1  │
        └──────┘                              └──────┘
                                                  │
         PC-VoIP                                  │
        10.0.0.11                                 │
           │                                      │
           │ Fa0                                  │
           │                                      │
        ┌──▼───┐                                  │
        │  Fa  │                                  │
        │ 0/2  │      ┌──────────┐         ┌─────▼────┐
        └──────┘      │          │         │          │
                      │  Switch  │         │  Router  │
                      │   SW1    │         │    R1    │
         PC-Stream    │          │  Gi0/1  │          │
        10.0.0.12     │  2960    ◄─────────┤  2911    │
           │          │  24TT    │         │          │
           │ Fa0      │          │         │          │
           │          └──────────┘         └──────────┘
        ┌──▼───┐                                  │
        │  Fa  │                                  │
        │ 0/3  │                              Gi0/2│
        └──────┘                                  │
                                                  │
         PC-FTP                               ┌───▼──┐
        10.0.0.13                             │  Fa0 │
           │                                  │      │
           │ Fa0                         Server-VoIP
           │                              10.0.1.101
        ┌──▼───┐
        │  Fa  │                         (Additional servers:
        │ 0/4  │                          Server-Stream: 10.0.1.102
        └──────┘                          Server-FTP: 10.0.1.103)


LEGEND:
━━━━━  Physical Connection
  │    Interface Connection
Gi     GigabitEthernet
Fa     FastEthernet
```

---

## 📋 IP Addressing Table

| Device | Interface | IP Address | Subnet Mask | Default Gateway |
|--------|-----------|------------|-------------|-----------------|
| **R1** | Gi0/0 | 10.0.0.1 | 255.255.255.0 | N/A (router) |
| **R1** | Gi0/1 | 10.0.1.1 | 255.255.255.0 | N/A (router) |
| **SW1** | - | N/A | N/A | N/A (L2 switch) |
| **PC-Web** | Fa0 | 10.0.0.10 | 255.255.255.0 | 10.0.0.1 |
| **PC-VoIP** | Fa0 | 10.0.0.11 | 255.255.255.0 | 10.0.0.1 |
| **PC-Stream** | Fa0 | 10.0.0.12 | 255.255.255.0 | 10.0.0.1 |
| **PC-FTP** | Fa0 | 10.0.0.13 | 255.255.255.0 | 10.0.0.1 |
| **Server-Web** | Fa0 | 10.0.1.100 | 255.255.255.0 | 10.0.1.1 |
| **Server-VoIP** | Fa0 | 10.0.1.101 | 255.255.255.0 | 10.0.1.1 |
| **Server-Stream** | Fa0 | 10.0.1.102 | 255.255.255.0 | 10.0.1.1 |
| **Server-FTP** | Fa0 | 10.0.1.103 | 255.255.255.0 | 10.0.1.1 |

---

## 🔌 Connection Matrix

### Switch SW1 Connections

| Port | Connected To | Device Type |
|------|-------------|-------------|
| Gi0/1 | R1 Gi0/0 | Router |
| Fa0/1 | PC-Web Fa0 | Client |
| Fa0/2 | PC-VoIP Fa0 | Client |
| Fa0/3 | PC-Stream Fa0 | Client |
| Fa0/4 | PC-FTP Fa0 | Client |

### Router R1 Connections

| Port | Connected To | Network |
|------|-------------|---------|
| Gi0/0 | SW1 Gi0/1 | Client Network (10.0.0.0/24) |
| Gi0/1 | Server-Web Fa0 | Server Network (10.0.1.0/24) |
| Gi0/2 | Server-VoIP Fa0 | Alternative server connection |

---

## 🚦 Traffic Flow Diagrams

### Web Browsing Traffic (HTTP)

```
PC-Web ──HTTP GET──> SW1 ──> R1 ──> Server-Web
       ◄─HTTP 200─── SW1 ◄─ R1 ◄── (HTML page)

Flow Characteristics:
• Protocol: HTTP (Port 80)
• Pattern: Request-Response
• Packet Size: Small-Medium (64-1500 bytes)
• Timing: Bursty (requests with pauses)
• Duration: Short (seconds)
• IAT: Variable (human-paced)
```

### VoIP Traffic (SIP/RTP)

```
PC-VoIP ══SIP INVITE══> SW1 ──> R1 ──> Server-VoIP
        ◄═SIP 200 OK══ SW1 ◄─ R1 ◄──
        ══════RTP═════> SW1 ──> R1 ──> (bidirectional)
        ◄═════RTP═════ SW1 ◄─ R1 ◄──

Flow Characteristics:
• Protocol: SIP (Port 5060) + RTP (dynamic)
• Pattern: Constant rate
• Packet Size: Small (160-200 bytes)
• Timing: Regular (20ms intervals)
• Duration: Medium-Long (20-30s+)
• IAT: Highly regular (low variance)
```

### Streaming Traffic (RTSP/HTTP)

```
PC-Stream ──RTSP SETUP──> SW1 ──> R1 ──> Server-Stream
          ◄─RTSP 200────── SW1 ◄─ R1 ◄──
          ══VIDEO DATA═══> SW1 ──> R1 ──> (sustained)
          ◄═════ACKs═════ SW1 ◄─ R1 ◄──

Flow Characteristics:
• Protocol: RTSP (Port 554) or HTTP (Port 80)
• Pattern: Sustained throughput
• Packet Size: Medium-Large (500-1500 bytes)
• Timing: Buffer-based (bursts)
• Duration: Long (30-45s+)
• IAT: Low variance, sustained
```

### File Transfer Traffic (FTP)

```
PC-FTP ──FTP CONNECT──> SW1 ──> R1 ──> Server-FTP
       ◄─FTP 220────── SW1 ◄─ R1 ◄── (welcome)
       ──FTP USER───> SW1 ──> R1 ──>
       ──FTP RETR───> SW1 ──> R1 ──>
       ◄═FILE DATA══ SW1 ◄─ R1 ◄══ (bulk transfer)

Flow Characteristics:
• Protocol: FTP (Port 21 control, 20 data)
• Pattern: Bulk transfer
• Packet Size: Large (1400-1500 bytes)
• Timing: Window-based (TCP flow control)
• Duration: Medium (15-20s)
• IAT: Minimal (back-to-back packets)
```

---

## 📊 Service Configuration Summary

### Server-Web (10.0.1.100)

```
Services Enabled:
✓ HTTP (Port 80)
  - Index page: Custom FlowSentry test page
  - Documents: Multiple HTML pages for testing
  
Configuration:
• Service: ON
• Port: 80 (default)
• Root: /html/
```

### Server-VoIP (10.0.1.101)

```
Services Enabled:
✓ VoIP/SIP (Port 5060)
  - SIP registrar enabled
  - RTP ports: 16384-32767
  
Configuration:
• Service: ON (if available in Packet Tracer)
• Alternative: Use IP Phone devices
```

### Server-Stream (10.0.1.102)

```
Services Enabled:
✓ HTTP (Port 80) - Simulating streaming
  - Large video files
  - Sustained delivery
  
Configuration:
• Service: ON
• Simulated with continuous HTTP GET
```

### Server-FTP (10.0.1.103)

```
Services Enabled:
✓ FTP (Port 21)
  - User: cisco
  - Password: cisco
  - Write permission: Enabled
  
Configuration:
• Service: ON
• Port: 21 (control), 20 (data)
• Anonymous: Disabled
• Users: cisco/cisco
```

---

## 🎯 Feature Extraction Points

### What FlowSentry Extracts from This Traffic

```
NETWORK CAPTURE
      │
      ▼
  ┌───────────────────────┐
  │  Packet Sniffer       │  ← Captures all packets
  │  (e.g., Wireshark)    │     at router/switch level
  └──────────┬────────────┘
             │
             ▼
  ┌───────────────────────┐
  │  Flow Grouping        │  ← Groups packets by 5-tuple:
  │  (5-Tuple)            │     (src_ip, dst_ip, src_port,
  └──────────┬────────────┘      dst_port, protocol)
             │
             ▼
  ┌───────────────────────┐
  │  Feature Extraction   │  ← Computes statistics:
  │  (CICFlowMeter)       │     • Flow duration
  └──────────┬────────────┘     • Inter-Arrival Time (IAT)
             │                   • Packet sizes (fwd/bwd)
             │                   • Throughput
             ▼                   • TCP flags
  ┌───────────────────────┐     • Flow bytes/packets
  │  Feature Vector       │     • Directional ratios
  │  (9 selected)         │
  └──────────┬────────────┘
             │
             ▼
  ┌───────────────────────┐
  │  ML Model             │  ← Decision Tree, RF, SVM, XGBoost
  │  (Trained)            │     Trained on ISCX-VPN2016
  └──────────┬────────────┘
             │
             ▼
  ┌───────────────────────┐
  │  Classification       │  ← Output: Web, VoIP, Streaming, FTP
  │  Result               │
  └───────────────────────┘
```

---

## 🔬 Distinguishing Features by Traffic Type

### Web Browsing
```
Key Features:
✓ High IAT variance (human-paced)
✓ Small-medium packets
✓ Request-response pattern
✓ Short flow duration
✓ Low packets per second

Example Values:
• Mean IAT: 500-2000ms
• Packet size: 200-800 bytes
• Duration: 2-10s
• Flow bytes: 10-100 KB
```

### VoIP
```
Key Features:
✓ Low IAT variance (regular)
✓ Small packets (voice codec)
✓ Constant rate
✓ Bidirectional
✓ High packets per second

Example Values:
• Mean IAT: 20ms (±2ms)
• Packet size: 160-200 bytes
• Duration: 20-30s+
• Flow bytes: 100-500 KB
```

### Streaming
```
Key Features:
✓ Medium IAT variance
✓ Large packets
✓ Sustained throughput
✓ Forward-heavy (server→client)
✓ Medium packets per second

Example Values:
• Mean IAT: 10-50ms
• Packet size: 800-1400 bytes
• Duration: 30-60s+
• Flow bytes: 1-10 MB
```

### File Transfer
```
Key Features:
✓ Very low IAT (back-to-back)
✓ Maximum packet size (MTU)
✓ Bulk transfer
✓ TCP window-based
✓ High packets per second

Example Values:
• Mean IAT: 1-5ms
• Packet size: 1400-1500 bytes
• Duration: 10-30s
• Flow bytes: 500KB-10MB
```

---

## 🧪 Verification Tests

### Test 1: Connectivity
```
From PC-Web Command Prompt:
ping 10.0.0.1     → Router (should succeed)
ping 10.0.1.100   → Web Server (should succeed)
ping 10.0.0.11    → PC-VoIP (should succeed)
```

### Test 2: Services
```
From PC-Web:
• Web Browser → http://10.0.1.100 (should load page)

From PC-FTP:
• Command Prompt → ftp 10.0.1.103 (should connect)
• Login: cisco/cisco (should authenticate)
```

### Test 3: Traffic Visibility
```
In Packet Tracer:
1. Enable Simulation Mode
2. Generate traffic (ping)
3. Verify packets visible in Event List
4. Check packet details show correct src/dst
```

---

## 📖 Integration with FlowSentry

### How This Topology Connects to ML Pipeline

```
PACKET TRACER           →    FLOWSENTRY
────────────────             ──────────────

1. Generate Traffic     →    1. Capture packets (Wireshark/tshark)
   (4 types)                    at network interface

2. Packets flow         →    2. Export PCAP file
   through router               traffic_capture.pcap

3. Simulation shows     →    3. Extract flows (CICFlowMeter)
   packet details               PCAP → CSV features

4. Services active      →    4. Preprocess features
                                Scaling, selection

                         →    5. Load trained model
                                (Decision Tree: 99.92% F1)

                         →    6. Classify flows
                                Predict: Web, VoIP, etc.

                         →    7. Display results
                                Dashboard visualization
```

---

## 💡 Tips for Viva Presentation

### What to Highlight

1. **Realistic Network:**
   - Router provides gateway/routing
   - Switch provides Layer 2 connectivity
   - Separate subnets for clients and servers

2. **Traffic Diversity:**
   - Each client generates different traffic type
   - Different protocols (HTTP, SIP, FTP)
   - Different patterns (bursty, constant, sustained, bulk)

3. **Feature-Based Classification:**
   - No payload inspection needed
   - Flow statistics are sufficient
   - Works with encrypted traffic

4. **ML Integration:**
   - This network generates training/test data
   - Real-world deployment would use same features
   - High accuracy (99.92%) proves concept

### Common Questions & Answers

**Q: Why not just use port numbers?**
A: Many apps use non-standard ports, and port-based methods fail with port hopping or encryption.

**Q: How does this work with HTTPS?**
A: We don't inspect payload, only flow patterns (timing, size). Works fine with encryption!

**Q: Why 4 classes?**
A: These represent common network applications with distinct flow behaviors. Extensible to more classes.

**Q: What if new application type?**
A: Retrain model with new labeled data. ML adapts to new patterns.

---

## ✅ Pre-Demo Checklist

- [ ] Topology built correctly
- [ ] All green connection indicators
- [ ] All IPs configured (verify with ping)
- [ ] Services enabled on servers
- [ ] Can browse to Server-Web
- [ ] Can FTP to Server-FTP
- [ ] Simulation mode works
- [ ] Understand each traffic type's characteristics
- [ ] Can explain feature extraction
- [ ] Dashboard ready (http://localhost:5000)
- [ ] Practiced demo (under 15 min)

---

**Total Setup Time:** 30 minutes
**Demonstration Time:** 10-15 minutes
**Difficulty Level:** Beginner-Friendly

**You're ready to demonstrate! 🎓🚀**
