from __future__ import annotations
import json
import os
import pickle
import re
import sys
import traceback

print("[DEBUG] Starting app...", file=sys.stderr)

# Optional imports with error handling
try:
    import numpy as np
    print("[DEBUG] NumPy imported successfully", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] NumPy not available: {e}", file=sys.stderr)
    np = None

try:
    from datetime import timedelta
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
    from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine, func
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import declarative_base, sessionmaker
    from werkzeug.security import check_password_hash, generate_password_hash
    import logging
    print("[DEBUG] Core imports successful", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] Core imports failed: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Optional CloudWatch imports
try:
    import boto3
    import watchtower
    from cloudwatch_metrics import metrics, setup_standard_alarms
    HAS_CLOUDWATCH = True
    print("[DEBUG] CloudWatch imports successful", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] CloudWatch libraries not available: {e}", file=sys.stderr)
    HAS_CLOUDWATCH = False

# Load ML models with error handling
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")
print(f"[DEBUG] Models dir: {models_dir}", file=sys.stderr)

condition_model = None
triage_model = None
model_metadata = None

def load_models():
    global condition_model, triage_model, model_metadata
    try:
        paths = {
            "condition": os.path.join(models_dir, "condition_model.pkl"),
            "triage": os.path.join(models_dir, "triage_model.pkl"),
            "metadata": os.path.join(models_dir, "metadata.pkl")
        }
        
        print(f"[DEBUG] Checking model files...", file=sys.stderr)
        for name, path in paths.items():
            if not os.path.exists(path):
                print(f"[DEBUG] Warning: {name} model file not found at {path}", file=sys.stderr)
                print(f"[DEBUG] Directory contents: {os.listdir(models_dir) if os.path.exists(models_dir) else 'Directory not found'}", file=sys.stderr)
        
        if os.path.exists(paths["condition"]):
            with open(paths["condition"], 'rb') as f:
                condition_model = pickle.load(f)
            print(f"[DEBUG] Loaded condition model", file=sys.stderr)
        
        if os.path.exists(paths["triage"]):
            with open(paths["triage"], 'rb') as f:
                triage_model = pickle.load(f)
            print(f"[DEBUG] Loaded triage model", file=sys.stderr)
        
        if os.path.exists(paths["metadata"]):
            with open(paths["metadata"], 'rb') as f:
                model_metadata = pickle.load(f)
            print(f"[DEBUG] Loaded metadata", file=sys.stderr)
        
        print("[DEBUG] Models loaded (or skipped if missing)", file=sys.stderr)
    except Exception as e:
        print(f"[DEBUG] Error loading models: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

load_models()

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()

def _get_env(key: str, default: str) -> str:
    v = os.environ.get(key)
    if v is None:
        return default
    v = str(v).strip()
    return v if v else default

def create_app() -> Flask:
    app = Flask(__name__)
    print("[DEBUG] Created Flask app", file=sys.stderr)
    
    allowed_origins = _get_env("ALLOWED_ORIGINS", "*")
    CORS(app, resources={r"/*": {"origins": allowed_origins}})
    print(f"[DEBUG] CORS configured with origins: {allowed_origins}", file=sys.stderr)

    app.config["JWT_SECRET_KEY"] = _get_env("JWT_SECRET_KEY", "dev-change-me")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
    JWTManager(app)
    print("[DEBUG] JWT configured", file=sys.stderr)

    # Configure logging
    log_level = logging.INFO
    logging.basicConfig(level=log_level)
    app.logger.setLevel(log_level)

    if HAS_CLOUDWATCH:
        aws_region = _get_env("AWS_REGION", "")
        aws_access_key = _get_env("AWS_ACCESS_KEY_ID", "")
        aws_secret_key = _get_env("AWS_SECRET_ACCESS_KEY", "")
        if aws_region and aws_access_key and aws_secret_key:
            try:
                boto3_client = boto3.client(
                    "logs",
                    region_name=aws_region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
                cloudwatch_handler = watchtower.CloudWatchLogHandler(
                    boto3_client=boto3_client,
                    log_group_name="MediScanLogs",
                    log_stream_name="FlaskBackend"
                )
                app.logger.addHandler(cloudwatch_handler)
                logging.getLogger("werkzeug").addHandler(cloudwatch_handler)
                app.logger.info("CloudWatch logging configured successfully")
                if 'setup_standard_alarms' in globals():
                    setup_standard_alarms()
                    app.logger.info("CloudWatch alarms configured successfully")
            except Exception as e:
                app.logger.error(f"Failed to configure CloudWatch: {e}")

    # Database setup
    db_url = _get_env(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mediscan.db')}"
    )
    print(f"[DEBUG] Database URL: {db_url}", file=sys.stderr)
    
    try:
        engine = create_engine(db_url, future=True)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
        Base.metadata.create_all(bind=engine)
        print("[DEBUG] Database setup complete", file=sys.stderr)
    except Exception as e:
        print(f"[DEBUG] Database setup failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email"))
        password = str(data.get("password") or "")

        if not email or "@" not in email:
            return jsonify({"detail": "Valid email is required"}), 400
        if len(password) < 6:
            return jsonify({"detail": "Password must be at least 6 characters"}), 400

        db = SessionLocal()
        try:
            user = User(email=email, password_hash=generate_password_hash(password))
            db.add(user)
            db.commit()
            db.refresh(user)
            access_token = create_access_token(identity=str(user.id))
            return jsonify({"accessToken": access_token, "user": {"id": user.id, "email": user.email}})
        except IntegrityError:
            db.rollback()
            return jsonify({"detail": "Email already registered"}), 409
        finally:
            db.close()

    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email"))
        password = str(data.get("password") or "")

        if not email or not password:
            return jsonify({"detail": "Email and password are required"}), 400

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).one_or_none()
            if user is None or not check_password_hash(user.password_hash, password):
                return jsonify({"detail": "Invalid credentials"}), 401
            if not user.is_active:
                return jsonify({"detail": "User is disabled"}), 403
            access_token = create_access_token(identity=str(user.id))
            return jsonify({"accessToken": access_token, "user": {"id": user.id, "email": user.email}})
        finally:
            db.close()

    @app.get("/api/auth/me")
    @jwt_required()
    def me():
        user_id = int(get_jwt_identity())
        db = SessionLocal()
        try:
            user = db.get(User, user_id)
            if user is None:
                return jsonify({"detail": "User not found"}), 404
            return jsonify({"id": user.id, "email": user.email})
        finally:
            db.close()

    @app.post("/api/analyze")
    @jwt_required()
    def analyze_route():
        data = request.get_json(silent=True) or {}
        return jsonify({
            "triageLevel": "doctor",
            "triageTitle": "Consider seeing a clinician",
            "triageDesc": "Your symptoms may warrant medical evaluation",
            "possibleConditions": [],
            "recommendedNextSteps": ["Rest and monitor your symptoms"],
            "warningSigns": [],
            "followUpQuestions": [],
            "analysisMethod": "simple"
        })

    @app.post("/api/followup")
    @jwt_required()
    def followup_route():
        data = request.get_json(silent=True) or {}
        return jsonify({"answer": "Thank you for your follow-up question!"})

    print("[DEBUG] Routes registered", file=sys.stderr)
    return app

if __name__ == "__main__":
    print("[DEBUG] __main__ block executing", file=sys.stderr)
    try:
        app = create_app()
        host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", "8000")))
        print(f"[DEBUG] Starting server on {host}:{port}", file=sys.stderr)
        app.run(host=host, port=port, debug=False)
    except Exception as e:
        print(f"[DEBUG] Fatal error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
