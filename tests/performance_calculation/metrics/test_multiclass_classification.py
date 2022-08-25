#  Author:   Niels Nuyttens  <niels@nannyml.com>
#  #
#  License: Apache Software License 2.0
#  Author:   Niels Nuyttens  <niels@nannyml.com>
#
#  License: Apache Software License 2.0

"""Unit tests for performance metrics."""
from typing import Tuple

import pandas as pd
import pytest

from nannyml import PerformanceCalculator
from nannyml._typing import UseCase
from nannyml.datasets import load_synthetic_multiclass_classification_dataset
from nannyml.performance_calculation.metrics.base import MetricFactory
from nannyml.performance_calculation.metrics.multiclass_classification import (
    MulticlassClassificationAccuracy,
    MulticlassClassificationAUROC,
    MulticlassClassificationF1,
    MulticlassClassificationPrecision,
    MulticlassClassificationRecall,
    MulticlassClassificationSpecificity,
)


@pytest.fixture
def multiclass_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:  # noqa: D103
    ref_df, ana_df, tgt_df = load_synthetic_multiclass_classification_dataset()

    return ref_df, ana_df, tgt_df


@pytest.fixture()
def performance_calculator() -> PerformanceCalculator:
    return PerformanceCalculator(
        timestamp_column_name='timestamp',
        y_pred_proba={
            'prepaid_card': 'y_pred_proba_prepaid_card',
            'highstreet_card': 'y_pred_proba_highstreet_card',
            'upmarket_card': 'y_pred_proba_upmarket_card',
        },
        y_pred='y_pred',
        y_true='y_true',
        metrics=['roc_auc', 'f1', 'precision', 'recall', 'specificity', 'accuracy'],
    )


@pytest.fixture
def realized_performance_metrics(performance_calculator, multiclass_data) -> pd.DataFrame:
    performance_calculator.fit(multiclass_data[0])
    results = performance_calculator.calculate(multiclass_data[1].merge(multiclass_data[2], on='identifier'))
    return results.data


@pytest.mark.parametrize(
    'key,problem_type,metric',
    [
        ('roc_auc', UseCase.CLASSIFICATION_MULTICLASS, MulticlassClassificationAUROC),
        ('f1', UseCase.CLASSIFICATION_MULTICLASS, MulticlassClassificationF1),
        ('precision', UseCase.CLASSIFICATION_MULTICLASS, MulticlassClassificationPrecision),
        ('recall', UseCase.CLASSIFICATION_MULTICLASS, MulticlassClassificationRecall),
        ('specificity', UseCase.CLASSIFICATION_MULTICLASS, MulticlassClassificationSpecificity),
        ('accuracy', UseCase.CLASSIFICATION_MULTICLASS, MulticlassClassificationAccuracy),
    ],
)
def test_metric_factory_returns_correct_metric_given_key_and_problem_type(key, problem_type, metric):  # noqa: D103
    calc = PerformanceCalculator(
        timestamp_column_name='timestamp',
        y_pred_proba='y_pred_proba',
        y_pred='y_pred',
        y_true='y_true',
        metrics=['roc_auc', 'f1'],
    )
    sut = MetricFactory.create(key, problem_type, {'calculator': calc})
    assert sut == metric(calculator=calc)


@pytest.mark.parametrize(
    'metric, expected',
    [
        ('roc_auc', [0.90759, 0.91053, 0.90941, 0.91158, 0.90753, 0.74859, 0.75114, 0.7564, 0.75856, 0.75394]),
        ('f1', [0.7511, 0.76305, 0.75849, 0.75894, 0.75796, 0.55711, 0.55915, 0.56506, 0.5639, 0.56164]),
        ('precision', [0.75127, 0.76313, 0.7585, 0.75897, 0.75795, 0.5597, 0.56291, 0.56907, 0.56667, 0.56513]),
        ('recall', [0.75103, 0.76315, 0.75848, 0.75899, 0.75798, 0.55783, 0.56017, 0.56594, 0.56472, 0.56277]),
        ('specificity', [0.87555, 0.88151, 0.87937, 0.87963, 0.87899, 0.77991, 0.78068, 0.78422, 0.78342, 0.78243]),
        ('accuracy', [0.75117, 0.763, 0.75867, 0.75917, 0.758, 0.56083, 0.56233, 0.56983, 0.56783, 0.566]),
    ],
)
def test_metric_values_are_calculated_correctly(realized_performance_metrics, metric, expected):
    metric_values = realized_performance_metrics[metric]
    assert (round(metric_values, 5) == expected).all()