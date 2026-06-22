# app/ml/logistic_regression.py — Logistic Regression model (train + predict)

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score
import joblib


class LogisticRegressionModel:
    """LR model training + inference."""
    
    def __init__(self):
        self.model = LogisticRegression(random_state=42)
        self.is_trained = False
    
    # Train on train/test split and return metrics
    def train(self, X, y):
        """Train the logistic regression model."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate - handle edge cases
        y_pred = self.model.predict(X_test)
        unique_classes = len(np.unique(y_test))
        if unique_classes < 2:
            # Only one class in test set, return default values
            return {
                'auc': 0.5,
                'precision': precision_score(y_test, y_pred, zero_division=0)
            }

        auc = roc_auc_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)

        return {
            'auc': auc,
            'precision': precision
        }
    
    # Return prediction probabilities
    def predict(self, X):
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict_proba(X)[:, 1]
    
    def save(self, filepath):
        """Save model to file."""
        joblib.dump(self.model, filepath)
    
    def load(self, filepath):
        """Load model from file."""
        self.model = joblib.load(filepath)
        self.is_trained = True
