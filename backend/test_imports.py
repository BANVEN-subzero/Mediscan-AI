
import sys
print("Python version:", sys.version)

print("\nTrying imports:")
try:
    import flask
    print("✓ flask OK")
except Exception as e:
    print(f"✗ flask FAILED: {e}")

try:
    import flask_cors
    print("✓ flask_cors OK")
except Exception as e:
    print(f"✗ flask_cors FAILED: {e}")

try:
    import flask_jwt_extended
    print("✓ flask_jwt_extended OK")
except Exception as e:
    print(f"✗ flask_jwt_extended FAILED: {e}")

try:
    import sqlalchemy
    print("✓ sqlalchemy OK")
except Exception as e:
    print(f"✗ sqlalchemy FAILED: {e}")

try:
    import numpy
    print("✓ numpy OK, version:", numpy.__version__)
except Exception as e:
    print(f"✗ numpy FAILED: {e}")

try:
    import pandas
    print("✓ pandas OK")
except Exception as e:
    print(f"✗ pandas FAILED: {e}")

try:
    import sklearn
    print("✓ sklearn OK")
except Exception as e:
    print(f"✗ sklearn FAILED: {e}")

try:
    import pickle
    print("✓ pickle OK")
    import os
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    print("Checking models dir at", models_dir)
    if os.path.exists(models_dir):
        print("Models dir exists, contents:", os.listdir(models_dir))
        for f in os.listdir(models_dir):
            fp = os.path.join(models_dir, f)
            print(f"  {f}: {os.path.getsize(fp)} bytes")
    else:
        print("Models dir NOT found")
except Exception as e:
    print(f"✗ pickle/models check FAILED: {e}")

print("\nDone!")
