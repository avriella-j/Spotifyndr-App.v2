# app/ml/model_store.py — Model persistence (joblib save/load)

import joblib
import os
import json
from flask import current_app


class ModelStore:
    """joblib model storage."""

    @staticmethod
    def get_model_path(model_name, user_id=None):
        """Get file path for model."""
        if user_id:
            return os.path.join(
                current_app.config.get('MODELS_STORE_PATH', 'models_store/users'),
                f'user_{user_id}_{model_name}.joblib'
            )
        return os.path.join(
            current_app.config.get('MODELS_STORE_PATH', 'models_store'),
            f'global_{model_name}.joblib'
        )

    @staticmethod
    # Serialize model with joblib and write to disk
    def save_model(model, model_name, user_id=None):
        """Save model to disk."""
        filepath = ModelStore.get_model_path(model_name, user_id)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model, filepath)

    @staticmethod
    def load_model(model_name, user_id=None):
        """Load model from disk."""
        filepath = ModelStore.get_model_path(model_name, user_id)
        if os.path.exists(filepath):
            return joblib.load(filepath)
        return None

    @staticmethod
    def get_model_metadata(model_name, user_id=None):
        """Get model metadata from JSON file."""
        meta_path = os.path.join(
            current_app.config.get('MODELS_STORE_PATH', 'models_store'),
            f'{model_name}_metadata.json'
        )
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                return json.load(f)
        return None