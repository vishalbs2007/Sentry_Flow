# FlowSentry Complete Demo Setup Guide

This guide presents the project in the requested order:

1. install and run the NS-2 file on Ubuntu;
2. convert the NS-2 trace into a PCAP and labels;
3. show the real processed dataset;
4. show recorded model accuracy;
5. classify network-traffic flows;
6. review the predictions and explain the integration boundary.

The demo uses Ubuntu or WSL for NS-2 and Windows PowerShell for the prepared presentation scripts. If the entire repository is on Ubuntu, complete Stages 1 and 2 there, then use the manual Python commands in the alternatives section for the remaining stages.

## 1. Pre-demo checklist

Confirm that these repository files exist:

```text
demo/flowsentry.tcl
demo/tr_to_pcap.py
demo/requirements.txt
data/processed/test/test.csv
artifacts/reports/comparison.csv
artifacts/registry/decision_tree_20261014_011743/pipeline.joblib
```

Only the first three source files are included in a fresh clone. The dataset and artifact paths are generated locally and ignored by Git. If they are absent, complete “Obtaining the datasets” in `README.md`, then run ingestion, preprocessing, training, evaluation, comparison, and registration before the presentation. There is no prepared-artifact download bundle in this repository.

The minimum preparation sequence after placing ISCX-VPN2016 under `data/raw/` is:

```powershell
python -m preprocessing.ingest --raw-dir data/raw --out data/processed/manifest.json
python -m preprocessing.preprocess --manifest data/processed/manifest.json --filter ScenarioB --output data/processed
python -m models.train --model xgboost
python -m evaluation.evaluate --run-id <run-id-created-by-training>
python -m evaluation.compare
python -m models.registry register --run-id <run-id-created-by-training> --model-name "XGBoost"
```

For the supplied step scripts, the active registry model must be `decision_tree_20261014_011743`. If you rebuild the artifacts with a different run ID, update `demo/step3_classify_traffic.ps1` to load that registered pipeline or revise the script to use the registry API.

The presentation scripts assume the Windows checkout is `D:\Sentry_Flow`. Change each script's `Set-Location` line if your checkout is elsewhere.

## 2. Stage 1 - Install NS-2 on Ubuntu

Ubuntu publishes NS-2 in the `universe` repository for supported releases, including Ubuntu 22.04 LTS and 24.04 LTS.

Open an Ubuntu terminal and run:

```bash
sudo add-apt-repository universe
sudo apt update
sudo apt install -y ns2 python3 python3-venv python3-pip
```

Verify the installation:

```bash
command -v ns
ns
```

`command -v ns` should print a path. Running `ns` without a script should enter the `%` prompt; type `exit` to leave it.

If you are using WSL and the repository is stored at `D:\Sentry_Flow`, open it as:

```bash
cd /mnt/d/Sentry_Flow
```

For a native Ubuntu checkout, replace that path with the actual repository path.

## 3. Stage 2 - Prepare Python and run the NS-2 topology

Create a Linux virtual environment:

```bash
cd /mnt/d/Sentry_Flow
python3 -m venv .venv-ubuntu
source .venv-ubuntu/bin/activate
python -m pip install --upgrade pip
python -m pip install -r demo/requirements.txt
```

Run the topology from the `demo` directory so its relative `out.tr` output is predictable:

```bash
cd demo
ns flowsentry.tcl
ls -lh out.tr
head -n 5 out.tr
```

What to explain during the demo:

- `flowsentry.tcl` creates four clients, a router, and four servers;
- each client produces a different traffic pattern representing Web, VoIP, Streaming, or File Transfer;
- NS-2 records packet events in `out.tr`;
- the trace contains enqueue, dequeue, receive, timestamps, node identifiers, protocol, and packet-size information.

Return to the repository root and convert the trace:

```bash
cd ..
mkdir -p simulation/pcaps
python demo/tr_to_pcap.py \
  demo/out.tr \
  simulation/pcaps/ns2_traffic.pcap
```

The converter should create:

```text
simulation/pcaps/ns2_traffic.pcap
simulation/pcaps/ns2_traffic_labels.csv
```

Inspect the outputs:

```bash
ls -lh simulation/pcaps/ns2_traffic.pcap
column -s, -t < simulation/pcaps/ns2_traffic_labels.csv
```

This is the integration point:

```text
NS-2 topology -> out.tr -> tr_to_pcap.py -> PCAP + ground-truth CSV
```

Do not use `simulation/ns2/run_ns2.sh` for the presentation in its current state. It expects `flowsentry.tcl` and `tr_to_pcap.py` at the repository root, while both files are under `demo/`.

## 4. Stage 3 - Prepare the Windows demo environment

Open PowerShell:

```powershell
cd D:\Sentry_Flow
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r demo\requirements.txt
python scripts\verify_environment.py
```

If PowerShell blocks virtual-environment activation for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Before presenting, verify the important inputs without changing them:

```powershell
Test-Path data\processed\test\test.csv
Test-Path artifacts\reports\comparison.csv
Test-Path artifacts\registry\decision_tree_20261014_011743\pipeline.joblib
```

All three commands should print `True`.

## 5. Stage 4 - Show the dataset

Run:

```powershell
powershell -ExecutionPolicy Bypass -File demo\step1_show_traffic.ps1
```

The script shows five held-out flows and the test-set class distribution. Explain that:

- the processed data comes from ISCX-VPN2016 Scenario B;
- the held-out test set contains 11,925 flows;
- each row represents a flow, not a raw packet;
- the displayed fields include duration, forward/backward timing, packets per second, and bytes per second;
- the target is one of Web Browsing, VoIP, Streaming, or File Transfer;
- payload contents and endpoint identities are not used as model features.

Recorded class counts for the held-out set are:

| Class | Flows |
|---|---:|
| Web Browsing | 4,816 |
| VoIP | 3,442 |
| File Transfer | 3,119 |
| Streaming | 548 |

## 6. Stage 5 - Show model accuracy

Run:

```powershell
powershell -ExecutionPolicy Bypass -File demo\step2_model_accuracy.ps1
```

The script reads `artifacts/reports/comparison.csv`; it does not retrain models. Present the results as recorded artifacts:

| Model | Test accuracy | Test macro F1 |
|---|---:|---:|
| XGBoost | 98.12% | 97.16% |
| Decision Tree | 96.70% | 95.77% |
| Random Forest | 96.47% | 95.65% |
| SVM | 70.10% | 65.37% |

The script displays CV macro F1 as the selection criterion and reports test accuracy, test macro F1, macro precision, and macro recall as held-out evaluation results.

Say clearly that XGBoost was selected because it has the highest training cross-validation macro F1 (`0.9629`). Test accuracy is reported after selection; it was not used to tune or choose the winner.

Also explain that the active registry entry is still Decision Tree. Therefore, the next prepared classification stage loads Decision Tree, not the best XGBoost run.

## 7. Stage 6 - Classify network-traffic flows

Run:

```powershell
powershell -ExecutionPolicy Bypass -File demo\step3_classify_traffic.ps1
```

This script:

1. loads `data/processed/test/test.csv`;
2. selects 100 deterministic held-out flows with random seed 42;
3. loads the registered Decision Tree pipeline;
4. applies the exact persisted preprocessing and model pipeline;
5. predicts one of the four traffic classes;
6. writes `demo/classification_results.csv`.

The accuracy printed here is the accuracy of this 100-flow demonstration sample. It is not a replacement for the full test-set metrics shown in Stage 5.

## 8. Stage 7 - Review predictions

Run:

```powershell
powershell -ExecutionPolicy Bypass -File demo\step4_view_results.ps1
```

The script displays:

- total correct and incorrect predictions;
- accuracy for each traffic class;
- sample true and predicted labels;
- prediction confidence;
- a confusion matrix;
- examples of any misclassified flows.

Open the saved CSV if an examiner asks for the underlying output:

```powershell
Import-Csv demo\classification_results.csv | Select-Object -First 15 | Format-Table
```

## 9. What is and is not integrated

The demonstrated working chain is:

```text
NS-2 -> trace -> PCAP + labels

ISCX-VPN2016 processed flows -> persisted model -> predicted traffic class
```

The intended full chain is:

```text
NS-2 -> trace -> PCAP -> feature extractor -> canonical 21 features
     -> persisted model -> predicted class -> compare with NS-2 labels
```

The final full chain is currently **not verified**. A direct PCAP-classifier check in the present Windows environment stopped safely with `SchemaMismatchError`: the Scapy fallback produced simplified feature names that did not map to the 21-feature training schema. This is correct fail-closed behavior and prevents invalid predictions.

If you want to demonstrate the current limitation, run:

```powershell
python -m inference.pcap_classifier `
  --pcap simulation\pcaps\ns2_traffic.pcap `
  --output artifacts\predictions\ns2_traffic
```

Only describe this command as successful if it completes in the actual demo environment and creates prediction outputs. Otherwise, show the trace-to-PCAP integration and then use the prepared held-out-flow classification stage.

## 10. Manual alternatives

### Show the dataset without PowerShell scripts

```powershell
python -c "import pandas as pd; d=pd.read_csv('data/processed/test/test.csv', index_col=0); print(d[['duration','total_fiat','total_biat','flowPktsPerSecond','flowBytesPerSecond','target_class']].head()); print(d['target_class'].value_counts())"
```

### Show model results directly

```powershell
Import-Csv artifacts\reports\comparison.csv |
  Select-Object model_name,cv_macro_f1,test_accuracy,test_macro_f1 |
  Format-Table -AutoSize
```

### Show the model registry

```powershell
Get-Content artifacts\registry\registry.json
```

### Start the dashboard

```powershell
python -m dashboard.app
```

Open `http://127.0.0.1:5000`.

## 11. Troubleshooting

### `ns: command not found`

```bash
sudo add-apt-repository universe
sudo apt update
sudo apt install -y ns2
command -v ns
```

### `flowsentry.tcl` cannot be found

Run NS-2 from the correct directory:

```bash
cd /mnt/d/Sentry_Flow/demo
ns flowsentry.tcl
```

### Python module is missing

Activate the correct environment and reinstall the pinned demo dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r demo\requirements.txt
```

### A demo step changes to the wrong directory

The scripts currently contain:

```powershell
Set-Location D:\Sentry_Flow
```

Store the project there or replace that path in the step scripts with the real checkout path.

### Model or dataset file is missing

The prepared demo requires the processed CSV and recorded artifacts. Restore these paths before presenting:

```text
data/processed/test/test.csv
artifacts/reports/comparison.csv
artifacts/registry/decision_tree_20261014_011743/pipeline.joblib
```

### PCAP classification reports a schema mismatch

Do not bypass the error. It means the extractor output does not satisfy the model's feature contract. Continue with the held-out-flow classification demo and explain that train/inference feature parity must be completed before NS-2 PCAP predictions are valid.

## 12. Recommended presentation script

1. **NS-2:** "This topology generates four application-like traffic patterns through a shared router."
2. **Integration:** "NS-2 writes a packet-event trace; our converter turns it into a PCAP and a ground-truth flow-label file."
3. **Dataset:** "For reproducible model evaluation, we use 11,925 frozen ISCX-VPN2016 test flows with 21 statistical features."
4. **Accuracy:** "We evaluated four models. XGBoost won by cross-validation macro F1 and achieved 98.12% on the untouched test set."
5. **Classification:** "The prepared classifier now predicts 100 held-out flows with the registered Decision Tree pipeline."
6. **Results:** "The confusion matrix shows which traffic types are separated well and where mistakes occur."
7. **Limitation:** "Trace-to-PCAP integration is present; direct NS-2 PCAP classification remains fail-closed until extractor feature names match the training schema."

## 13. Cleanup

Generated demo outputs may include:

```text
demo/out.tr
simulation/pcaps/ns2_traffic.pcap
simulation/pcaps/ns2_traffic_labels.csv
demo/classification_results.csv
artifacts/predictions/
```

Keep them if they are needed as presentation evidence. Remove them only after confirming they are generated artifacts and not source data you need.
