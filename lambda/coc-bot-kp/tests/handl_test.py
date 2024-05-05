"""
This code is testing a handler part of the Discord API using Lambda with pytest.
"""
from unittest.mock import patch

import json
import pytest
from handler import run

# mockを使った正常なリクエストのテスト
@pytest.mark.parametrize("request_body", [{"type": 0}, {"type": 1}, {"type": 2}])
def test_run_with_valid_request(request_body, mocker):
    mock_bot = mocker.Mock()
    mock_bot.verify.return_value = True
    mocker.patch("handler.Bot", return_value=mock_bot)

    event = {
        "body": json.dumps({"type": 1}),
        "headers": {
            "X-Signature-Ed25519": "valid_signature",
            "X-Signature-Timestamp": "valid_timestamp",
        },
    }
    lambda_context = {}
    response = run(event, lambda_context)

    # InteractionType.Pingのリクエストに対して200ステータスと適切なbodyが返されることを確認
    assert response == {"statusCode": 200, "body": json.dumps({"type": 1})}
    mock_bot.verify.assert_called_once_with(
        "valid_signature", "valid_timestamp", json.dumps({"type": 1})
    )


# リクエストボディがない場合のテスト
def test_run_without_body():
    event = {"headers": {}}
    lambda_context = {}
    response = run(event, lambda_context)

    # リクエストボディがない場合に適切なレスポンスが返されることを確認
    assert response == {"statusCode": 200, "body": json.dumps({"content": "not body"})}


# 署名の検証に失敗した場合のテスト
@patch("yig.bot.Bot")
def test_run_with_invalid_signature(mock_bot_class, mocker):
    mock_bot = mock_bot_class.return_value
    mock_bot.verify.return_value = False

    event = {
        "body": json.dumps({"type": 2}),
        "headers": {
            "X-Signature-Ed25519": "invalid_signature",
            "X-Signature-Timestamp": "invalid_timestamp",
        },
    }
    lambda_context = {}

    response = run(event, lambda_context)

    # 署名の検証に失敗した場合に401ステータスが返されることを確認
    assert response == {
        "cookies": [],
        "isBase64Encoded": False,
        "statusCode": 401,
        "headers": {},
        "body": "invalid request signature",
    }
