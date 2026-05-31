
print("Hello World from MediScan!")

print("\nTrying to import packages...")
try:
    import flask
    print("OK Flask")
except Exception as e:
    print("FAIL Flask:", e)

try:
    import numpy as np
    print("OK NumPy")
except Exception as e:
    print("FAIL NumPy:", e)

try:
    import pandas
    print("OK Pandas")
except Exception as e:
    print("FAIL Pandas:", e)

try:
    import sklearn
    print("OK scikit-learn")
except Exception as e:
    print("FAIL scikit-learn:", e)

import os
models_path = os.path.join(os.path.dirname(__file__), "models")
print("\nLooking for models at:", models_path)
if os.path.exists(models_path):
    print("OK Models directory found!")
    print("  Files in models dir:", os.listdir(models_path))
else:
    print("FAIL Models directory not found")

print("\nAll tests done!")
