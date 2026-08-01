import numpy as np

from decision_maker.core.ahp import AHPHelper


def test_zero_in_pairwise_matrix_returns_error():
    matrix = np.array([[1, 0], [0, 1]])
    labels = ["A", "B"]
    result = AHPHelper.calculate_weights(matrix, labels)
    assert "error" in result


def test_negative_values_in_pairwise_matrix_returns_error():
    matrix = np.array([[1, -3], [-1 / 3, 1]])
    labels = ["A", "B"]
    result = AHPHelper.calculate_weights(matrix, labels)
    assert "error" in result


class TestAHPHelper:
    def test_consistent_matrix(self):
        matrix = np.array(
            [
                [1, 3, 5],
                [1 / 3, 1, 3],
                [1 / 5, 1 / 3, 1],
            ]
        )
        labels = ["Cost", "Quality", "Speed"]
        result = AHPHelper.calculate_weights(matrix, labels)
        assert result["is_consistent"]
        assert result["consistency_ratio"] <= 0.1
        assert len(result["weights"]) == 3

    def test_inconsistent_matrix(self):
        matrix = np.array(
            [
                [1, 3, 1 / 5],
                [1 / 3, 1, 3],
                [5, 1 / 3, 1],
            ]
        )
        labels = ["Cost", "Quality", "Speed"]
        result = AHPHelper.calculate_weights(matrix, labels)
        assert not result["is_consistent"]
        assert result["correction_advice"] is not None

    def test_single_factor(self):
        matrix = np.array([[1]])
        labels = ["Only"]
        result = AHPHelper.calculate_weights(matrix, labels)
        assert result["weights"]["Only"] == 1.0
        assert result["consistency_ratio"] == 0.0
        assert result["is_consistent"]

    def test_two_factors(self):
        matrix = np.array(
            [
                [1, 3],
                [1 / 3, 1],
            ]
        )
        labels = ["A", "B"]
        result = AHPHelper.calculate_weights(matrix, labels)
        assert result["is_consistent"]
        assert result["weights"]["A"] > result["weights"]["B"]

    def test_weights_sum_to_one(self):
        matrix = np.array(
            [
                [1, 1 / 5, 3],
                [5, 1, 7],
                [1 / 3, 1 / 7, 1],
            ]
        )
        labels = ["A", "B", "C"]
        result = AHPHelper.calculate_weights(matrix, labels)
        total = sum(result["weights"].values())
        assert abs(total - 1.0) < 0.01

    def test_error_on_mismatched_dimensions(self):
        matrix = np.array([[1, 2], [3, 4]])
        labels = ["A"]
        result = AHPHelper.calculate_weights(matrix, labels)
        assert "error" in result

    def test_random_index_exists(self):
        assert AHPHelper.RI_TABLE[1] == 0
        assert AHPHelper.RI_TABLE[3] == 0.58
        assert AHPHelper.RI_TABLE[9] == 1.45

    def test_non_reciprocal_matrix_returns_error(self):
        matrix = np.array(
            [
                [1, 3, 5],
                [1 / 4, 1, 3],
                [1 / 5, 1 / 3, 1],
            ]
        )
        labels = ["A", "B", "C"]
        result = AHPHelper.calculate_weights(matrix, labels)
        assert "error" in result

    def test_consistent_with_equal_weights(self):
        matrix = np.array(
            [
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
            ]
        )
        labels = ["A", "B", "C"]
        result = AHPHelper.calculate_weights(matrix, labels)
        assert result["is_consistent"]
        assert abs(result["weights"]["A"] - result["weights"]["B"]) < 0.01
        assert abs(result["weights"]["A"] - result["weights"]["C"]) < 0.01
