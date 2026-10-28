# Complete Installation & Setup Guide
**FlowSentry - Npcap Installation & Cisco Packet Tracer Tutorial**

---

## Part 1: Npcap Installation ✅

### What is Npcap?
Npcap is a Windows packet capture library required by CICFlowMeter to read PCAP files. It's a modern replacement for WinPcap.

### Installation Steps

#### 1. Download & Run Installer
- Download from: https://npcap.com/#download
- Run `npcap-1.XX-setup.exe` as **Administrator**

#### 2. Configure Installation Options

**REQUIRED:**
- ✅ **"Install Npcap in WinPcap API-compatible Mode"** - MUST be checked
  - This allows CICFlowMeter (which uses older WinPcap API) to work

**OPTIONAL:**
- ☐ "Restrict Npcap driver's access to Administrators only" - Leave **UNCHECKED**
  - Unchecked: Your Python scripts can access Npcap without admin rights
  - Checked: Only admin users can capture packets (more secure, but requires `runas`)
  
- ☐ "Support raw 802.11 traffic (and monitor mode) for wireless adapters" - Leave **UNCHECKED**
  - Not needed for this project (we're reading PCAP files, not capturing live Wi-Fi)

#### 3. Complete Installation
1. Click **"Install"**
2. Wait 30-60 seconds
3. Click **"Finish"**
4. **⚠️ RESTART YOUR COMPUTER** (required for driver to load)

#### 4. Verify Installation

After restart:

```powershell
# Navigate to project
cd d:\Sentry_Flow

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run verification script
python scripts\verify_cicflowmeter.py
```

**Expected Success Output:**
```
======================================================================
CICFLOWMETER VERIFICATION
======================================================================
Python version: 3.X.X

Checking cicflowmeter availability...
✅ cicflowmeter is available (version: 0.X.X)

Testing PCAP processing...
Processing test.pcap with CICFlowMeter...
✅ PCAP processing successful
   Duration: 2.34 seconds
   Output: test_output.csv
   Columns extracted: 83

Checking output validity...
✅ CSV output generated with expected columns

======================================================================
✅ VERIFICATION SUCCESSFUL
======================================================================
CICFlowMeter is ready to use!
```

**If you see errors:**
- `Scapy error: No such device` → Npcap not installed or needs restart
- `tcpdump is not available` → Npcap not in WinPcap mode (reinstall with checkbox)
- `ModuleNotFoundError: cicflowmeter` → Run `pip install cicflowmeter==0.4.2`

---

## Part 2: Testing PCAP Classification

### Step 1: Generate Test PCAP

```powershell
# Generate synthetic test traffic
python scripts\generate_test_pcap.py
```

This creates `data/sample/test_traffic.pcap` with 4 flows:
- Web Browsing (HTTP)
- File Transfer (FTP)
- VoIP (UDP)
- Streaming (Video)

### Step 2: Classify the Test PCAP

```powershell
# Run PCAP classifier
python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/test_classification
```

**Expected Output:**
```
======================================================================
FLOWSENTRY PCAP CLASSIFICATION
======================================================================
Input PCAP: data/sample/test_traffic.pcap
Output directory: artifacts/test_classification
Model: active model from registry

Loading model from registry...
✅ Loaded model: XGBoost (xgboost_20261024_124732)
   Features: 79
   Classes: 4 (Web Browsing, VoIP, Streaming, File Transfer)

Extracting flows from PCAP...
✅ Extracted 4 flows

Classifying flows...
✅ Classification complete

======================================================================
CLASSIFICATION RESULTS
======================================================================
Total flows: 4

Flows per class:
  Web Browsing        :    1 ( 25.0%)  ██████████████████
  VoIP                :    1 ( 25.0%)  ██████████████████
  Streaming           :    1 ( 25.0%)  ██████████████████
  File Transfer       :    1 ( 25.0%)  ██████████████████

Average confidence: 0.8532

✅ Predictions saved to: artifacts/test_classification/
   - predictions.csv     (per-flow predictions)
   - predictions.json    (structured results with metadata)
   - summary.txt         (this output)

======================================================================
```

### Step 3: Inspect Results

```powershell
# View CSV predictions
type artifacts\test_classification\predictions.csv

# View JSON results
type artifacts\test_classification\predictions.json
```

---

## Part 3: Cisco Packet Tracer Setup 🌐

### What is Cisco Packet Tracer?
Cisco Packet Tracer is a network simulation tool that lets you:
- Build virtual networks (routers, switches, PCs, servers)
- Configure devices with real Cisco IOS commands
- Generate network traffic
- Capture traffic as PCAP files
- Test your FlowSentry classifier with realistic traffic

### Prerequisites
- Cisco Packet Tracer 8.x installed
- Free Cisco Networking Academy account (for download)
- Download: https://www.netacad.com/courses/packet-tracer

---

## Step-by-Step: Building FlowSentry Test Network

### Overview: What We're Building

```
                    10.0.0.0/24                     10.0.1.0/24
                    (Clients)                       (Servers)
                        |                               |
    ┌───────────┐       |       ┌──────────┐       |       ┌───────────┐
    │  PC-Web   │───────┼───────│          │───────┼───────│Server-Web │
    │.0.10      │       |       │   SW1    │       |       │.1.100     │
    └───────────┘       |       │ (Switch) │       |       └───────────┘
                        |       └────┬─────┘       |
    ┌───────────┐       |            │             |       ┌───────────┐
    │ PC-VoIP   │───────┼────────────┤             |───────│Server-VoIP│
    │.0.11      │       |            │             |       │.1.101     │
    └───────────┘       |       ┌────┴─────┐       |       └───────────┘
                        |       │    R1    │       |
    ┌───────────┐       |───────│ (Router) │───────┼       ┌───────────┐
    │PC-Stream  │       |       │Gig0/0│Gig0/1│    |───────│Server-    │
    │.0.12      │───────┘       │.0.1  │.1.1  │    └───────│Stream     │
    └───────────┘               └──────────────┘            │.1.102     │
                                                            └───────────┘
    ┌───────────┐                                           ┌───────────┐
    │  PC-FTP   │───────────────────────────────────────────│Server-FTP │
    │.0.13      │                                           │.1.103     │
    └───────────┘                                           └───────────┘

Traffic Types:
  PC-Web    ↔ Server-Web    : HTTP  (Web Browsing)
  PC-VoIP   ↔ Server-VoIP   : SIP   (VoIP)
  PC-Stream ↔ Server-Stream : HTTP  (Streaming)
  PC-FTP    ↔ Server-FTP    : FTP   (File Transfer)
```

**Network Details:**
- **Router:** R1 (Cisco 2911)
- **Switch:** SW1 (Cisco 2960-24TT)
- **Clients:** 10.0.0.10-13 (subnet 10.0.0.0/24, gateway 10.0.0.1)
- **Servers:** 10.0.1.100-103 (subnet 10.0.1.0/24, gateway 10.0.1.1)

---

### Phase 1: Create the Topology (15 minutes)

#### 1. Open Cisco Packet Tracer
- Launch Packet Tracer
- Close any welcome screens
- You'll see a blank workspace

#### 2. Add Devices

**Add Router:**
1. Click **"Network Devices"** (bottom left)
2. Click **"Routers"**
3. Drag **"2911"** router to the center of workspace
4. It will be named `Router0` → right-click → rename to **`R1`**

**Add Switch:**
1. Click **"Network Devices"**
2. Click **"Switches"**
3. Drag **"2960-24TT"** switch below the router
4. Rename to **`SW1`**

**Add Client PCs (Left side):**
1. Click **"End Devices"**
2. Click **"PC"**
3. Drag **4 PCs** to the left side
4. Rename them:
   - `PC0` → **`PC-Web`**
   - `PC1` → **`PC-VoIP`**
   - `PC2` → **`PC-Stream`**
   - `PC3` → **`PC-FTP`**

**Add Servers (Right side):**
1. Click **"End Devices"**
2. Click **"Server"**
3. Drag **4 Servers** to the right side
4. Rename them:
   - `Server0` → **`Server-Web`**
   - `Server1` → **`Server-VoIP`**
   - `Server2` → **`Server-Stream`**
   - `Server3` → **`Server-FTP`**

#### 3. Connect Devices with Cables

**Cable Type:** Use **"Copper Straight-Through"** (black cable icon, bottom left)

**Connect PCs to Switch:**
1. Click the black cable icon
2. Click `PC-Web` → choose `FastEthernet0`
3. Click `SW1` → choose `FastEthernet0/1`
4. Repeat for other PCs:
   - `PC-VoIP` → `SW1` port `FastEthernet0/2`
   - `PC-Stream` → `SW1` port `FastEthernet0/3`
   - `PC-FTP` → `SW1` port `FastEthernet0/4`

**Connect Switch to Router:**
1. Click `SW1` → choose `GigabitEthernet0/1`
2. Click `R1` → choose `GigabitEthernet0/0`

**Connect Servers to Router:**
1. `Server-Web` → `R1` port `GigabitEthernet0/1` (use another switch if needed)
   
   **OR** add a second switch `SW2` on the right:
   - Connect `SW2` port `GigabitEthernet0/1` → `R1` port `GigabitEthernet0/1`
   - Connect all 4 servers to `SW2` ports `FastEthernet0/1-4`

**Visual Check:**
- All connections should show **green triangles** after ~30 seconds
- Red = not configured yet (expected at this stage)

---

### Phase 2: Configure Router (10 minutes)

#### 1. Open Router CLI
- Click **`R1`** router
- Click **"CLI"** tab
- Press **Enter** to start

#### 2. Enter Configuration Mode

```
Router> enable
Router# configure terminal
Router(config)#
```

#### 3. Configure GigabitEthernet0/0 (Client side - 10.0.0.0/24)

```
Router(config)# interface GigabitEthernet0/0
Router(config-if)# description Client Network
Router(config-if)# ip address 10.0.0.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit
```

**Output:**
```
%LINK-5-CHANGED: Interface GigabitEthernet0/0, changed state to up
```

#### 4. Configure GigabitEthernet0/1 (Server side - 10.0.1.0/24)

```
Router(config)# interface GigabitEthernet0/1
Router(config-if)# description Server Network
Router(config-if)# ip address 10.0.1.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit
```

#### 5. Set Hostname & Save

```
Router(config)# hostname R1
R1(config)# exit
R1# write memory
```

**Output:**
```
Building configuration...
[OK]
```

#### 6. Verify Configuration

```
R1# show ip interface brief
```

**Expected Output:**
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.0.0.1        YES manual up                    up
GigabitEthernet0/1     10.0.1.1        YES manual up                    up
```

---

### Phase 3: Configure Client PCs (10 minutes)

For each client PC, set IP address, subnet mask, and gateway:

#### PC-Web
1. Click **`PC-Web`**
2. Click **"Desktop"** tab
3. Click **"IP Configuration"**
4. Select **"Static"**
5. Enter:
   - **IP Address:** `10.0.0.10`
   - **Subnet Mask:** `255.255.255.0`
   - **Default Gateway:** `10.0.0.1`
6. Close

#### PC-VoIP
- **IP Address:** `10.0.0.11`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `10.0.0.1`

#### PC-Stream
- **IP Address:** `10.0.0.12`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `10.0.0.1`

#### PC-FTP
- **IP Address:** `10.0.0.13`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `10.0.0.1`

---

### Phase 4: Configure Servers (15 minutes)

#### Server-Web (HTTP)

**1. Set IP Address:**
- Click **`Server-Web`**
- **Desktop** → **IP Configuration** → **Static**
- **IP:** `10.0.1.100`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `10.0.1.1`

**2. Enable HTTP Service:**
- Click **"Services"** tab
- Click **"HTTP"**
- Ensure **"HTTP Service"** is **ON**
- (Default index.html already exists)

#### Server-VoIP (SIP/VoIP)

**Set IP:**
- **IP:** `10.0.1.101`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `10.0.1.1`

**Enable VoIP:**
- **Services** → **VoIP** → **ON** (if available)
- (For simplicity, we'll simulate VoIP with ping in traffic generation)

#### Server-Stream (HTTP Streaming)

**Set IP:**
- **IP:** `10.0.1.102`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `10.0.1.1`

**Enable HTTP:**
- **Services** → **HTTP** → **ON**

#### Server-FTP (File Transfer)

**Set IP:**
- **IP:** `10.0.1.103`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `10.0.1.1`

**Enable FTP:**
- **Services** → **FTP** → **ON**
- Default credentials: `cisco` / `cisco`

---

### Phase 5: Test Connectivity (5 minutes)

#### 1. Test from PC-Web to Server-Web

1. Click **`PC-Web`**
2. **Desktop** → **Command Prompt**
3. Run:
   ```
   ping 10.0.1.100
   ```
4. **Expected:**
   ```
   Reply from 10.0.1.100: bytes=32 time<1ms TTL=127
   Reply from 10.0.1.100: bytes=32 time<1ms TTL=127
   ...
   ```
5. If "Request timed out" → check IP configs and cable connections

#### 2. Test All Servers

From any PC:
```
ping 10.0.1.100    (Server-Web - should succeed)
ping 10.0.1.101    (Server-VoIP - should succeed)
ping 10.0.1.102    (Server-Stream - should succeed)
ping 10.0.1.103    (Server-FTP - should succeed)
```

**All should reply ✅**

---

### Phase 6: Generate Traffic (20 minutes)

Now generate each traffic type and capture it.

#### Traffic Type 1: Web Browsing

**On PC-Web:**
1. **Desktop** → **Web Browser**
2. Enter URL: `http://10.0.1.100`
3. Press **Go**
4. You should see the server's default webpage
5. Click links, refresh page (generate more HTTP traffic)

**Expected:** HTTP GET/POST requests, HTML responses

#### Traffic Type 2: VoIP (Simulated with continuous ping)

**On PC-VoIP:**
1. **Desktop** → **Command Prompt**
2. Run continuous ping:
   ```
   ping 10.0.1.101 -t
   ```
3. Let it run for ~30 seconds (generates constant small packets, like VoIP)
4. Press **Ctrl+C** to stop

**Expected:** Constant stream of small ICMP packets

#### Traffic Type 3: Streaming (Large continuous packets)

**On PC-Stream:**
1. **Desktop** → **Command Prompt**
2. Run:
   ```
   ping 10.0.1.102 -l 1400 -t
   ```
   - `-l 1400` = large 1400-byte packets (like video)
   - `-t` = continuous
3. Let it run for ~30 seconds
4. Press **Ctrl+C** to stop

**Expected:** Large packets at sustained rate

#### Traffic Type 4: File Transfer (FTP)

**On PC-FTP:**
1. **Desktop** → **Command Prompt**
2. Connect to FTP server:
   ```
   ftp 10.0.1.103
   ```
3. Login:
   - **Username:** `cisco`
   - **Password:** `cisco`
4. Upload/download a file:
   ```
   ftp> dir
   ftp> get file.txt
   ftp> put testfile.txt
   ftp> bye
   ```

**Expected:** FTP control + data channel traffic

---

### Phase 7: Capture Traffic as PCAP (15 minutes)

#### Method 1: Simulation Mode (Easiest)

**1. Enable Simulation Mode:**
- Click **"Simulation"** button (bottom right, stopwatch icon)
- Packet Tracer switches to simulation mode

**2. Filter Traffic (Optional):**
- Click **"Edit Filters"**
- Check only: **TCP**, **UDP**, **HTTP**, **FTP**
- Uncheck **ARP**, **ICMP** (unless simulating VoIP)

**3. Generate Traffic:**
- Repeat traffic generation (web browsing, pings, FTP)
- You'll see packets animated across the network
- Click **"Capture/Forward"** to process packets

**4. Export as PCAP:**
- Unfortunately, **Packet Tracer does NOT directly export PCAP from simulation**
- You need to use **Realtime Mode** + external capture (see Method 2)

---

#### Method 2: Use External Tool (Recommended for Real PCAP)

Since Packet Tracer doesn't export PCAP directly, you have two options:

**Option A: Use Real Network Capture**
1. Generate traffic in Packet Tracer (tests your network design)
2. Capture **real** traffic from your Windows network adapter
3. Use Wireshark or `tshark`:
   ```powershell
   # Install Wireshark (includes tshark)
   # Then capture:
   tshark -i "Ethernet" -w capture.pcap -f "tcp or udp"
   ```

**Option B: Export Packet Tracer Simulation (Workaround)**
1. Save your Packet Tracer file: **File** → **Save As** → `flowsentry_topology.pkt`
2. Use the topology as a **reference/demonstration** for your viva
3. For actual PCAP files, use:
   - The synthetic PCAP you generated earlier (`generate_test_pcap.py`)
   - Real captured traffic from your network (with permission)
   - Public datasets (CIC-IDS, UNSW-NB15, etc.)

---

### Phase 8: Classify Packet Tracer Traffic

#### If you have a PCAP from capture:

```powershell
# Copy captured PCAP to project
copy path\to\captured.pcap d:\Sentry_Flow\data\sample\packet_tracer_traffic.pcap

# Classify it
python -m inference.pcap_classifier --pcap data/sample/packet_tracer_traffic.pcap --output artifacts/packet_tracer_classification
```

#### Using the synthetic test PCAP:

```powershell
python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/demo_classification
```

---

## Part 4: Demonstration for Viva 🎓

### What to Show

#### 1. Network Topology (5 minutes)
- Open `flowsentry_topology.pkt` in Packet Tracer
- Explain:
  - 2 subnets (clients 10.0.0.0/24, servers 10.0.1.0/24)
  - Router R1 connects them
  - 4 traffic types (Web, VoIP, Streaming, FTP)
- Show ping tests proving connectivity

#### 2. Traffic Generation (5 minutes)
- Demonstrate each traffic type:
  - Web: Browse to `http://10.0.1.100`
  - VoIP: Continuous ping
  - Streaming: Large packets
  - FTP: File transfer
- Show traffic in Simulation Mode (visual packet animation)

#### 3. PCAP Classification (10 minutes)
- Run the classifier:
  ```powershell
  python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/demo
  ```
- Show the output:
  - Per-flow predictions
  - Confidence scores
  - Class distribution
- Open `artifacts/demo/predictions.csv` in Excel/Notepad

#### 4. Dashboard (5 minutes)
- Launch dashboard:
  ```powershell
  python -m dashboard.app
  ```
- Show:
  - Model comparison tab
  - Feature importance
  - Confusion matrix
  - Active model info

#### 5. End-to-End Flow (Summary)
- **Network** (Packet Tracer) → **Traffic** → **Capture** (PCAP) → **Extraction** (CICFlowMeter) → **Features** (79 flow features) → **Model** (XGBoost) → **Prediction** (Traffic class)

---

## Quick Reference Commands

### After Npcap Installation:

```powershell
# 1. Verify Npcap
python scripts\verify_cicflowmeter.py

# 2. Generate test PCAP
python scripts\generate_test_pcap.py

# 3. Classify PCAP
python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/test

# 4. View results
type artifacts\test\predictions.csv
type artifacts\test\summary.txt

# 5. Run tests
pytest tests/integration/test_pcap_flow_extraction.py -v

# 6. Launch dashboard
python -m dashboard.app
```

---

## Troubleshooting

### Npcap Issues

**Error: "Scapy error: No such device"**
- **Cause:** Npcap not installed or driver not loaded
- **Fix:** Restart computer after Npcap installation

**Error: "tcpdump is not available"**
- **Cause:** Npcap not in WinPcap compatibility mode
- **Fix:** Reinstall Npcap with "WinPcap API-compatible Mode" checked

**Error: "Permission denied"**
- **Cause:** Npcap restricted to administrators
- **Fix:** Reinstall Npcap with "Restrict to Administrators" UNCHECKED, or run Python as admin

### Packet Tracer Issues

**Ping fails between devices**
- Check IP addresses (typo in subnet?)
- Check default gateway (should be router's IP on that subnet)
- Check router interface status: `show ip interface brief`
- Check cables (should show green triangles)

**Cannot save .pkt file**
- Packet Tracer requires Cisco account login
- Use **File** → **Save As**, not **Export**

**Simulation mode is slow**
- Normal behavior for complex networks
- Use **Realtime Mode** for faster traffic generation

---

## Summary Checklist

### Before Viva:
- ✅ Npcap installed and verified
- ✅ Test PCAP generated and classified successfully
- ✅ Packet Tracer topology built and saved
- ✅ All connectivity tests passing
- ✅ Traffic generation demonstrated
- ✅ Dashboard launched successfully
- ✅ Classification results reviewed

### For Viva Demo:
- ✅ Open Packet Tracer with topology
- ✅ Have terminal ready with project activated
- ✅ Pre-run classifier on test PCAP (have results ready)
- ✅ Dashboard running in browser
- ✅ Know the end-to-end flow explanation

---

## Next Steps

1. **Now:** Click "Install" on Npcap installer, restart computer
2. **After restart:** Run `python scripts\verify_cicflowmeter.py`
3. **Generate test data:** Run `python scripts\generate_test_pcap.py`
4. **Test classifier:** Run `python -m inference.pcap_classifier ...`
5. **Build Packet Tracer topology:** Follow Phase 1-7 above (~90 minutes)
6. **Practice demo:** Run through the demonstration flow

---

**Good luck with your project and viva! 🚀**

If you encounter any issues, check:
1. Environment verification output
2. Error messages (copy exact text)
3. Log files in `artifacts/logs/`
