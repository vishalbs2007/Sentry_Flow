# 🌐 FlowSentry Cisco Packet Tracer Demo - Quick Start

**Complete hands-on guide to build and demonstrate network traffic classification**

---

## 🎯 What You'll Build

A working network topology with:
- **1 Router** (Cisco 2911) - Gateway
- **1 Switch** (Cisco 2960-24TT) - Layer 2 switching  
- **4 Client PCs** - Generate different traffic types
- **4 Servers** - Provide services (HTTP, VoIP, Streaming, FTP)

This demonstrates all 4 traffic classes FlowSentry can classify!

---

## ⚡ Quick Setup (30 minutes)

### Part 1: Build the Topology (10 min)

#### Step 1: Open Packet Tracer
1. Launch **Cisco Packet Tracer**
2. **File → New** (or Ctrl+N)

#### Step 2: Add Devices (drag from bottom panel)

**Router:**
- Click **Network Devices** → **Routers**
- Select **2911**
- Drag **1 router** to workspace
- Label it: **R1**

**Switch:**
- Click **Network Devices** → **Switches**  
- Select **2960-24TT**
- Drag **1 switch** to workspace
- Label it: **SW1**

**Clients (4 PCs):**
- Click **End Devices** → **PC**
- Drag **4 PCs** to workspace
- Label them: **PC-Web**, **PC-VoIP**, **PC-Stream**, **PC-FTP**

**Servers (4):**
- Click **End Devices** → **Server**
- Drag **4 servers** to workspace  
- Label them: **Server-Web**, **Server-VoIP**, **Server-Stream**, **Server-FTP**

#### Step 3: Connect Everything

**Connect Router to Switch:**
- Select **Connections** → **Copper Straight-Through** (lightning bolt icon)
- Click **R1 GigabitEthernet0/0** → Click **SW1 GigabitEthernet0/1**
- Wait for green lights (may take a moment)

**Connect All 4 Clients to Switch:**
- **PC-Web** FastEthernet0 → **SW1** FastEthernet0/1
- **PC-VoIP** FastEthernet0 → **SW1** FastEthernet0/2
- **PC-Stream** FastEthernet0 → **SW1** FastEthernet0/3
- **PC-FTP** FastEthernet0 → **SW1** FastEthernet0/4

**Connect All 4 Servers to Router (direct):**
- **Server-Web** FastEthernet0 → **R1** GigabitEthernet0/1
- **Server-VoIP** FastEthernet0 → **R1** GigabitEthernet0/2 (if available)
- **Server-Stream** FastEthernet0 → **R1** FastEthernet0/0/0 (alternative)
- **Server-FTP** FastEthernet0 → **R1** FastEthernet0/0/1 (alternative)

**Note:** If router doesn't have enough ports, connect servers to a second switch, then switch to router.

✅ **Checkpoint:** All connections should show **green triangles** on both ends

---

### Part 2: Configure IP Addresses (10 min)

#### Network Plan:
- **Client Network:** 10.0.0.0/24 (Gateway: 10.0.0.1)
- **Server Network:** 10.0.1.0/24 (Gateway: 10.0.1.1)

---

#### Configure Router R1

**Click R1 → Config Tab:**

**GigabitEthernet0/0 (Client-side):**
- Port Status: **On**
- IP Address: **10.0.0.1**
- Subnet Mask: **255.255.255.0**

**GigabitEthernet0/1 (Server-side):**
- Port Status: **On**
- IP Address: **10.0.1.1**  
- Subnet Mask: **255.255.255.0**

**Or use CLI method:**
Click R1 → **CLI** tab:
```
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

exit
write memory
```

---

#### Configure Clients

**PC-Web:**
1. Click **PC-Web** → **Desktop** → **IP Configuration**
2. Select **Static**
3. IP Address: **10.0.0.10**
4. Subnet Mask: **255.255.255.0**
5. Default Gateway: **10.0.0.1**
6. DNS Server: **10.0.1.100** (optional)

**PC-VoIP:**
- IP Address: **10.0.0.11**
- Subnet Mask: **255.255.255.0**
- Default Gateway: **10.0.0.1**

**PC-Stream:**
- IP Address: **10.0.0.12**
- Subnet Mask: **255.255.255.0**
- Default Gateway: **10.0.0.1**

**PC-FTP:**
- IP Address: **10.0.0.13**
- Subnet Mask: **255.255.255.0**
- Default Gateway: **10.0.0.1**

---

#### Configure Servers

**Server-Web:**
1. Click **Server-Web** → **Desktop** → **IP Configuration**
2. IP Address: **10.0.1.100**
3. Subnet Mask: **255.255.255.0**
4. Default Gateway: **10.0.1.1**

**Server-VoIP:**
- IP Address: **10.0.1.101**
- Subnet Mask: **255.255.255.0**
- Default Gateway: **10.0.1.1**

**Server-Stream:**
- IP Address: **10.0.1.102**
- Subnet Mask: **255.255.255.0**
- Default Gateway: **10.0.1.1**

**Server-FTP:**
- IP Address: **10.0.1.103**
- Subnet Mask: **255.255.255.0**
- Default Gateway: **10.0.1.1**

---

#### Test Connectivity

From **PC-Web**:
1. **Desktop** → **Command Prompt**
2. Type: `ping 10.0.0.1` (should succeed - router)
3. Type: `ping 10.0.1.100` (should succeed - server)
4. Type: `ping 10.0.0.11` (should succeed - another PC)

✅ **Checkpoint:** All pings should succeed (Reply from...)

---

### Part 3: Configure Services (5 min)

#### Server-Web (HTTP Service)

1. Click **Server-Web** → **Services** tab
2. **HTTP** should be **ON** by default
3. (Optional) Click **HTTP** → Edit index.html:
   ```html
   <html><body>
   <h1>FlowSentry Test - Web Traffic</h1>
   <p>This is web browsing traffic for classification.</p>
   </body></html>
   ```

#### Server-VoIP (Phone Service)

1. Click **Server-VoIP** → **Services** tab
2. Enable **VoIP/SIP** (if available)
3. **Note:** Full VoIP requires IP phones (see alternative below)

#### Server-Stream (Streaming Service)

1. Click **Server-Stream** → **Services** tab
2. Enable **HTTP** service
3. Add a large file to simulate streaming (optional)

#### Server-FTP (FTP Service)

1. Click **Server-FTP** → **Services** tab
2. Enable **FTP** service
3. Configure:
   - **User:** cisco
   - **Password:** cisco
   - **Write Permission:** ✅ Enabled
4. Upload test files (optional)

✅ **Checkpoint:** All services show as **On** in Services tab

---

### Part 4: Generate Traffic (5 min)

Now let's create the 4 types of traffic!

#### 🌐 Traffic Type 1: Web Browsing

**From PC-Web:**
1. **Desktop** → **Web Browser**
2. Enter URL: `http://10.0.1.100`
3. Press Enter
4. ✅ You should see the webpage!

**What this demonstrates:**
- HTTP request-response pattern
- Bursty traffic (requests with pauses)
- Small to medium packet sizes
- Short duration connections

---

#### 📞 Traffic Type 2: VoIP Call

**Option A: Using IP Phone (Recommended)**

1. Delete PC-VoIP temporarily
2. Add **IP Phone** from End Devices
3. Connect to **SW1** FastEthernet0/2
4. Click Phone → **Config** tab:
   - IP Address: **10.0.0.11**
   - Subnet Mask: **255.255.255.0**
   - Default Gateway: **10.0.0.1**
5. Click Phone → **Physical** tab → Power on
6. **Dial** another phone or click **Service** → **Call**

**Option B: Simulate with Continuous Ping**

From PC-VoIP:
1. **Desktop** → **Command Prompt**
2. Type: `ping 10.0.1.101 -t -n 100`
   - `-t`: Continuous ping
   - `-n 100`: 100 packets

**What this demonstrates:**
- Constant rate traffic
- Small packets (64-128 bytes)
- Low latency requirement
- Bidirectional flow

---

#### 🎬 Traffic Type 3: Streaming

**From PC-Stream:**
1. **Desktop** → **Command Prompt**
2. Simulate sustained traffic:
   ```
   ping 10.0.1.102 -l 1400 -t
   ```
   - `-l 1400`: Large packet size (1400 bytes)
   - `-t`: Continuous

Or:
1. **Desktop** → **Web Browser**
2. Access: `http://10.0.1.102`
3. Keep connection open for 30-45 seconds

**What this demonstrates:**
- Sustained throughput
- Medium to large packets
- Buffer-based transmission
- Longer duration connections

---

#### 📁 Traffic Type 4: File Transfer

**From PC-FTP:**
1. **Desktop** → **Command Prompt**
2. Connect to FTP:
   ```
   ftp 10.0.1.103
   ```
3. Login:
   - User: **cisco**
   - Password: **cisco**
4. Transfer file:
   ```
   get test.txt
   ```
   (Use any file shown in `dir` command)

**Alternative - Simulate with Large Ping:**
```
ping 10.0.1.103 -l 1400 -n 200
```

**What this demonstrates:**
- Bulk data transfer
- Large packets
- TCP window-based flow control
- Complete file transfer

---

## 📊 Part 5: Visualize Traffic Flow

### Enable Simulation Mode

1. Click **Simulation** button (bottom right corner)
2. Panel appears at bottom showing Event List
3. Click **Auto Capture/Play** (▶️ button)

### Generate Traffic in Simulation

1. **Slow down** the simulation speed (slider at bottom)
2. Generate any traffic (e.g., ping from PC-Web to Server-Web)
3. **Watch packets flow:**
   - Green = Layer 2 (Ethernet)
   - Orange = Layer 3 (IP)
   - Blue = Layer 4 (TCP/UDP)

4. Click any packet to see details:
   - OSI Layer information
   - Source/Destination
   - Protocol
   - Timing

### Capture Multiple Traffic Types

1. Reset simulation: **Reset Simulation** button
2. Generate all 4 traffic types simultaneously:
   - PC-Web: Browse to Server-Web
   - PC-VoIP: Ping Server-VoIP continuously
   - PC-Stream: Large pings to Server-Stream
   - PC-FTP: FTP connection to Server-FTP

3. Watch different traffic patterns in the simulation!

---

## 🎓 Part 6: Viva Demonstration

### What to Show (10 minutes)

#### 1. Topology Overview (2 min)
**Say:** 
> "This is a realistic network with router, switch, 4 clients, and 4 servers representing different traffic classes."

**Point out:**
- Router as gateway between networks
- Switch for client connectivity
- Each server provides different services
- IP addressing scheme (10.0.0.x clients, 10.0.1.x servers)

#### 2. Traffic Generation (4 min)
**Say:**
> "Let me demonstrate each traffic type that FlowSentry can classify."

**Show each:**
- **Web:** PC-Web browsing Server-Web
- **VoIP:** Continuous small packets
- **Streaming:** Sustained large packets  
- **FTP:** File transfer

**Enable Simulation Mode** to show packets flowing!

#### 3. Traffic Characteristics (2 min)
**Say:**
> "Each traffic type has distinctive patterns that ML can learn without payload inspection."

**Explain:**
- **Web:** Request-response, bursty, variable timing
- **VoIP:** Constant rate, small packets, predictable
- **Streaming:** Sustained flow, buffer-based
- **FTP:** Bulk transfer, window-based

#### 4. Feature Extraction (2 min)
**Say:**
> "FlowSentry extracts flow-level statistical features from this traffic."

**Mention features:**
- Inter-Arrival Time (IAT) - timing between packets
- Packet sizes (forward/backward)
- Flow duration
- TCP flags
- Throughput (bytes per second)

**Show:** Switch to dashboard/presentation showing feature list

---

## 💡 Key Talking Points

### Why This Approach?

1. **Privacy-Preserving:** No payload inspection needed
2. **Encryption-Friendly:** Works even with HTTPS/encrypted traffic
3. **Network-Level:** Based on flow behavior, not content
4. **Realistic:** Packet Tracer shows real network protocols

### Traffic Classification Use Cases

1. **Quality of Service (QoS):** Prioritize VoIP over file transfers
2. **Network Management:** Identify bandwidth-heavy applications
3. **Security:** Detect anomalous traffic patterns
4. **Billing:** Usage-based pricing by application type

### Why Machine Learning?

1. **Port-based methods fail:** Apps use random/non-standard ports
2. **DPI breaks with encryption:** Can't inspect HTTPS payload
3. **ML learns patterns:** Timing and size patterns are distinctive
4. **Adaptable:** Can learn new applications

---

## 📸 Screenshots to Take

For your report/presentation:

1. **Complete topology** (all devices connected)
2. **Router configuration** (showing IP addresses)
3. **PC IP configuration** (one example)
4. **Server services enabled** (HTTP/FTP tabs)
5. **Web browser** showing Server-Web page
6. **FTP session** showing file transfer
7. **Simulation mode** showing packet flow
8. **Ping results** from each PC to server

---

## 🐛 Troubleshooting

### Ping Fails

**Problem:** `Request timed out` or `Destination host unreachable`

**Solutions:**
1. Check cable connections (green triangles on both ends)
2. Verify IP addresses match the plan
3. Verify default gateway is set correctly
4. Check router interfaces are "no shutdown"
5. Try `ping 10.0.0.1` first (should always work from clients)

### Services Don't Respond

**Problem:** Web browser shows "Request Timeout"

**Solutions:**
1. Go to server → **Services** tab
2. Ensure service (HTTP/FTP) is **ON**
3. Toggle it Off and On again
4. Try from Command Prompt: `ping 10.0.1.100` (test connectivity first)

### Simulation Shows No Packets

**Problem:** Simulation mode but no packets visible

**Solutions:**
1. Click **Edit Filters** in Simulation Panel
2. Ensure **ICMP, HTTP, TCP** are checked
3. Click **Reset Simulation**
4. Generate traffic again (ping or web browse)

---

## 🚀 Next Steps

After demonstrating the network:

1. **Save your topology:**
   - File → Save As → `flowsentry_demo.pkt`

2. **Export screenshot** for documentation

3. **Connect to FlowSentry ML pipeline:**
   - Explain that in real deployment, FlowSentry would:
     - Capture packets from this network
     - Extract flow features using CICFlowMeter
     - Classify traffic using trained ML models
     - Display results in dashboard

4. **Show ML results** (switch to dashboard):
   ```powershell
   cd d:\Sentry_Flow
   python -m dashboard.app
   ```
   Open: http://localhost:5000

5. **Explain integration:**
   > "The Packet Tracer network generates traffic → FlowSentry captures and extracts features → ML models classify → Dashboard displays results"

---

## 📚 Additional Enhancements (Optional)

### Add More Realism

1. **Add ACLs** on router (access control lists)
2. **Configure VLANs** on switch (separate client/server VLANs)
3. **Add second router** for routing between subnets
4. **Enable DHCP** instead of static IPs
5. **Configure DNS** server for name resolution

### Advanced Traffic

1. **Email traffic:** Enable SMTP/POP3 on server
2. **Database traffic:** Simulate with specific ports
3. **Gaming traffic:** Low latency, small packets
4. **Video conferencing:** Combine VoIP patterns

---

## ✅ Pre-Viva Checklist

- [ ] Packet Tracer topology built and tested
- [ ] All 4 traffic types work
- [ ] Can ping between all devices
- [ ] Services (HTTP, FTP) respond correctly
- [ ] Simulation mode shows packets flowing
- [ ] Screenshots taken for report
- [ ] Practiced demonstration (under 10 minutes)
- [ ] Can explain feature extraction
- [ ] Can explain why ML is better than port-based
- [ ] Dashboard ready to show
- [ ] Backup: topology saved, screenshots ready

---

## 🎯 Summary

You've created a **realistic network topology** that demonstrates:
- ✅ All 4 traffic classes FlowSentry classifies
- ✅ Network protocols and services
- ✅ Flow-based traffic patterns
- ✅ Integration point for ML classification

This shows **both networking knowledge AND machine learning application** - exactly what your viva examiners want to see!

---

**Time to complete:** ~30 minutes
**Difficulty:** Beginner-friendly
**Requirements:** Cisco Packet Tracer (free for students)

**Good luck with your demonstration! 🎓🚀**
