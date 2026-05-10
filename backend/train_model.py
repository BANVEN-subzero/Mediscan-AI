"""
Train RandomForest models for condition prediction and triage classification.
"""
import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


# Triage mapping: condition -> triage level
# home: Minor, self-limiting conditions
# doctor: Conditions requiring medical evaluation
# emergency: Life-threatening conditions requiring immediate attention
TRIAGE_MAPPING = {
    # home
    "Acne": "home",
    "Allergy": "home",
    "Common Cold": "home",
    "Fungal infection": "home",
    "GERD": "home",
    "Impetigo": "home",
    "Psoriasis": "home",
    "Varicose veins": "home",
    "Dimorphic hemmorhoids(piles)": "home",
    
    # doctor
    "Arthritis": "doctor",
    "Bronchial Asthma": "doctor",
    "Cervical spondylosis": "doctor",
    "Chicken pox": "doctor",
    "Chronic cholestasis": "doctor",
    "Dengue": "doctor",
    "Diabetes": "doctor",
    "Drug Reaction": "doctor",
    "Gastroenteritis": "doctor",
    "Hepatitis A": "doctor",
    "Hepatitis B": "doctor",
    "Hepatitis C": "doctor",
    "Hepatitis D": "doctor",
    "Hepatitis E": "doctor",
    "Hypertension": "doctor",
    "Hyperthyroidism": "doctor",
    "Hypoglycemia": "doctor",
    "Hypothyroidism": "doctor",
    "Jaundice": "doctor",
    "Malaria": "doctor",
    "Migraine": "doctor",
    "Osteoarthristis": "doctor",
    "Peptic ulcer diseae": "doctor",
    "Pneumonia": "doctor",
    "Tuberculosis": "doctor",
    "Typhoid": "doctor",
    "Urinary tract infection": "doctor",
    "AIDS": "doctor",
    "Alcoholic hepatitis": "doctor",
    "(vertigo) Paroymsal  Positional Vertigo": "doctor",
    
    # emergency
    "Heart attack": "emergency",
    "Paralysis (brain hemorrhage)": "emergency",
}


def get_triage_for_condition(condition: str) -> str:
    """Get triage level for a given condition."""
    # Normalize condition name for lookup
    normalized = condition.strip()
    if normalized in TRIAGE_MAPPING:
        return TRIAGE_MAPPING[normalized]
    # Default to doctor if not in mapping
    return "doctor"


def train_models():
    """Train condition and triage prediction models."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    models_dir = os.path.join(script_dir, "models")
    
    # Create models directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    # Load training data
    train_path = os.path.join(data_dir, "training_data.csv")
    test_path = os.path.join(data_dir, "test_data.csv")
    
    print(f"Loading training data from {train_path}...")
    train_df = pd.read_csv(train_path)
    
    print(f"Loading test data from {test_path}...")
    test_df = pd.read_csv(test_path)
    
    # The target column is 'prognosis'
    symptom_columns = [col for col in train_df.columns if col not in ['prognosis', 'Unnamed: 133']]
    
    print(f"Found {len(symptom_columns)} symptom columns")
    
    # Prepare features and labels
    X_train = train_df[symptom_columns].values
    y_condition_train = train_df['prognosis'].values
    
    X_test = test_df[symptom_columns].values
    y_condition_test = test_df['prognosis'].values
    
    # Create triage labels
    y_triage_train = [get_triage_for_condition(c) for c in y_condition_train]
    y_triage_test = [get_triage_for_condition(c) for c in y_condition_test]
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train condition prediction model
    print("\nTraining condition prediction model...")
    condition_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    condition_model.fit(X_train, y_condition_train)
    
    # Evaluate condition model
    y_condition_pred = condition_model.predict(X_test)
    condition_accuracy = accuracy_score(y_condition_test, y_condition_pred)
    print(f"Condition model accuracy: {condition_accuracy:.4f}")
    
    # Train triage prediction model
    print("\nTraining triage prediction model...")
    triage_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    triage_model.fit(X_train, y_triage_train)
    
    # Evaluate triage model
    y_triage_pred = triage_model.predict(X_test)
    triage_accuracy = accuracy_score(y_triage_test, y_triage_pred)
    print(f"Triage model accuracy: {triage_accuracy:.4f}")
    print("\nTriage classification report:")
    print(classification_report(y_triage_test, y_triage_pred))
    
    # Save models
    condition_model_path = os.path.join(models_dir, "condition_model.pkl")
    triage_model_path = os.path.join(models_dir, "triage_model.pkl")
    metadata_path = os.path.join(models_dir, "metadata.pkl")
    
    with open(condition_model_path, 'wb') as f:
        pickle.dump(condition_model, f)
    print(f"Saved condition model to {condition_model_path}")
    
    with open(triage_model_path, 'wb') as f:
        pickle.dump(triage_model, f)
    print(f"Saved triage model to {triage_model_path}")
    
    # Save metadata
    metadata = {
        'symptom_columns': symptom_columns,
        'conditions': sorted(train_df['prognosis'].unique().tolist()),
        'triage_levels': ['home', 'doctor', 'emergency'],
        'condition_accuracy': condition_accuracy,
        'triage_accuracy': triage_accuracy,
    }
    
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Saved metadata to {metadata_path}")
    
    print("\nTraining complete!")
    return metadata


if __name__ == "__main__":
    metadata = train_models()
    print(f"\nConditions ({len(metadata['conditions'])}):")
    for c in metadata['conditions']:
        print(f"  - {c} -> {get_triage_for_condition(c)}")
