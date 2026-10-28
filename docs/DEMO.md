# FlowSentry Viva Demonstration Guide

**Version:** 1.0  
**Last Updated:** 2026-10-11  
**Demo Duration:** 15-20 minutes  
**Preparation Time:** 10 minutes

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Flight Checklist](#pre-flight-checklist)
3. [Demo Script](#demo-script)
4. [Talking Points](#talking-points)
5. [Q&A Preparation](#qa-preparation)
6. [Fallback Plans](#fallback-plans)

---

## Overview

### Demo Objectives

1. Demonstrate ML-based network traffic classification
2. Show flow-level feature extraction (no payload inspection)
3. Present model evaluation results (98.12% accuracy)
4. Explain packets → five-tuple → flow → features → ML → class pipeline
5. Show integration with Packet Tracer simulation

### What Will Be Demonstrated

- Network topology with 4 traffic types
- Flow-based feature extraction concept
- Trained ML models and performance metrics
- Dashboard visualization
- Classification results

### What Is Out of Scope

- Live packet capture (no Npcap installed)
- CICFlowMeter integration (requires external tool)
- Real-time classification (CN-016-017 not delivered)

---

## Pre-Flight Checklist

### 1. Environment Setup (5 minutes before demo)

```powershell
# Navigate to project
cd d:\Sentry_Flow

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Verify environment
python scripts/verify_environment.py
```

**Expected Output:**
- Python 3.x detected
- All required libraries (pandas, scikit-learn, xgboost) installed
- No errors

**If Fails:** See [Fallback Plans](#fallback-plans) → Environment Issues

---

### 2. Check Model Registry (1 minute)

```powershell
python -m models.registry list
```

**Expected Output:**
```
REGISTERED MODELS
Model: Decision Tree Classifier [ACTIVE]
  ID: decision_tree_20261014_011743
  CV Macro F1: 0.9438
  Test Macro F1: 0.9577
  Test Accuracy: 0.9670
```

**If Fails:** See [Fallback Plans](#fallback-plans) → No Models

---

### 3. Start Dashboard (2 minutes)

```powershell
# Set UTF-8 encoding (Windows)
$env:PYTHONIOENCODING = "utf-8"

# Start dashboard
python -m dashboard.app
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

**Open in Browser:** http://localhost:5000

**Verify:** All 5 tabs load (Overview, Dataset, Models, Features, Network)

**If Fails:** See [Fallback Plans](#fallback-plans) → Dashboard Issues

---

### 4. Open Packet Tracer (2 minutes)

**File:** `docs/simulation/flowsentry_demo.pkt` (if created)  
**Alternative:** Build from `QUICK_START_PACKET_TRACER.md`

**Verify:**
- All devices connected (green triangles)
- Router R1 configured (10.0.0.1, 10.0.1.1)
- Clients can ping router: `ping 10.0.0.1` from PC-Web

**If Fails:** Use fallback presentation slides

---

## Demo Script

### Introduction (2 minutes)

**Talking Points:**

> "Good morning/afternoon. I'll be demonstrating **FlowSentry**, an ML-based network traffic classification system.
>
> **The Problem:** Modern networks need to identify traffic types (Web, VoIP, Streaming, FTP) for quality-of-service management, but traditional port-based classification fails with encrypted traffic.
>
> **Our Solution:** FlowSentry classifies traffic using **flow-level statistical features** — timing patterns, packet sizes, and directional ratios — **without inspecting payload**. This works even with HTTPS and VPNs.
>
> **Key Innovation:** We extract features from bidirectional flows (5-tuple aggregation) and train 4 ML models. Our best model, XGBoost, achieves **98.12% accuracy** on the test set."

**Show:** Dashboard → Overview tab

---

### Part 1: Network Topology (3 minutes)

**Action:** Switch to Packet Tracer

**Talking Points:**

> "Here's our test network topology. We have:
>
> - 1 Router (R1) connecting two subnets
> - 1 Switch (SW1) connecting client devices
> - 4 Clients: PC-Web, PC-VoIP, PC-Stream, PC-FTP
> - 4 Servers: Server-Web, Server-VoIP, Server-Stream, Server-FTP
>
> Each client-server pair generates a specific traffic type."

**Action:** Show topology diagram

**Show:** Dashboard → Network tab (or `docs/NETWORK_TOPOLOGY.md`)

---

### Part 2: Traffic Generation & Flow Concept (3 minutes)

**Action:** Generate traffic in Packet Tracer

| Client | Action | Traffic Type |
|--------|--------|--------------|
| PC-Web | Web Browser → `http://10.0.1.100` | 🌐 Web Browsing |
| PC-VoIP | Command: `ping 10.0.1.101 -t` | 📞 VoIP (simulated) |
| PC-Stream | Command: `ping 10.0.1.102 -l 1400 -t` | 🎬 Streaming |
| PC-FTP | Command: `ftp 10.0.1.103` | 📁 File Transfer |

**Talking Points:**

> "Let me demonstrate the four traffic types...
>
> **Enable Simulation Mode** to show packets flowing.
>
> Each traffic type creates a bidirectional flow — identified by the **five-tuple**:
> - Source IP + Port
> - Destination IP + Port  
> - Protocol (TCP/UDP)
>
> Packets in both directions (forward/backward) are aggregated into a single flow for feature extraction."

**Visual:** Show packets flowing in simulation mode

**Talking Points:**

> "The key insight: each traffic type has **distinctive timing patterns**:
>
> - **Web**: Bursty, variable inter-arrival time (high variance)
> - **VoIP**: Regular, constant inter-arrival time (~20ms), small packets
> - **Streaming**: Sustained, medium-sized packets, consistent rate
> - **FTP**: Bulk transfer, maximum packet size, minimal gaps"

---

### Part 3: Feature Extraction (3 minutes)

**Action:** Switch to Dashboard → Features tab

**Talking Points:**

> "From each flow, we extract **79 statistical features** across four families, following the Review-1 specification:
>
> 1. **Time Features** (IAT - Inter-Arrival Time):
>    - Mean, std, min, max of forward/backward IAT
>    - Flow duration, active/idle times
>
> 2. **Volume Features**:
>    - Packet counts (forward/backward/total)
>    - Byte counts (forward/backward/total)
>    - Bytes per packet statistics
>
> 3. **TCP Flag Features**:
>    - Counts of FIN, SYN, RST, PSH, ACK, URG flags
>    - Forward/backward flag distributions
>
> 4. **Directional Ratio Features**:
>    - Forward/backward packet ratio
>    - Forward/backward byte ratio
>    - Average packet size differences
>
> **Feature Selection:** After training, we found that **timing features dominate** classification. Our final model uses only **9 selected features**, with IAT (Inter-Arrival Time) statistics being the most important.
>
> This chart shows the top features from Random Forest feature importance analysis."

**Visual:** Show feature importance chart (Dashboard → Features tab)

---

### Part 4: Dataset & Preprocessing (2 minutes)

**Action:** Dashboard → Dataset tab

**Talking Points:**

> "We used the **ISCX-VPN2016 dataset**, a public research dataset containing labeled network traffic flows.
>
> **Dataset Statistics:**
> - **59,621 flows** total
> - Split: 80% training (47,696), 20% test (11,925)
> - **4 traffic classes:** Web Browsing, VoIP, Streaming, File Transfer
> - Balanced distribution across classes
>
> **Preprocessing Steps:**
> 1. **Label Mapping:** Applied approved mapping from original labels to 4 target classes
> 2. **Cleaning:** Removed metadata (IPs, ports, timestamps) from model input
> 3. **Imputation:** Missing values filled with median (fitted on training only)
> 4. **Scaling:** Min-max normalization to [0,1] (fitted on training only)
> 5. **Feature Selection:** Variance + correlation + importance filtering
>
> **Anti-Leakage Guards:**
> - Test set never touched during training
> - All preprocessing fitted only on training data
> - Stratified split to preserve class distributions
> - No test data used for hyperparameter tuning"

**Visual:** Show dataset statistics and class distribution

---

### Part 5: ML Models & Results (4 minutes)

**Action:** Dashboard → Models tab

**Talking Points:**

> "We trained **four models** as specified in Review-1:
>
> 1. **Decision Tree** (baseline, interpretable)
> 2. **Random Forest** (ensemble, feature importances)
> 3. **SVM** (kernel method, trained on 42% subsample due to scalability)
> 4. **XGBoost** (gradient boosting, best performance)
>
> All models were tuned using **5-fold cross-validation** on the training set, scoring by **macro-F1** to handle class balance fairly."

**Show:** Model comparison table

**Talking Points:**

> "**Results on Test Set:**
>
> | Model | Accuracy | Macro F1 | Time/Flow |
> |-------|----------|----------|-----------|
> | **XGBoost** | **98.12%** | **97.16%** | 0.015 ms |
> | Decision Tree | 96.70% | 95.77% | 0.006 ms |
> | Random Forest | 96.47% | 95.65% | 0.015 ms |
> | SVM | 70.10% | 65.37% | 1.311 ms |
>
> **Best Model: XGBoost**
> - Selected based on CV Macro-F1 (96.29%) on training data
> - Test accuracy: **98.12%** (exceeds Review-1's 95-98% benchmark)
> - Fast inference: **0.015 ms per flow**
> - Handles all 4 classes well (no weak classes)
>
> **Why XGBoost Won:**
> - Highest cross-validation score (selection criterion)
> - Robust to overfitting through regularization
> - Handles feature interactions better than trees
> - Fast inference suitable for real-time use
>
> **SVM Limitations:**
> - Trained on 42% subsample due to O(n²) scalability
> - Poor performance likely due to insufficient training data
> - Documented limitation in our report"

**Visual:** Show confusion matrix or performance chart

---

### Part 6: Pipeline Demonstration (1 minute)

**Action:** Terminal (if time permits)

**Command:**

```powershell
# Show model evaluation (quick demo)
python -m evaluation.evaluate --run-id xgboost_20261014_012230
```

**Talking Points:**

> "Here's a quick demonstration of model evaluation. The pipeline:
>
> 1. Loads trained model from registry
> 2. Loads frozen test set (never seen during training)
> 3. Applies preprocessing pipeline (imputer + scaler + selector)
> 4. Generates predictions
> 5. Calculates metrics and saves artifacts
>
> All results are saved to `artifacts/reports/` for reproducibility."

**Skip if time is short** — go directly to conclusion

---

### Conclusion (1-2 minutes)

**Talking Points:**

> "To summarize:
>
> ✅ **Achieved:** ML-based traffic classification with **98.12% accuracy**
>
> ✅ **Privacy-Preserving:** No payload inspection — works with encrypted traffic
>
> ✅ **Flow-Based:** Features from timing patterns and packet sizes
>
> ✅ **Robust:** Proper train/test split with anti-leakage guards
>
> ✅ **Reproducible:** All results saved to artifacts with version tracking
>
> **Key Contributions:**
> - Demonstrated flow-level classification without DPI
> - Systematic comparison of 4 ML algorithms
> - Complete pipeline from PCAP concept to model registry
> - Integration with network simulation (Packet Tracer)
>
> **Limitations:**
> - PCAP capture pipeline not delivered (blocked by Npcap dependency)
> - Live classification not implemented (CN-016-017 optional)
> - SVM underperformed due to scalability constraints
>
> **Future Work:**
> - Deploy live classification on real network
> - Test on additional datasets
> - Extend to more traffic classes
>
> Thank you! Questions?"

---

## Talking Points

### Packets → Flow → Features → ML → Class Pipeline

**Visual Aid:** Draw on board or show diagram

```
Packets (Layer 3/4)
    ↓
Five-Tuple Grouping (src_ip, src_port, dst_ip, dst_port, protocol)
    ↓
Bidirectional Flow (aggregate forward + backward packets)
    ↓
Feature Extraction (79 features: timing, volume, flags, ratios)
    ↓
Preprocessing (impute, scale, select → 9 features)
    ↓
ML Model (XGBoost)
    ↓
Class Prediction (Web / VoIP / Streaming / FTP)
```

**Key Terms:**
- **Five-tuple:** Unique flow identifier (src+dst IP+port, protocol)
- **Bidirectional:** Forward (src→dst) and backward (dst→src) packets grouped
- **Flow features:** Statistical summaries (mean, std, min, max) of packet properties
- **IAT (Inter-Arrival Time):** Time between consecutive packets — most discriminative feature

---

### Why Flow Features?

**Question:** "Why not use port numbers or packet payloads?"

**Answer:**

> "**Port-based classification fails** because:
> - Modern apps use dynamic ports
> - HTTP/HTTPS share port 80/443
> - Cannot distinguish Netflix from YouTube
>
> **Payload inspection (DPI) has problems:**
> - Fails with encryption (HTTPS, VPNs)
> - Privacy concerns (reading user data)
> - Computationally expensive
> - Legally restricted in some jurisdictions
>
> **Flow-level features work because:**
> - Timing patterns differ by application behavior
> - VoIP needs constant bitrate → regular IAT
> - Video streaming needs sustained throughput → medium IAT
> - Web browsing is bursty → high IAT variance
> - Works regardless of encryption
> - Privacy-preserving (no payload read)"

---

### Why These Four Models?

**Question:** "Why Decision Tree, Random Forest, SVM, and XGBoost?"

**Answer:**

> "These were specified in Review-1, but each serves a purpose:
>
> 1. **Decision Tree:** Simple baseline, interpretable rules for viva explanation
> 2. **Random Forest:** Feature importance analysis, shows which features matter
> 3. **SVM:** Kernel method with mathematical foundation (required in Review-1)
> 4. **XGBoost:** State-of-art ensemble method, best performance
>
> We didn't add neural networks because:
> - Not in Review-1 specification
> - Overkill for tabular data with 79 features
> - Harder to explain in academic viva
> - Tree-based models work better for this problem"

---

### Data Leakage Prevention

**Question:** "How did you prevent data leakage?"

**Answer:**

> "We implemented several safeguards:
>
> 1. **Test Set Isolation:**
>    - Test set loaded only by `evaluation/` module
>    - `models/` cannot import test loader
>    - Audit logs track test set access
>
> 2. **Preprocessing Fitted on Training Only:**
>    - Imputer median calculated from training data
>    - Scaler min/max fitted on training data
>    - Feature selector uses training statistics
>    - Test data never seen until final evaluation
>
> 3. **Cross-Validation Inside Training:**
>    - 5-fold CV splits only training set
>    - Each fold respects train/validation boundary
>    - Hyperparameter tuning uses CV scores only
>
> 4. **No Test Peeking:**
>    - Model selection by CV macro-F1 (training)
>    - Test metrics reported after model frozen
>    - No retraining based on test results
>
> 5. **Reproducibility:**
>    - Seeds fixed in config
>    - Pipeline saved with model
>    - Dataset checksums recorded"

---

## Q&A Preparation

### Technical Questions

#### Q1: What is Inter-Arrival Time (IAT)?

**Answer:**

> "IAT is the time gap between consecutive packets in a flow. For example:
> - Packet 1 arrives at t=0.000s
> - Packet 2 arrives at t=0.020s
> - IAT = 0.020s (20 milliseconds)
>
> We calculate:
> - Mean IAT (average gap)
> - Std IAT (variability of gaps)
> - Min/Max IAT (shortest/longest gap)
>
> Different traffic has different IAT patterns:
> - VoIP: constant IAT (~20ms, low variance)
> - Web: bursty IAT (high variance)
> - FTP: minimal IAT (packets back-to-back)"

#### Q2: How do you handle encrypted traffic?

**Answer:**

> "Flow-level features work with encrypted traffic because:
> - We don't read payload (only headers)
> - Timing and size patterns visible in packet headers
> - Encryption doesn't hide packet arrival times or sizes
> - Application behavior (bursty vs. constant) still observable
>
> This is the key advantage over Deep Packet Inspection (DPI), which fails with HTTPS/VPNs."

#### Q3: What if multiple applications share the same flow?

**Answer:**

> "In practice, each application gets its own flow because:
> - Five-tuple uniquely identifies connections
> - Web browser to server = one flow
> - VoIP call = separate flow (different dst_ip or port)
> - TCP connections are isolated by design
>
> If somehow multiplexed (rare), the flow would show mixed characteristics and might be misclassified. This is a known limitation, but uncommon in real networks."

#### Q4: Why is SVM performance poor?

**Answer:**

> "SVM underperformed (70.10% accuracy) for two reasons:
>
> 1. **Scalability:** SVM training is O(n²) time complexity. With 47,696 training samples, training was prohibitively slow (hours).
>
> 2. **Subsampling:** We trained on 42% stratified subsample (20,000 samples) to finish in reasonable time. This reduced model quality.
>
> With a full training set, SVM would likely perform better, but the scalability constraint is a documented limitation. In production, we'd use XGBoost or Random Forest."

#### Q5: How do you handle imbalanced classes?

**Answer:**

> "Our dataset is relatively balanced (4 classes, each ~25%), so we didn't need aggressive rebalancing. We used:
>
> 1. **Stratified split:** Test set has same class proportions as training
> 2. **Macro-F1 metric:** Averages F1 across classes equally (doesn't favor majority class)
> 3. **Cross-validation stratified:** Each fold preserves class distribution
>
> If classes were highly imbalanced, we'd consider:
> - Class weights in model training
> - SMOTE oversampling (on training only)
> - Threshold tuning for high-recall classes"

#### Q6: What features are most important?

**Answer:**

> "From Random Forest feature importance analysis:
>
> **Top 5 Features:**
> 1. **Flow IAT Mean** (forward inter-arrival time average)
> 2. **Flow IAT Std** (IAT variability)
> 3. **Fwd IAT Total** (total time of forward direction)
> 4. **Bwd Packet Length Mean** (average backward packet size)
> 5. **Fwd Packet Length Max** (largest forward packet)
>
> **Key Insight:** Timing features (IAT family) dominate. Volume features are secondary. TCP flags and ratios are least important for this 4-class problem.
>
> After feature selection, we use only **9 features**, reducing dimensionality while maintaining 98% accuracy."

---

### Conceptual Questions

#### Q7: What is a flow?

**Answer:**

> "A flow is a sequence of packets sharing the same five-tuple:
> - Source IP
> - Source Port
> - Destination IP
> - Destination Port
> - Protocol (TCP/UDP)
>
> Packets in both directions are aggregated into a **bidirectional flow**. For example:
> - Client (10.0.0.10:5000) → Server (10.0.1.100:80): forward packets
> - Server (10.0.1.100:80) → Client (10.0.0.10:5000): backward packets
> - Both directions form one flow
>
> This models the full conversation, not just one-way traffic."

#### Q8: Why is this better than port-based classification?

**Answer:**

> "Port-based classification is outdated:
> - HTTP, HTTPS, FTP, SSH, VoIP, etc. can use any port
> - Dynamic port allocation (ephemeral ports)
> - Port 443 (HTTPS) used by all apps: web, streaming, file transfer
> - Cannot distinguish Netflix (streaming) from Gmail (web) — both use HTTPS
>
> Flow-based ML classification:
> - Uses behavioral patterns, not port numbers
> - Works with encrypted traffic
> - Adapts to new applications (retrain model)
> - Higher accuracy (98% vs. ~60% port-based)"

#### Q9: How is this used in real networks?

**Answer:**

> "Applications include:
>
> 1. **Quality of Service (QoS):** Prioritize VoIP/video over file transfers
> 2. **Network Monitoring:** Identify bandwidth hogs
> 3. **Security:** Detect anomalous traffic (botnet C&C, data exfiltration)
> 4. **Billing:** ISPs charge by traffic type (video streaming premium)
> 5. **Troubleshooting:** Diagnose slow applications
>
> Our system outputs flow classifications that network devices (routers, firewalls) can use for policy enforcement."

#### Q10: What are the limitations?

**Answer:**

> "**Current Limitations:**
>
> 1. **PCAP Pipeline Not Delivered:** We couldn't integrate CICFlowMeter due to Npcap system dependency. Feature extraction from live traffic is not implemented.
>
> 2. **Offline Only:** We classify pre-captured traffic, not live streams (CN-016-017 not delivered).
>
> 3. **SVM Scalability:** SVM trained on subsample, poor performance.
>
> 4. **Dataset Specific:** Model trained on ISCX-VPN2016. May not generalize to other networks without retraining.
>
> 5. **Four Classes Only:** Limited to Web/VoIP/Streaming/FTP. Real networks have more traffic types.
>
> **Future Improvements:**
> - Deploy live classification
> - Test on additional datasets
> - Extend to more classes (gaming, IoT, etc.)
> - Integrate with real routers/SDN controllers"

---

## Fallback Plans

### Fallback 1: Environment Issues

**Problem:** Python environment broken, libraries missing

**Action:**

1. **Show Pre-Captured Screenshots:**
   - Dashboard screenshots (save from working session)
   - Model comparison table
   - Feature importance chart

2. **Walk Through Code:**
   - Open `models/xgboost_model.py` in editor
   - Explain model architecture
   - Show configuration in `config/models.yaml`

3. **Show Artifacts:**
   - Open `artifacts/reports/comparison.csv` in Excel
   - Show JSON metrics files
   - Demonstrate reproducibility

**Script:**

> "Due to an environment issue, I'll demonstrate using pre-captured results. Here's the comparison table showing XGBoost achieved 98.12% accuracy..."

---

### Fallback 2: No Models in Registry

**Problem:** Registry empty or corrupted

**Action:**

1. **Show Artifacts Directly:**
   - Navigate to `artifacts/runs/xgboost_20261014_012230/`
   - Open `metrics.json` in text editor
   - Show `summary.json` for model info

2. **Explain from Documentation:**
   - Open `docs/task_reports/CN-010.md`
   - Show evaluation results
   - Reference decision record `docs/decisions/best_model.md`

**Script:**

> "The registry isn't loading, but I can show the evaluation artifacts directly. Here's the metrics JSON from the XGBoost run..."

---

### Fallback 3: Dashboard Won't Start

**Problem:** Port 5000 in use, Flask errors, encoding issues

**Action:**

1. **Use Static HTML:**
   - Open `dashboard/templates/index.html` in browser
   - Show tabs (limited interactivity)

2. **Use Packet Tracer Only:**
   - Focus on topology demonstration
   - Explain features conceptually with diagram

3. **Use Matplotlib Plots:**
   - Open PNG files in `artifacts/reports/`:
     - `comparison.png`
     - Confusion matrices
     - Feature importance plots

**Script:**

> "The dashboard isn't starting, but I have static visualizations. Here's the model comparison chart..."

---

### Fallback 4: Packet Tracer Issues

**Problem:** Packet Tracer not installed, topology file missing

**Action:**

1. **Use Topology Diagram:**
   - Open `docs/NETWORK_TOPOLOGY.md`
   - Draw on whiteboard
   - Explain conceptually

2. **Show Pre-Recorded Simulation:**
   - Screenshots of packet flow (save from working session)
   - Wireshark PCAP visualization (if available)

3. **Skip Simulation:**
   - Focus on model results
   - Explain traffic characteristics from table

**Script:**

> "Packet Tracer isn't available, but here's the topology diagram. Let me explain how each traffic type behaves..."

---

### Fallback 5: Time Runs Short

**Problem:** Only 10 minutes available

**Condensed Demo (10 min):**

1. **Introduction (1 min):** Problem, solution, key result (98.12%)
2. **Dashboard Overview (2 min):** Show tabs quickly
3. **Model Results (4 min):** Focus on comparison table and XGBoost
4. **Features (2 min):** Show feature importance chart, explain IAT
5. **Conclusion (1 min):** Achievements and limitations

**Skip:**
- Packet Tracer simulation
- Detailed preprocessing explanation
- CLI demonstrations
- Deep dive into SVM scalability

---

## Post-Demo Checklist

After demo, before leaving:

- [ ] Stop dashboard (`Ctrl+C` in terminal)
- [ ] Close Packet Tracer (save if needed)
- [ ] Deactivate virtual environment
- [ ] Note any issues for next presenter
- [ ] Save any modified Packet Tracer file
- [ ] Clear browser history if using shared machine

---

## Demo Timing Breakdown

| Section | Time | Critical? |
|---------|------|-----------|
| Introduction | 2 min | Yes |
| Topology | 3 min | Optional |
| Traffic & Flow | 3 min | Yes |
| Feature Extraction | 3 min | Yes |
| Dataset | 2 min | Optional |
| Model Results | 4 min | Yes |
| Pipeline Demo | 1 min | Optional |
| Conclusion | 1-2 min | Yes |
| **Total** | **15-20 min** | |

**Minimum Critical Path (10 min):**
- Introduction (1 min)
- Features (2 min)
- Model Results (4 min)
- Dashboard (2 min)
- Conclusion (1 min)

---

## Contact & Support

**If Issues During Demo:**
- Refer to `docs/demo_fallbacks.md` (this section)
- Have backup artifacts ready
- Stay calm, explain conceptually

**Practice Recommendation:**
- Dry-run entire demo at least once
- Time yourself
- Test all commands
- Prepare fallback materials

**Good luck with your viva! 🎓**

---

**Document Version History:**
- v1.0 (2026-10-11): Initial rehearsed demo guide
- Tested: [✅] Environment, [✅] Dashboard, [⏭️] Packet Tracer (optional)
