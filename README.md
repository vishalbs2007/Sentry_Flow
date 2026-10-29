# FlowSentry

FlowSentry is an academic network-traffic classification project. It converts packet captures into bidirectional flow statistics and uses supervised machine-learning models to classify each flow as **Web Browsing**, **VoIP**, **Streaming**, or **File Transfer**. Classification uses timing, volume, and directional flow behavior; it does not inspect application payloads.

For the complete presentation workflow, including running the NS-2 simulation on Ubuntu, see [DEMO_SETUP_GUIDE.md](DEMO_SETUP_GUIDE.md).

## What the project demonstrates

```text
Network simulation or packet capture
                |
                v
        packets / NS-2 trace
                |
                v
     PCAP and five-tuple grouping
                |
                v
       bidirectional network flows
                |
                v
  timing and volume feature extraction
                |
                v
 persisted preprocessing + ML pipeline
                |
                v
 Web / VoIP / Streaming / File Transfer
```

The project includes:

- an NS-2 topology that generates four recognizable traffic patterns;
- an NS-2 trace-to-PCAP converter and ground-truth label generator;
- preprocessing for the ISCX-VPN2016 flow dataset;
- Decision Tree, Random Forest, SVM, and XGBoost training pipelines;
- test-set evaluation, per-class metrics, confusion matrices, and model comparison artifacts;
- a model registry and PCAP-classification CLI;
- PowerShell scripts for a repeatable classroom demonstration;
- a Flask dashboard for viewing project artifacts.

## Dataset and features

The current local demonstration dataset is derived from **ISCX-VPN2016 Scenario B**. Raw datasets, processed splits, trained models, and generated artifacts are intentionally ignored by Git and are not included in a fresh clone. The values below come from the prepared local `data/processed/preprocessing_summary.json` artifact:

| Item | Recorded value |
|---|---:|
| Mapped rows before deduplication | 101,108 |
| Rows after deduplication | 59,621 |
| Training rows | 47,696 |
| Held-out test rows | 11,925 |
| Web Browsing test rows | 4,816 |
| VoIP test rows | 3,442 |
| File Transfer test rows | 3,119 |
| Streaming test rows | 548 |

The canonical schema contains 21 numeric flow features. Most are timing statistics such as duration and forward, backward, and whole-flow inter-arrival times. It also includes packet and byte rates. IP addresses, MAC addresses, payload content, and the target label are not model inputs.

Important data files:

- `data/raw/` - source ARFF archives and extracted dataset files;
- `data/processed/train/train.csv` - training partition;
- `data/processed/test/test.csv` - frozen test partition;
- `data/processed/preprocessing_summary.json` - row counts and fitted preprocessing summary;
- `config/feature_schema.yaml` - canonical feature contract;
- `config/label_mapping.yaml` - source-label to project-class mapping.

### Obtaining the datasets

Download datasets only from their official sources after reviewing their current licence terms:

| Dataset | Official source | Expected local path | Use in FlowSentry |
|---|---|---|---|
| ISCX VPN-nonVPN 2016 | https://www.unb.ca/cic/datasets/vpn.html | `data/raw/ISCX-VPN2016/` | Primary application-category dataset |
| CIC-IDS2017 | https://www.unb.ca/cic/datasets/ids-2017.html | `data/raw/CIC-IDS2017/` | Optional; attack labels are not equivalent to the four FlowSentry classes |

ISCX-VPN2016 should be cited as: Draper-Gil et al., “Characterization of Encrypted and VPN Traffic Using Time-Related Features,” ICISSP 2016. CIC-IDS2017 should be cited as: Sharafaldin et al., “Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization,” ICISSP 2018.

Do not commit downloaded datasets. After placing the ISCX-VPN2016 files under `data/raw/`, generate the manifest and processed split:

```powershell
python -m preprocessing.ingest --raw-dir data/raw --out data/processed/manifest.json
python -m preprocessing.preprocess `
  --manifest data/processed/manifest.json `
  --config config/default.yaml `
  --label-config config/label_mapping.yaml `
  --filter ScenarioB `
  --output data/processed
```

Inspect `data/processed/preprocessing_summary.json` and confirm the label mapping before training. To reproduce model artifacts from a clean checkout:

```powershell
python -m models.train --model decision_tree
python -m models.train --model random_forest
python -m models.train --model svm
python -m models.train --model xgboost

# Replace <run-id> with each directory created under artifacts/runs/.
python -m evaluation.evaluate --run-id <run-id>
python -m evaluation.compare

# Register the run selected by CV macro F1.
python -m models.registry register --run-id <run-id> --model-name "Selected model"
```

Training all models can take substantial time. For a classroom demo, prepare and verify the ignored `data/processed/` and `artifacts/` directories on the presentation machine in advance. This repository does not currently publish a separate prepared-artifact bundle.

## Models and recorded results

Model selection is based on cross-validation macro F1 on the training data, not on test accuracy. The final decision record selects `xgboost_20261024_124732` as the best evaluated run.

When the prepared local artifacts are present, the following values come from `artifacts/reports/comparison.csv`:

| Model | CV macro F1 | Test accuracy | Test macro F1 | Training rows |
|---|---:|---:|---:|---:|
| XGBoost | 0.9629 | 98.12% | 0.9716 | 47,696 |
| Decision Tree | 0.9438 | 96.70% | 0.9577 | 47,696 |
| Random Forest | 0.9404 | 96.47% | 0.9565 | 47,696 |
| SVM | 0.6555 | 70.10% | 0.6537 | 20,032 |

The SVM run used a stratified training subsample under the project's scalability policy. The active entry in `artifacts/registry/registry.json` is currently the Decision Tree run, even though XGBoost is the best recorded evaluation run. This distinction matters when using the PCAP CLI without `--model-id`.

## Repository structure

| Path | Responsibility |
|---|---|
| `capture/` | Live packet-capture support |
| `common/` | Configuration, paths, logging, and typed errors |
| `config/` | Runtime, feature-schema, label, and model configuration |
| `dashboard/` | Flask dashboard and static assets |
| `data/` | Raw, processed, and small sample data |
| `demo/` | Presentation scripts, NS-2 topology, and trace converter |
| `evaluation/` | Frozen-test evaluation and model comparison |
| `flow/` | PCAP extraction, normalization, and Scapy fallback |
| `inference/` | PCAP and real-time classifier entry points |
| `models/` | Model implementations, tuning, training, and registry |
| `preprocessing/` | Ingestion, cleaning, splitting, validation, and pipelines |
| `simulation/` | NS-2, Packet Tracer, PCAP, and label assets |
| `artifacts/` | Recorded runs, reports, registry entries, logs, and predictions |
| `tests/` | Unit, integration, and end-to-end tests |

## Environment setup

The repository's demo dependencies are pinned in `demo/requirements.txt`.

### Windows PowerShell

```powershell
cd D:\Sentry_Flow
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r demo\requirements.txt
python scripts\verify_environment.py
```

The current demo PowerShell scripts contain `Set-Location D:\Sentry_Flow`. If the repository is stored elsewhere, update that line in the step scripts or run their underlying commands manually.

### Ubuntu or WSL

```bash
cd /path/to/Sentry_Flow
python3 -m venv .venv-ubuntu
source .venv-ubuntu/bin/activate
python -m pip install --upgrade pip
python -m pip install -r demo/requirements.txt
python scripts/verify_environment.py
```

Ubuntu-specific NS-2 installation and execution are covered in [DEMO_SETUP_GUIDE.md](DEMO_SETUP_GUIDE.md).

## Common commands

Run the tests:

```powershell
python -m pytest
```

Train one of the four supported models:

```powershell
python -m models.train --model decision_tree
python -m models.train --model random_forest
python -m models.train --model svm
python -m models.train --model xgboost
```

Evaluate a recorded run:

```powershell
python -m evaluation.evaluate --run-id xgboost_20261024_124732
```

Start the dashboard:

```powershell
python -m dashboard.app
```

Then open `http://127.0.0.1:5000`.

Classify a PCAP with the active registry model:

```powershell
python -m inference.pcap_classifier --pcap data\sample\test_traffic.pcap --output artifacts\predictions\test_traffic
```

The output argument is a directory, not a CSV filename.

## Current limitations

- The best evaluated XGBoost run is not the active model in the current registry; the active model is Decision Tree.
- The NS-2 simulation and trace-to-PCAP conversion work as a separate demonstration stage. The checked-in automated Linux runner uses stale root-relative paths, so the setup guide uses corrected manual commands.
- Direct PCAP-to-model classification is fail-closed when extracted columns do not match the 21-feature training schema. In the current Windows environment, the Scapy fallback produced simplified columns and the classifier correctly stopped with `SchemaMismatchError`. Do not present NS-2 PCAP classification as verified until extractor aliases and train/inference feature parity are completed.
- The PowerShell classification demonstration uses 100 deterministic samples from the held-out processed dataset. It demonstrates model prediction, but it is not live capture and is not the same as classifying the generated NS-2 PCAP.
- Model performance is specific to the recorded ISCX-VPN2016 split and should not be generalized to arbitrary networks without external validation.

## Safety and responsible use

Capture traffic only on networks you own or are authorized to monitor. Packet captures may contain sensitive metadata. FlowSentry is designed to classify statistical flow behavior without payload inspection; do not extend the project to log or classify payload content.

## Documentation map

The two user-facing entry documents are:

1. `README.md` - project purpose, architecture, data, models, commands, and limitations;
2. `DEMO_SETUP_GUIDE.md` - complete setup and presentation sequence.

Detailed internal specifications, decision records, verification evidence, and task reports remain under `files/` and `docs/` for traceability.
