
import subprocess
import sys
import os

def run_command(cmd, cwd=None):
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, ".venv", "Scripts", "python.exe")
    venv_pip = os.path.join(script_dir, ".venv", "Scripts", "pip.exe")

    print("=== MediScan Backend Setup ===")

    # Step 1: Install dependencies
    print("\n=== Step 1: Installing dependencies ===")
    packages = [
        "flask", "flask-cors", "flask-jwt-extended",
        "sqlalchemy", "numpy", "pandas", "scikit-learn",
        "boto3", "watchtower"
    ]
    run_command([venv_pip, "install", "--upgrade", "pip"], cwd=script_dir)
    for pkg in packages:
        run_command([venv_pip, "install", pkg], cwd=script_dir)

    # Step 2: Run main.py
    print("\n=== Step 2: Starting backend server ===")
    print("Running:", venv_python, "main.py")
    subprocess.run([venv_python, "main.py"], cwd=script_dir)
