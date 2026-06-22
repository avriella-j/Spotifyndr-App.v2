# app/ml/metrics.py — AUC-ROC, Precision@K, and recall logging

import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score
import logging


class MetricsLogger:
    """AUC-ROC, Precision@K logging."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_auc_roc(self, y_true, y_pred, model_name):
        """Log AUC-ROC score."""
        auc = roc_auc_score(y_true, y_pred)
        self.logger.info(f"{model_name} - AUC-ROC: {auc:.4f}")
        return auc
    
    # Compute precision for top K predictions
    def log_precision_at_k(self, y_true, y_pred_scores, k, model_name):
        """Log Precision@K score."""
        # Get top k predictions
        top_k_indices = np.argsort(y_pred_scores)[-k:]
        top_k_predictions = [1 if i in top_k_indices else 0 for i in range(len(y_pred_scores))]
        
        precision = precision_score(y_true, top_k_predictions)
        self.logger.info(f"{model_name} - Precision@{k}: {precision:.4f}")
        return precision
    
    def log_recall(self, y_true, y_pred, model_name):
        """Log recall score."""
        recall = recall_score(y_true, y_pred)
        self.logger.info(f"{model_name} - Recall: {recall:.4f}")
        return recall
    
    def log_training_metrics(self, metrics, model_name):
        """Log all training metrics."""
        self.logger.info(f"{model_name} Training Metrics:")
        for metric_name, value in metrics.items():
            self.logger.info(f"  {metric_name}: {value:.4f}")
