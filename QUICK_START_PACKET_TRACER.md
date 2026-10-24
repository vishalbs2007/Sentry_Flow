# 🚀 FlowSentry + Packet Tracer - Quick Reference

**30-Minute Setup | 10-Minute Demo**

---

## ⚡ Super Quick Start

### 1. Build Topology (10 min)

```
Drag to workspace:
• 1 Router (2911)      → Label: R1
• 1 Switch (2960-24TT) → Label: SW1  
• 4 PCs                → Label: PC-Web, PC-VoIP, PC-Stream, PC-FTP
• 4 Servers            → Label: Server-Web, Server-VoIP, Server-Stream, Server-FTP

Connect with Copper Straight-Through:
• R1 Gi0/0 ↔ SW1 Gi0/1
• All 4 PCs Fa0 ↔ SW1 Fa0/1-4
• All 4 Servers Fa0 ↔ R1 Gi0/1, Gi0/2, Fa0/0/0, Fa0/0/1
```

### 2. Configure IPs (10 min)

**Router R1 (Config tab):**
- Gi0/0: 10.0.0.1 / 255.255.255.0 (On)
- Gi0/1: 10.0.1.1 / 255.255.255.0 (On)

**Clients (Desktop → IP Configuration → Static):**
- PC-Web: 10.0.0.10 | Gateway: 10.0.0.1
- PC-VoIP: 10.0.0.11 | Gateway: 10.0.0.1
- PC-Stream: 10.0.0.12 | Gateway: 10.0.0.1
- PC-FTP: 10.0.0.13 | Gateway: 10.0.0.1

**Servers (Desktop → IP Configuration → Static):**
- Server-Web: 10.0.1.100 | Gateway: 10.0.1.1
- Server-VoIP: 10.0.1.101 | Gateway: 10.0.1.1
- Server-Stream: 10.0.1.102 | Gateway: 10.0.1.1
- Server-FTP: 10.0.1.103 | Gateway: 10.0.1.1

**Test:** `ping 10.0.0.1` from PC-Web ✓

### 3. Enable Services (5 min)

- Server-Web: Services → HTTP (On)
- Server-FTP: Services → FTP (On, User: cisco/cisco)

### 4. Generate Traffic (5 min)

| PC | Action | Traffic Type |
|----|--------|--------------|
| PC-Web | Web Browser → `http://10.0.1.100` | 🌐 Web Browsing |
| PC-VoIP | Command: `ping 10.0.1.101 -t` | 📞 VoIP (simulated) |
| PC-Stream | Command: `ping 10.0.1.102 -l 1400 -t` | 🎬 Streaming |
| PC-FTP | Command: `ftp 10.0.1.103` (cisco/cisco) | 📁 File Transfer |

---

## 🎓 Viva Demo Script (10 min)

### Minute 1-2: Introduce
> "FlowSentry classifies network traffic using ML on flow-level features, without payload inspection. Here's the network topology..."

**Show:** Packet Tracer topology

### Minute 3-6: Generate Traffic
> "Let me demonstrate each traffic type..."

**Enable Simulation Mode** → Generate all 4 traffic types → Show packets flowing

### Minute 7-8: Explain Features
> "Each traffic type has distinctive patterns in timing and size..."

**Show:** Feature importance chart from dashboard

### Minute 9-10: ML Results
> "Our Decision Tree model achieves 99.92% F1 score..."

**Show:** Dashboard (http://localhost:5000) → Models tab

---

## 📊 Traffic Characteristics Cheat Sheet

| Type | IAT | Packet Size | Pattern | Duration |
|------|-----|-------------|---------|----------|
| 🌐 Web | Variable (high) | 200-800B | Bursty | 2-10s |
| 📞 VoIP | Regular (20ms) | 160-200B | Constant | 20-30s+ |
| 🎬 Stream | Medium | 800-1400B | Sustained | 30-60s+ |
| 📁 FTP | Very low (1-5ms) | 1400-1500B | Bulk | 10-30s |

**Key Insight:** Timing features (IAT) are most important for classification!

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Ping fails | Check cables (green triangles), verify IPs, check gateway |
| Service doesn't respond | Services tab → Toggle Off/On |
| No simulation packets | Edit Filters → Check ICMP, HTTP, TCP |

---

## 🔗 Complete Guides

- **Detailed Setup:** `docs/PACKET_TRACER_DEMO.md`
- **Topology Reference:** `docs/NETWORK_TOPOLOGY.md`
- **Original Guide:** `docs/packet_tracer_guide.md`

---

## 💻 FlowSentry Dashboard

```powershell
cd d:\Sentry_Flow
python -m dashboard.app
```

**Open:** http://localhost:5000

**Tabs:**
- 📈 Overview - Project intro
- 📁 Dataset - 59,621 samples, 4 classes
- 🤖 Models - 4 models trained, performance comparison
- 🔍 Features - Timing features dominate
- 🌐 Network - This topology explained!

---

## ✅ Pre-Viva Checklist

- [ ] Topology built & tested ✓
- [ ] All pings work ✓
- [ ] Services respond ✓
- [ ] Simulation mode shows packets ✓
- [ ] Dashboard runs ✓
- [ ] Demo practiced (< 15 min) ✓

---

## 🎯 Key Points to Emphasize

1. **Privacy-Preserving:** No payload inspection
2. **Encryption-Friendly:** Works with HTTPS
3. **ML-Powered:** 99.92% accuracy
4. **Flow-Based:** Timing + size patterns
5. **Realistic:** Real protocols in Packet Tracer

---

**Need Help?**
- Full guide: `docs/PACKET_TRACER_DEMO.md`
- Network details: `docs/NETWORK_TOPOLOGY.md`
- Cisco guide: `docs/packet_tracer_guide.md`

**Good luck! 🎓🚀**
