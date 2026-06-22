import pytest
import numpy as np
from app.ml.logistic_regression import LogisticRegressionModel
from app.ml.metrics import MetricsLogger


def test_lr_training_with_metrics():
    """Test LR model training with metrics logging."""
    model = LogisticRegressionModel()
    # Need more samples for train/test split to have both classes
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18]])
    y = np.array([0, 1, 0, 1, 0, 1])

    metrics = model.train(X, y)

    logger = MetricsLogger()
    logger.log_training_metrics(metrics, 'test_model')

    assert model.is_trained is True
    assert 'auc' in metrics
