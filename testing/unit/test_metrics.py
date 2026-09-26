import unittest

def calculate_mae(y_true: list[float], y_pred: list[float]) -> float:
    """Calculates Mean Absolute Error using standard library."""
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        raise ValueError("Inputs must be non-empty and equal length.")
    return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)

class TestMetricCalculations(unittest.TestCase):
    def test_mae_calculation(self):
        y_true = [10.0, 20.0, 30.0]
        y_pred = [12.0, 18.0, 31.0]
        # Expected: (|10-12| + |20-18| + |30-31|) / 3 = 5 / 3 = 1.666666...
        mae = calculate_mae(y_true, y_pred)
        self.assertAlmostEqual(mae, 1.666666, places=5)

if __name__ == "__main__":
    unittest.main()
