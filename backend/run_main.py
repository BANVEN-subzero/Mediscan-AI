
import sys
import os

# Set up logging to a file
log_file = os.path.join(os.path.dirname(__file__), "backend.log")
print(f"Logging to {log_file}")

# Redirect stdout and stderr to the log file
sys.stdout = open(log_file, "w", encoding="utf-8")
sys.stderr = sys.stdout

print("Starting MediScan Backend...")

# Now import and run main
try:
    with open(os.path.join(os.path.dirname(__file__), "main.py"), encoding="utf-8") as f:
        code = compile(f.read(), "main.py", "exec")
        exec(code, globals())
except Exception as e:
    print(f"Error running main.py: {e}")
    import traceback
    traceback.print_exc()

sys.stdout.close()
sys.stderr.close()
