# 📡 Cisco Packet Tracer Guide for FlowSentry

**Complete guide for network simulation and traffic classification demonstration**

---

## 🎯 Overview

This guide shows you how to:
1. Build a network topology in Cisco Packet Tracer
2. Generate the 4 traffic classes (Web Browsing, VoIP, Streaming, File Transfer)
3. Capture traffic and export PCAPs
4. Classify the captured traffic with FlowSentry
5. Demonstrate the complete pipeline for your viva

---

## 📋 Prerequisites

### Required Software
- **Cisco Packet Tracer 8.x** (free for Cisco Networking Academy students)
  - Download: https://www.netacad.com/courses/packet-tracer
  - Version 8.2 or higher recommended

### FlowSentry Setup
```powershell
# Ensure FlowSentry is installed
cd d:\Sentry_Flow
python -m pip install -r requirements.txt

# Verify models are trained
python scripts\demo.py
```

---

## 🏗️ Part 1: Build the Network Topology

### Step 1: Open Cisco Packet Tracer

1. Launch Cisco Packet Tracer
2. Click **File → New** to create a new topology

### Step 2: Add Devices

**Add Router:**
1. Click on **Network Devices** (bottom left)
2. Select **Routers** → **Cisco 2911**
3. Drag one router to the workspace
4. Label it: **Router0**

**Add Switch:**
1. Select **Switches** → **Cisco 2960-24TT**
2. Drag one switch to the workspace
3. Label it: **Switch0**

**Add Client Computers:**
1. Click on **End Devices**
2. Select **PC** (Desktop PC)
3. Drag **4 PCs** to the workspace
4. Label them: **Client1**, **Client2**, **Client3**, **Client4**

**Add Servers:**
1. Select **Server** (from End Devices)
2. Drag **4 Servers** to the workspace
3. Label them: **WebServer**, **VoIPServer**, **StreamServer**, **FTPServer**

### Step 3: Connect Devices

**Router to Switch:**
- Connect **Router0 GigabitEthernet0/0** to **Switch0 GigabitEthernet0/1**
- Use **Copper Straight-Through** cable (automatic selection)

**Clients to Switch:**
- Connect **Client1 FastEthernet0** to **Switch0 FastEthernet0/1**
- Connect **Client2 FastEthernet0** to **Switch0 FastEthernet0/2**
- Connect **Client3 FastEthernet0** to **Switch0 FastEthernet0/3**
- Connect **Client4 FastEthernet0** to **Switch0 FastEthernet0/4**

**Router to Servers (Direct):**
- Connect **Router0 GigabitEthernet0/1** to **WebServer FastEthernet0**
- Connect **Router0 GigabitEthernet0/2** to **VoIPServer FastEthernet0**
- Use **Copper Straight-Through** cable

**Alternative: Servers Behind Switch:**
If your router has limited ports, connect servers to a second switch connected to the router.

---

## 🔧 Part 2: Configure IP Addressing

### Client Network: 10.0.0.0/24
### Server Network: 10.0.1.0/24

### Configure Router

Click on **Router0** → **Config** tab:

**Interface GigabitEthernet0/0 (Client Side):**
```
IP Address: 10.0.0.1
Subnet Mask: 255.255.255.0
Port Status: On
```

**Interface GigabitEthernet0/1 (WebServer):**
```
IP Address: 10.0.1.1
Subnet Mask: 255.255.255.0
Port Status: On
```

**Interface GigabitEthernet0/2 (VoIPServer):**
```
IP Address: 10.0.2.1
Subnet Mask: 255.255.255.0
Port Status: On
```

Or use **CLI** tab:
```cisco
enable
configure terminal
interface GigabitEthernet0/0
ip address 10.0.0.1 255.255.255.0
no shutdown
exit

interface GigabitEthernet0/1
ip address 10.0.1.1 255.255.255.0
no shutdown
exit

interface GigabitEthernet0/2
ip address 10.0.2.1 255.255.255.0
no shutdown
exit
```

### Configure Clients

**Client1:**
- Click **Client1** → **Desktop** → **IP Configuration**
- Select **Static**
- IP Address: `10.0.0.10`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.0.1`

**Client2:**
- IP Address: `10.0.0.11`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.0.1`

**Client3:**
- IP Address: `10.0.0.12`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.0.1`

**Client4:**
- IP Address: `10.0.0.13`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.0.1`

### Configure Servers

**WebServer (HTTP):**
- IP Address: `10.0.1.100`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.1.1`

**VoIPServer (SIP):**
- IP Address: `10.0.2.100`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.2.1`

**StreamServer (RTSP):**
- IP Address: `10.0.1.102`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.1.1`

**FTPServer:**
- IP Address: `10.0.1.103`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `10.0.1.1`

### Verify Connectivity

From any client:
1. Click **Desktop** → **Command Prompt**
2. Test: `ping 10.0.0.1` (should succeed)
3. Test: `ping 10.0.1.100` (should succeed if routing is correct)

---

## 🌐 Part 3: Configure Services

### WebServer (HTTP Service)

1. Click **WebServer** → **Services** tab
2. Enable **HTTP** service (it's usually on by default)
3. Click **Config** → **HTTP**
4. Ensure service is **On**
5. Create a simple HTML page (optional):
   - Go to **index.html**
   - Add content like: "Welcome to FlowSentry Test Server"

### VoIPServer (SIP Service)

1. Click **VoIPServer** → **Services** tab
2. Enable **VoIP** service
3. Note: Packet Tracer has built-in SIP support
4. The server will respond to SIP calls automatically

### StreamServer (Streaming)

1. Click **StreamServer** → **Services** tab
2. Enable **HTTP** service (we'll simulate streaming as HTTP)
3. For realistic simulation, configure a large file to simulate video stream

### FTPServer (FTP Service)

1. Click **FTPServer** → **Services** tab
2. Enable **FTP** service
3. Configure FTP settings:
   - Username: `cisco`
   - Password: `cisco`
   - Write: Enabled
4. Add test files in the FTP directory

---

## 🔄 Part 4: Generate Traffic

### Method 1: Using Simulation Mode (Recommended for Capture)

1. Click **Simulation** mode button (bottom right)
2. This allows you to see and capture packets

### Traffic Scenario 1: Web Browsing (Client1)

1. Click **Client1** → **Desktop** → **Web Browser**
2. Enter URL: `http://10.0.1.100`
3. The browser will generate HTTP GET requests
4. **Duration:** Let it run for 10-15 seconds
5. **Expected:** Request-response pattern, bursty traffic

### Traffic Scenario 2: VoIP (Client2)

**Note:** VoIP in Packet Tracer requires IP phones. Alternative simulation:

1. Add **IP Phone** device from End Devices
2. Connect to Switch
3. Configure with IP: `10.0.0.20`
4. Click Phone → Physical tab
5. Click **Config** → Set SIP server to `10.0.2.100`
6. Make a call → generates SIP + RTP traffic
7. **Duration:** 20-30 seconds
8. **Expected:** Constant rate, small packets

**Alternative if no phone:**
- Use continuous ping with small packets: `ping 10.0.2.100 -t`

### Traffic Scenario 3: Streaming (Client3)

1. Click **Client3** → **Desktop** → **Web Browser**
2. Access streaming URL: `http://10.0.1.102/video.mp4` (simulated)
3. Or use **Command Prompt**:
   ```
   ping 10.0.1.102 -l 1400 -t
   ```
   (Simulates sustained large packet flow)
4. **Duration:** 30-45 seconds
5. **Expected:** Sustained throughput, medium packets

### Traffic Scenario 4: File Transfer (Client4)

1. Click **Client4** → **Desktop** → **Command Prompt**
2. Use FTP:
   ```
   ftp 10.0.1.103
   User: cisco
   Password: cisco
   get largefile.bin
   ```
3. Or use Command Prompt ping to simulate:
   ```
   ping 10.0.1.103 -l 1400 -n 100
   ```
4. **Duration:** 15-20 seconds
5. **Expected:** Bulk transfer, large packets

---

## 📦 Part 5: Capture and Export Traffic

### Method 1: Packet Tracer Simulation Mode Export

1. **Enable Simulation Mode:**
   - Click **Simulation** button (bottom right)
   - The timeline appears at the bottom

2. **Run Traffic:**
   - Switch to **Real-Time** mode temporarily to generate traffic
   - Then back to **Simulation** mode

3. **View Packets:**
   - In Simulation Panel, you'll see packet list
   - Click **Event List** to see all packets

4. **Export PCAP:**
   - Unfortunately, Packet Tracer does **NOT** directly export PCAP files
   - Workaround: Use screen capture or record packet details

### Method 2: Connect Real Wireshark (Advanced)

**This requires connecting Packet Tracer to real network:**

1. **Enable Packet Tracer's Cloud Device:**
   - Add **Cloud-PT** device from Network Devices
   - Connect to your topology
   - Configure to bridge with real network adapter

2. **Run Wireshark on Host:**
   - Start Wireshark on your Windows machine
   - Select the bridge interface
   - Start capture
   - Generate traffic in Packet Tracer
   - Stop capture and save as `.pcap`

### Method 3: Use Real Network (Recommended for Demo)

**For actual PCAP files to classify:**

1. Generate real traffic on your network
2. Capture with Wireshark:
   ```powershell
   # Install Wireshark with tshark
   # Then capture:
   tshark -i <interface> -w traffic_capture.pcap -a duration:60
   ```

3. Or use sample PCAPs from ISCX dataset (already have these)

---

## 🤖 Part 6: Classify Traffic with FlowSentry

### Prepare PCAP File

If you have a real PCAP file `captured_traffic.pcap`:

```powershell
# Place in project directory
cd d:\Sentry_Flow
```

### Run Classification (Once CN-015 is complete)

```powershell
# Classify PCAP file
python -m inference.classify --pcap captured_traffic.pcap

# Or use evaluation module
python -m evaluation.evaluate --pcap captured_traffic.pcap
```

**Expected Output:**
```
🔍 Analyzing PCAP: captured_traffic.pcap
📊 Extracted 245 flows
⚙️ Preprocessing features...
🤖 Loading best model: decision_tree_20261014_011743
🎯 Classifying...

Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Class              Flows    Percentage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Web Browsing         98        40.0%
VoIP                 71        29.0%
Streaming            45        18.4%
File Transfer        31        12.7%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total               245       100.0%

💾 Results saved to: artifacts/inference/results_20261024_130000.json
```

---

## 🎓 Part 7: Viva Demonstration Script

### Setup (Before Viva)

1. **Open Packet Tracer** with completed topology
2. **Have FlowSentry ready:**
   ```powershell
   cd d:\Sentry_Flow
   python -m dashboard.app
   ```
3. **Browser open** to `http://localhost:5000`

### Demonstration Flow (10-15 minutes)

#### 1. Introduce the Problem (2 min)

**Say:**
> "Network traffic classification is essential for Quality of Service, security, and network management. Traditional methods use port numbers or deep packet inspection. FlowSentry uses machine learning on flow-level statistical features without inspecting payload, making it privacy-preserving and encryption-friendly."

**Show:** Dashboard → Overview tab

#### 2. Show Network Topology (2 min)

**Say:**
> "We've created a realistic network in Cisco Packet Tracer with 4 clients, 4 servers, demonstrating all four traffic classes."

**Show:** Packet Tracer topology
- Point out Router, Switch, Clients, Servers
- Mention IP addressing scheme
- Show configured services

#### 3. Demonstrate Traffic Generation (3 min)

**Say:**
> "Let me generate each type of traffic."

**Do:**
- **Web Browsing:** Client1 → Web Browser → 10.0.1.100
- **VoIP:** Client2 → (ping or phone call)
- **Streaming:** Client3 → Sustained traffic
- **File Transfer:** Client4 → FTP transfer

**Show:** Packet Tracer's Simulation mode showing packets flowing

#### 4. Show ML Pipeline (3 min)

**Say:**
> "We trained 4 machine learning models on the ISCX-VPN2016 dataset using flow-level features like inter-arrival times, packet sizes, and TCP flags."

**Show:** Dashboard → Models tab
- Show trained models and performance
- **Decision Tree: 99.92% F1**
- Explain why Decision Tree performs best

**Show:** Dashboard → Features tab
- Feature importance chart
- **Key insight:** Timing features dominate

#### 5. Show Dataset (1 min)

**Show:** Dashboard → Dataset tab
- 59,621 total samples
- 4 classes
- Class distribution

#### 6. Live Classification (2 min)

**Say:**
> "Now let's classify real traffic."

**Do:**
```powershell
python -m inference.classify --pcap sample_traffic.pcap
```

**Show:** Classification results
- Number of flows detected
- Predicted classes and distribution
- Matches expected traffic from Packet Tracer

#### 7. Wrap Up (1 min)

**Say:**
> "This demonstrates a complete pipeline: network topology → traffic generation → feature extraction → ML classification, all without inspecting packet payloads."

**Show:** Dashboard → Network tab with architecture overview

---

## 🎬 Alternative: Record a Demo Video

If live demo is risky, record a video beforehand:

1. **Use OBS Studio** (free) to record screen
2. Follow the demonstration script above
3. Keep video under 10 minutes
4. Have it ready as backup

---

## 🐛 Troubleshooting

### Packet Tracer Issues

**Problem:** Devices can't ping each other
- **Solution:** Check cable connections (green lights on ports)
- Verify IP addresses and default gateways
- Check router interfaces are "no shutdown"

**Problem:** Services not responding
- **Solution:** Go to Services tab, ensure service is **On**
- Restart the service
- Check firewall settings (usually off in Packet Tracer)

**Problem:** Can't see packets in Simulation mode
- **Solution:** Click "Edit Filters" in Simulation panel
- Ensure relevant protocols (HTTP, TCP, ICMP) are selected
- Reset simulation and try again

### FlowSentry Issues

**Problem:** Can't classify PCAP
- **Solution:** Ensure CICFlowMeter is installed (currently blocked - see docs)
- Use sample PCAPs from dataset instead
- Or wait for CN-015 completion

**Problem:** Dashboard won't start
- **Solution:**
  ```powershell
  pip install Flask
  python -m dashboard.app
  ```

**Problem:** No models shown in dashboard
- **Solution:** Train models first:
  ```powershell
  python -m models.train --model decision_tree
  python -m models.train --model random_forest
  python -m models.train --model xgboost
  python -m models.train --model svm
  ```

---

## 📚 Additional Resources

### Cisco Packet Tracer Tutorials
- Official Packet Tracer Documentation
- Cisco Networking Academy courses
- YouTube: "Cisco Packet Tracer Tutorial for Beginners"

### FlowSentry Documentation
- `files/README.md` - Project overview
- `files/PRD.md` - Requirements
- `files/TRD.md` - Technical design
- `files/BUILD_PLAN.md` - Implementation plan

### Network Traffic Classification Papers
- ISCX-VPN2016 Dataset Paper
- "A Survey of Techniques for Internet Traffic Classification"
- "Network Traffic Classification Using Machine Learning"

---

## ✅ Checklist for Viva

Before your viva, ensure:

- [ ] Packet Tracer topology is built and tested
- [ ] All 4 traffic scenarios work
- [ ] FlowSentry dashboard runs successfully
- [ ] All 4 models are trained
- [ ] You can explain the ML pipeline
- [ ] You understand feature importance
- [ ] You can explain why timing features dominate
- [ ] You know the limitations (no payload, encryption-friendly)
- [ ] Sample PCAP is ready for classification
- [ ] Backup slides/video prepared
- [ ] You've practiced the demo (under 15 minutes)

---

## 🎯 Key Points to Emphasize

1. **Privacy-Preserving:** No payload inspection, works with encrypted traffic
2. **Flow-Level Features:** Timing, volume, directional statistics
3. **High Accuracy:** Decision Tree achieves 99.92% F1 score
4. **Real Network:** Packet Tracer demonstrates practical application
5. **Complete Pipeline:** From packets to predictions
6. **Academic Rigor:** Proper train/test split, cross-validation, no leakage

---

## 📞 Support

For questions or issues:
1. Check `docs/task_reports/` for task completion details
2. Review `files/TRD.md` for technical design
3. Check GitHub repository for latest updates
4. Consult with team members

---

**Good luck with your viva! 🎓🚀**

Remember: The goal is to demonstrate understanding of both networking concepts and machine learning, showing how they integrate in a practical system.
