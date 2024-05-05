import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import os
from yig.util.data import write_user_data, read_user_data
import yig.config

AWS_S3_BUCKET_NAME = yig.config.AWS_S3_BUCKET_NAME


@pytest.fixture
def aws_credentials():
    """AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def mock_s3_client():
    mock_client = MagicMock()
    mock_client.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(return_value=b'{"test": "Test Value"}'))
    }
    # put_object の戻り値を設定
    mock_client.put_object.return_value = {
        "ResponseMetadata": {
            "HTTPStatusCode": 200
        }
    }
    return mock_client


@patch("yig.util.data.boto3.client")
def test_write_user_data_success(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client

    guild_id = "guild123"
    user_id = "user456"
    filename = "test.txt"
    content = {'test': 'Test Value'}

    success = write_user_data(guild_id, user_id, filename, content)
    assert success is True


@patch("yig.util.data.boto3.client")
def test_write_user_data_failure(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client
    mock_s3_client.put_object.side_effect = Exception("S3 Error")

    guild_id = "guild123"
    user_id = "user456"
    filename = "test.txt"
    content = "Hello, world!"

    with pytest.raises(Exception) as exc_info:
        write_user_data(guild_id, user_id, filename, content)

    assert str(exc_info.value) == "S3 Error"


@patch("yig.util.data.boto3.client")
def test_read_user_data_success(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client

    guild_id = "guild123"
    user_id = "user456"
    filename = "test.txt"

    result = read_user_data(guild_id, user_id, filename)
    assert result == {'test': 'Test Value'}


@patch("yig.util.data.boto3.client")
def test_read_user_data_failure(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client
    mock_s3_client.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey"}}, "GetObject"
    )

    try:
        read_user_data("guild123", "user456", "test.txt")
    except ClientError as e:
        assert e.response["Error"]["Code"] == "NoSuchKey"

    mock_s3_client.get_object.assert_called_once()
