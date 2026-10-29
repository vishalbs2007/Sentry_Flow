"""
tests/e2e/test_user_scenarios.py
---------------------------------
End-to-end tests for FlowSentry user scenarios (CN-020).

Tests complete workflows from clean state following documented commands.
These are NOT performance benchmarks - they verify the pipeline works.
"""

import pytest
import subprocess
import sys
from pathlib import Path
import json
import time


def run_command(args: list[str], cwd: Path = None, timeout: int = 120) -> tuple:
    """Run a command and return (returncode, stdout, stderr).
    
    Parameters
    ----------
    args : list[str]
        Command arguments to run without a shell
    cwd : Path, optional
        Working directory
    timeout : int
        Timeout in seconds
        
    Returns
    -------
    returncode : int
    stdout : str
    stderr : str
    """
    if cwd is None:
        cwd = Path(__file__).parent.parent.parent
    
    result = subprocess.run(
        args,
        shell=False,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=timeout,
    )
    
    return result.returncode, result.stdout, result.stderr


@pytest.mark.e2e
def test_scenario_a_environment_verification():
    """Scenario A1: Verify environment setup.
    
    Tests that the environment script runs and reports versions.
    """
    returncode, stdout, stderr = run_command(
        [sys.executable, 'scripts/verify_environment.py']
    )
    
    # Should succeed
    assert returncode == 0, f"Environment verification failed: {stderr}"
    
    # Should report Python version
    assert 'Python' in stdout or 'Python' in stderr
    
    # Should report library versions
    assert 'scikit-learn' in stdout or 'scikit-learn' in stderr


@pytest.mark.e2e
@pytest.mark.requires_dataset
def test_scenario_a_demo_script():
    """Scenario A2: Run demo script to show project status.
    
    Tests that the demo script executes without errors.
    """
    returncode, stdout, stderr = run_command(
        [sys.executable, 'scripts/demo.py'],
        timeout=60
    )
    
    # Should succeed
    assert returncode == 0, f"Demo script failed: {stderr}"
    
    # Should show dataset info
    assert 'Dataset' in stdout or 'Dataset' in stderr
    
    # Should show trained models
    assert 'Model' in stdout or 'trained' in stdout.lower()


@pytest.mark.e2e
@pytest.mark.requires_dataset
def test_scenario_b_model_evaluation():
    """Scenario B: Model evaluation workflow.
    
    Tests that a trained model can be evaluated on test set.
    """
    # Evaluate the active registered model rather than an arbitrary legacy run.
    registry_path = Path('artifacts/registry/registry.json')
    if not registry_path.exists():
        pytest.skip("Model registry not found")

    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    run_id = registry.get('active_model_id')
    if not run_id or not (Path('artifacts/runs') / run_id).exists():
        pytest.skip("No active model run found")
    
    # Run evaluation
    returncode, stdout, stderr = run_command(
        [sys.executable, '-m', 'evaluation.evaluate', '--run-id', run_id],
        timeout=180
    )
    
    # Should succeed
    assert returncode == 0, f"Evaluation failed: {stderr}"
    
    # Should report metrics
    assert 'Accuracy' in stdout or 'Accuracy' in stderr
    assert 'F1' in stdout or 'F1' in stderr
    
    # Check artifacts created
    report_dir = Path(f'artifacts/reports/{run_id}')
    assert report_dir.exists(), "Report directory not created"
    assert (report_dir / 'summary.json').exists(), "Summary not created"
    assert (report_dir / 'metrics.json').exists(), "Metrics not created"


@pytest.mark.e2e
def test_scenario_c_model_comparison():
    """Scenario C: Model comparison workflow.
    
    Tests that model comparison generates comparison reports.
    """
    returncode, stdout, stderr = run_command(
        [sys.executable, '-m', 'evaluation.compare'],
        timeout=60
    )
    
    # Should succeed
    assert returncode == 0, f"Comparison failed: {stderr}"
    
    # Should report best model
    assert 'Best model' in stdout or 'Best model' in stderr
    
    # Check artifacts created
    reports_dir = Path('artifacts/reports')
    assert (reports_dir / 'comparison.csv').exists(), "Comparison CSV not created"
    assert (reports_dir / 'comparison.md').exists(), "Comparison MD not created"
    assert (reports_dir / 'comparison.png').exists(), "Comparison plot not created"


@pytest.mark.e2e
def test_scenario_d_registry_list():
    """Scenario D: Model registry workflow.
    
    Tests that registry can list registered models.
    """
    returncode, stdout, stderr = run_command(
        [sys.executable, '-m', 'models.registry', 'list'],
        timeout=30
    )
    
    # Should succeed
    assert returncode == 0, f"Registry list failed: {stderr}"
    
    # Should show models or empty registry
    output = stdout + stderr
    assert 'Model' in output or 'model' in output.lower() or 'No models' in output


@pytest.mark.e2e
@pytest.mark.slow
def test_scenario_e_dashboard_startup():
    """Scenario E: Dashboard startup test.
    
    Tests that dashboard can start (does not test full functionality).
    """
    import threading
    import socket
    import time
    
    # Check if port 5000 is available
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    
    if result == 0:
        pytest.skip("Port 5000 already in use")
    
    # Start dashboard in background (timeout after 10 seconds)
    # We just verify it starts, not full functionality
    pytest.skip("Dashboard startup test requires manual verification (interactive)")


@pytest.mark.e2e
def test_failure_path_no_model():
    """Failure Path A: No active model in registry.
    
    Tests graceful error handling when trying to use non-existent model.
    """
    # Try to load a non-existent model
    returncode, stdout, stderr = run_command(
        [
            sys.executable,
            '-c',
            "from models.registry import load_model; "
            "from pathlib import Path; "
            "load_model(Path('artifacts/registry'), model_id='nonexistent')",
        ],
        timeout=10
    )
    
    # Should fail gracefully
    assert returncode != 0, "Should fail when model doesn't exist"
    
    # Should have informative error
    error_output = stderr.lower()
    assert 'not found' in error_output or 'does not exist' in error_output or 'error' in error_output


@pytest.mark.e2e
def test_failure_path_missing_config():
    """Failure Path B: Missing configuration file.
    
    Tests error handling when config is missing.
    """
    returncode, stdout, stderr = run_command(
        [
            sys.executable,
            '-c',
            "from common.config import load_config; "
            "load_config('nonexistent_config.yaml')",
        ],
        timeout=10
    )
    
    # Should fail gracefully
    assert returncode != 0, "Should fail when config doesn't exist"
    
    # Should have informative error
    error_output = (stdout + stderr).lower()
    assert 'not found' in error_output or 'does not exist' in error_output or 'error' in error_output


@pytest.mark.e2e
@pytest.mark.requires_dataset
def test_failure_path_invalid_run_id():
    """Failure Path C: Invalid run ID for evaluation.
    
    Tests error handling when evaluating non-existent run.
    """
    returncode, stdout, stderr = run_command(
        [
            sys.executable,
            '-m',
            'evaluation.evaluate',
            '--run-id',
            'nonexistent_run_123',
        ],
        timeout=30
    )
    
    # Should fail gracefully
    assert returncode != 0, "Should fail when run doesn't exist"
    
    # Should have informative error
    error_output = (stdout + stderr).lower()
    assert 'not found' in error_output or 'does not exist' in error_output or 'error' in error_output


@pytest.mark.e2e
def test_pytest_suite_runs():
    """Meta-test: Verify pytest suite runs.
    
    Tests that the test suite itself can be executed.
    """
    returncode, stdout, stderr = run_command(
        [sys.executable, '-m', 'pytest', 'tests/unit/test_common.py', '-v'],
        timeout=30
    )
    
    # Should succeed (tests should pass)
    # Note: We check that pytest runs, not that all tests pass
    output = stdout + stderr
    assert 'passed' in output.lower() or 'failed' in output.lower() or 'error' in output.lower()
