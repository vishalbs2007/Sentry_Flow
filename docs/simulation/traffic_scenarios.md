# Traffic Scenarios - FlowSentry Network Simulation

**Task:** CN-023 - Network Topology Design & Packet Tracer Integration  
**Purpose:** Generate sample traffic for each of the four classes FlowSentry classifies

## Overview

This document describes how to generate traffic for each class using Cisco Packet Tracer.
The traffic will be exported as PCAP files for testing FlowSentry's classification.

## Traffic Classes

| Class | Source | Destination | Protocol | Port | Duration |
|-------|--------|-------------|----------|------|----------|
| Web Browsing | Client1 | Web Server | TCP | 80 | 10-15s |
| VoIP | Client2 | VoIP Server | UDP | 5060 | 20-30s |
| Streaming | Client3 | Streaming Server | TCP | 80 | 30-45s |
| File Transfer | Client4 | FTP Server | TCP | 21 | 15-20s |

## Prerequisites

1. Packet Tracer topology built per `docs/simulation/topology.md`
2. All servers configured and running
3. Client devices assigned IPs (10.0.0.10-13)
4. Router routing configured

## Traffic Generation Procedure

### Step 1: Prepare for Capture

1. Open `simulation/packet_tracer/flowsentry_topology.pkt` in Packet Tracer
2. Navigate to **Simulation Mode** (bottom right, play button icon)
3. Click **Edit Filters** → Select all protocols (HTTP, SIP, RTSP, FTP)
4. Ensure **Capture** is enabled on Router R1, Gi0/1 (server-side interface)

### Step 2: Generate Traffic

#### Web Browsing Traffic

1. Click on **Client1** (10.0.0.10)
2. Go to **Desktop** → **Web Browser**
3. Enter URL: `http://10.0.1.100`
4. Click **Next** repeatedly to generate multiple requests
5. After 10-15 requests, click **Add PDU** to send
6. Wait for traffic to complete (Packets should appear in Simulation Window)
7. **Stop capture** and **Export** as `simulation/pcaps/web_browsing.pcap`

#### VoIP Traffic

1. Click on **Client2** (10.0.0.11)
2. Go to **Applications** → **Telephony** → **Phone**
3. Enter destination: `10.0.1.101` (VoIP Server)
4. Click **Call** to establish VoIP session
5. Wait for 20-30 seconds of call simulation
6. Click **End Call**
7. **Stop capture** and **Export** as `simulation/pcaps/voip.pcap`

#### Streaming Traffic

1. Click on **Client3** (10.0.0.12)
2. Go to **Desktop** → **Web Browser**
3. Enter URL: `http://10.0.1.102/stream` (or video file URL)
4. If using HTTP server with video, download/played video file
5. Allow continuous playback for 30-45 seconds
6. **Stop capture** and **Export** as `simulation/pcaps/streaming.pcap`

#### File Transfer Traffic

1. Click on **Client4** (10.0.0.13)
2. Open **Command Prompt**
3. Connect to FTP server:
   ```cmd
   ftp 10.0.1.103
   username: user
   password: pass
   ```
4. Download large file:
   ```cmd
   get largefile.zip
   ```
5. Wait for transfer to complete (15-20 seconds)
6. **Stop capture** and **Export** as `simulation/pcaps/file_transfer.pcap`

## Expected Traffic Patterns

### Web Browsing
- Small packets (HTTP headers + page content)
- Sustained bidirectional traffic
- Multiple request/response pairs
- Duration: ~10-15 seconds

### VoIP
- Small, regular packets
- Bidirectional voice stream
- Consistent timing (10-20ms intervals)
- Duration: ~20-30 seconds

### Streaming
- Large packets (video/audio data)
- Asymmetric traffic (server → client)
- Sustained high throughput
- Duration: ~30-45 seconds

### File Transfer
- Large packets (file data)
- Bidirectional control + data
- Sustained throughput
- Duration: ~15-20 seconds

## Export Instructions

### From Packet Tracer Simulation Window

1. In **Simulation Mode**, watch packets flow
2. Click **Capture/Forward** to see packet details
3. When sufficient traffic captured (50-100 packets):
   - Click **Export** button
   - Select **Pcap** format
   - Save to `simulation/pcaps/`
   - Name appropriately (web_browsing.pcap, etc.)

### Alternative: Use Wireshark

1. Add a PC to the network as "capture device"
2. Install Wireshark on the PC
3. Configure port mirroring if possible
4. Start capture in Wireshark
5. Generate traffic as above
6. Export from Wireshark as PCAP

## Verification Checklist

After exporting each PCAP:

- [ ] PCAP file created and readable
- [ ] Contains TCP/UDP traffic
- [ ] Has recognizable protocol (HTTP, SIP, etc.)
- [ ] Sufficient packet count (50+ packets recommended)
- [ ] Timestamps show duration (10+ seconds)
- [ ] Five-tuple visible in packet details

## Troubleshooting

### No Traffic in Capture
- Check that traffic generation completed
- Verify capture started before traffic generation
- Check Router interface configuration

### Traffic Not Visible
- Check firewall settings on clients
- Verify server services are running
- Check IP connectivity with ping

### Export Fails
- Ensure sufficient traffic captured first
- Try different export format
- Use Wireshark as alternative

## Screenshots to Capture

For documentation:

1. **Web Traffic:**
   - Client1 Web Browser with page loaded
   - Simulation window showing HTTP packets

2. **VoIP Traffic:**
   - Client2 Phone with active call
   - SIP/RTP packet flow in Simulation Window

3. **Streaming Traffic:**
   - Client3 with video streaming
   - Large packet flow from server

4. **File Transfer:**
   - Client4 Command Prompt with FTP session
   - FTP commands and data packets

## Related Documentation

- `topology.md` - Network topology design
- `../README.md` - Simulation overview

---

**Status:** Traffic scenarios documented and ready for implementation.
