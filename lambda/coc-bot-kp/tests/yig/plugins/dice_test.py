import pytest
from yig.plugins.roll import create_post_message_rolls_result


@pytest.fixture
def mock_eval_roll_or_value(mocker):
    return mocker.patch("yig.plugins.roll.eval_roll_or_value")


def test_simple_roll(mock_eval_roll_or_value):
    mock_eval_roll_or_value.return_value = [3, 4]

    expected_message = "2D6"
    expected_detail = "2D6     3, 4 [plus]"
    expected_sum = 7

    message, detail, total = create_post_message_rolls_result("2D6")

    assert message == expected_message
    assert detail == expected_detail
    assert total == expected_sum


def test_complex_roll(mock_eval_roll_or_value):
    mock_eval_roll_or_value.side_effect = [[3, 4], [2, 2, 2]]

    expected_message = "2D6+3D4-5"
    expected_detail = "2D6     3, 4 [plus]\n3D4     2, 2, 2 [plus]\n5        [minus]"
    expected_sum = 8

    message, detail, total = create_post_message_rolls_result("2D6+3D4-5")

    assert message == expected_message
    assert detail == expected_detail
    assert total == expected_sum
