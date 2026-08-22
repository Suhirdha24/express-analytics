import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Add project root directory to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

# Check python virtual environment or current python executable
PYTHON_EXE = sys.executable

def start_services():
    print("=" * 60)
    print("🚀 Starting DocuMind Application Stack...")
    print("=" * 60)

    # 1. Run sample document ingestion if needed
    print("\n[1/3] Verifying document index state...")
    try:
        subprocess.run([PYTHON_EXE, "scripts/ingest_sample_docs.py"], check=True)
    except Exception as e:
        print(f"Warning during ingestion: {e}")

    # 2. Launch FastAPI Backend Service
    print("\n[2/3] Starting FastAPI Backend Service on http://localhost:8000 ...")
    api_process = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=root_dir
    )

    # Wait briefly for FastAPI server to initialize
    time.sleep(3)

    # 3. Launch Streamlit Frontend Service
    print("\n[3/3] Starting Streamlit Interactive Dashboard on http://localhost:8501 ...")
    ui_process = subprocess.Popen(
        [
            PYTHON_EXE, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port=8501", "--server.address=0.0.0.0",
            "--server.headless=true", "--browser.gatherUsageStats=false"
        ],
        cwd=root_dir
    )

    print("\n" + "=" * 60)
    print("🎉 DocuMind is live and running!")
    print("   • API Backend & Docs : http://localhost:8000/docs")
    print("   • Streamlit Dashboard: http://localhost:8501")
    print("=" * 60)
    print("\nPress Ctrl+C to stop all services.\n")

    try:
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        api_process.terminate()
        ui_process.terminate()
        print("DocuMind services stopped cleanly.")

if __name__ == "__main__":
    start_services()
