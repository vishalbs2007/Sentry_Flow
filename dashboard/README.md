# FlowSentry Web Dashboard

Simple Flask-based web dashboard for visualizing FlowSentry ML pipeline.

## Features

- 📊 **Dataset Statistics** - View training/test split and class distribution
- 🤖 **Model Comparison** - Compare all 4 trained models (Decision Tree, Random Forest, SVM, XGBoost)
- 🔍 **Feature Importance** - Visualize which flow features matter most
- 🌐 **Network Topology** - Cisco Packet Tracer integration guide
- 📈 **Interactive Charts** - Visual representation of model performance

## Quick Start

### 1. Install Dependencies

```powershell
cd d:\Sentry_Flow
pip install Flask
```

Or install from requirements:
```powershell
pip install -r requirements.txt
```

### 2. Run Dashboard

```powershell
python -m dashboard.app
```

### 3. Open Browser

Navigate to: **http://localhost:5000**

## Dashboard Tabs

### 📈 Overview
- Project goal and approach
- 4 traffic classes explained
- Classification pipeline diagram
- Team information

### 📁 Dataset
- Total samples (training + test)
- Feature count
- Class distribution chart
- Shows balanced/imbalanced classes

### 🤖 Models
- All trained models ranked by CV Macro-F1
- Training time comparison
- Visual performance comparison
- Run IDs for traceability

### 🔍 Features
- Random Forest feature importance
- Top 15 most important features
- Insight: Timing features dominate

### 🌐 Network
- Cisco Packet Tracer topology overview
- Network architecture details
- Traffic scenarios (Web, VoIP, Streaming, FTP)
- Quick start guide

## Requirements

- Python 3.8+
- Flask 3.1.0
- Trained models in `artifacts/runs/`
- Dataset in `data/processed/`

## Architecture

```
dashboard/
├── app.py              # Flask application with API endpoints
├── templates/
│   └── index.html      # Main dashboard HTML
├── static/
│   ├── css/
│   │   └── style.css   # Dashboard styling
│   └── js/
│       └── dashboard.js # Client-side logic, charts
└── README.md           # This file
```

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/dataset-info` - Dataset statistics (JSON)
- `GET /api/models` - Trained models info (JSON)
- `GET /api/feature-importance` - Feature importance data (JSON)
- `GET /api/registry` - Model registry info (JSON)

## Technologies Used

- **Backend:** Flask (Python web framework)
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Chart.js 4.4.0
- **Styling:** Custom CSS with gradient themes

## Customization

### Change Port

Edit `dashboard/app.py`:
```python
app.run(host='127.0.0.1', port=5000, debug=False)
```

### Add New Tab

1. Add tab button in `templates/index.html`
2. Add tab content div
3. Add API endpoint in `app.py` if needed
4. Add client-side logic in `static/js/dashboard.js`

### Modify Styling

Edit `static/css/style.css` for colors, fonts, layout.

## Troubleshooting

### Dashboard won't start

```powershell
# Install Flask
pip install Flask

# Check Python path
python -c "import flask; print(flask.__version__)"
```

### No data showing

Ensure you have:
- Trained models: `python -m models.train --model decision_tree`
- Processed dataset: Check `data/processed/train/train.csv` exists

### Port already in use

```
OSError: [WinError 10048] Only one usage of each socket address...
```

Solution: Change port in `app.py` or kill process on port 5000:
```powershell
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

## Integration with Packet Tracer

See **Network** tab in dashboard or `docs/packet_tracer_guide.md` for complete guide.

## Development Mode

For development with auto-reload:

```python
# In app.py, change:
app.run(host='127.0.0.1', port=5000, debug=True)
```

⚠️ **Warning:** Never use debug=True in production!

## Security Notes

- Dashboard binds to `127.0.0.1` (localhost only)
- No authentication required (local development)
- No external connections
- Read-only access to artifacts
- For production deployment, add authentication!

## Future Enhancements

Potential additions (not in current scope):
- [ ] Live PCAP classification results
- [ ] Real-time traffic monitoring
- [ ] Confusion matrix visualization
- [ ] Model performance metrics over time
- [ ] Export reports as PDF
- [ ] Multi-user authentication

## License

Part of FlowSentry academic project. See main README for details.

## Authors

- Sudir Niranj R
- Vishal B S

Computer Networks - 2026
