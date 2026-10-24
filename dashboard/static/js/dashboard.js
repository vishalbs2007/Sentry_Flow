// FlowSentry Dashboard JavaScript

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Activate button
    event.target.classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'dataset' && !window.datasetLoaded) {
        loadDatasetInfo();
        window.datasetLoaded = true;
    } else if (tabName === 'models' && !window.modelsLoaded) {
        loadModels();
        window.modelsLoaded = true;
    } else if (tabName === 'features' && !window.featuresLoaded) {
        loadFeatureImportance();
        window.featuresLoaded = true;
    }
}

// Load dataset information
async function loadDatasetInfo() {
    try {
        const response = await fetch('/api/dataset-info');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('dataset-loading').innerHTML = '❌ ' + data.error;
            return;
        }
        
        // Update stats
        document.getElementById('total-samples').textContent = data.total_samples.toLocaleString();
        document.getElementById('train-samples').textContent = data.train_samples.toLocaleString();
        document.getElementById('test-samples').textContent = data.test_samples.toLocaleString();
        document.getElementById('features-count').textContent = data.features;
        document.getElementById('classes-count').textContent = data.classes;
        
        // Show content
        document.getElementById('dataset-loading').style.display = 'none';
        document.getElementById('dataset-content').style.display = 'block';
        
        // Create class distribution chart
        createClassDistributionChart(data.class_distribution);
        
    } catch (error) {
        document.getElementById('dataset-loading').innerHTML = '❌ Failed to load dataset info: ' + error.message;
    }
}

// Create class distribution chart
function createClassDistributionChart(distribution) {
    const ctx = document.getElementById('classDistChart');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: distribution.map(d => d.class),
            datasets: [{
                label: 'Sample Count',
                data: distribution.map(d => d.count),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(118, 75, 162, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Training Set Class Distribution',
                    font: { size: 16 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Load models
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('models-loading').innerHTML = '❌ ' + data.error;
            return;
        }
        
        if (data.models.length === 0) {
            document.getElementById('models-loading').innerHTML = '❌ No trained models found. Train models first.';
            return;
        }
        
        // Sort by score descending
        data.models.sort((a, b) => b.cv_score - a.cv_score);
        
        // Create models table
        let html = '<div class="models-grid">';
        
        data.models.forEach((model, index) => {
            const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '⭐';
            const modelName = model.model_name.replace(/_/g, ' ').toUpperCase();
            
            html += `
                <div class="model-card">
                    <div><strong>${medal} ${modelName}</strong></div>
                    <div class="model-stats">
                        <div class="model-stat">
                            <div class="model-stat-value">${(model.cv_score * 100).toFixed(2)}%</div>
                            <div class="model-stat-label">CV Macro-F1</div>
                        </div>
                        <div class="model-stat">
                            <div class="model-stat-value">${model.train_time.toFixed(1)}s</div>
                            <div class="model-stat-label">Training Time</div>
                        </div>
                        <div class="model-stat">
                            <div class="model-stat-value">${model.train_samples.toLocaleString()}</div>
                            <div class="model-stat-label">Samples</div>
                        </div>
                    </div>
                    <div style="margin-top: 12px; font-size: 0.85em; color: #6b7280;">
                        Run ID: ${model.run_id}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        document.getElementById('models-table').innerHTML = html;
        
        // Show content
        document.getElementById('models-loading').style.display = 'none';
        document.getElementById('models-content').style.display = 'block';
        
        // Create comparison chart
        createModelsChart(data.models);
        
    } catch (error) {
        document.getElementById('models-loading').innerHTML = '❌ Failed to load models: ' + error.message;
    }
}

// Create models comparison chart
function createModelsChart(models) {
    const ctx = document.getElementById('modelsChart');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: models.map(m => m.model_name.replace(/_/g, ' ').toUpperCase()),
            datasets: [{
                label: 'CV Macro-F1 Score (%)',
                data: models.map(m => m.cv_score * 100),
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Model Performance Comparison (CV Macro-F1)',
                    font: { size: 16 }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Load feature importance
async function loadFeatureImportance() {
    try {
        const response = await fetch('/api/feature-importance');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('features-loading').innerHTML = '❌ ' + data.error;
            return;
        }
        
        if (data.features.length === 0) {
            document.getElementById('features-loading').innerHTML = '❌ Feature importance not available. Train Random Forest first.';
            return;
        }
        
        // Show content
        document.getElementById('features-loading').style.display = 'none';
        document.getElementById('features-content').style.display = 'block';
        
        // Create feature importance chart
        createFeatureImportanceChart(data.features);
        
    } catch (error) {
        document.getElementById('features-loading').innerHTML = '❌ Failed to load feature importance: ' + error.message;
    }
}

// Create feature importance chart
function createFeatureImportanceChart(features) {
    const ctx = document.getElementById('featuresChart');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: features.map(f => f.name),
            datasets: [{
                label: 'Importance',
                data: features.map(f => f.importance),
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Random Forest Feature Importance (Top 15)',
                    font: { size: 16 }
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('FlowSentry Dashboard loaded');
});
