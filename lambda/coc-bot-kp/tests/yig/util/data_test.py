import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import os
from yig.util.data import write_user_data, read_user_data
import yig.config

# AWSのリソース名や設定値を定義
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
    mock_client.get_object.return_value = {'Body': MagicMock(read=MagicMock(return_value=b'Test Value'))}
    return mock_client


@patch("yig.util.data.boto3.client")
def test_write_user_data_success(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client

    guild_id = "guild123"
    user_id = "user456"
    filename = "test.txt"
    content = "Test Value"

    success = write_user_data(guild_id, user_id, filename, content)
    assert success is True

    mock_s3_client.put_object.assert_called_once_with(
        Body='Test Value',
        Bucket=AWS_S3_BUCKET_NAME,
        Key=f"{guild_id}/{user_id}/{filename}",
        ContentType='text/plain'
    )


@patch("yig.util.data.boto3.client") 
def test_write_user_data_failure(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client
    mock_s3_client.put_object.side_effect = Exception("S3 Error")

    success = write_user_data("guild123", "user456", "test.txt", "Hello, world!")
    assert not success

    mock_s3_client.put_object.assert_called_once()


@patch("yig.util.data.boto3.client")
def test_read_user_data_success(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client

    guild_id = 'guild123'
    user_id = 'user456'
    filename = 'test.txt'

    result = read_user_data(guild_id, user_id, filename)
    assert result == b'Test Value'


@patch("yig.util.data.boto3.client")
def test_read_user_data_failure(mock_boto_client, mock_s3_client):
    mock_boto_client.return_value = mock_s3_client

    error_response = {'Error': {'Code': 'NoSuchKey', 'Message': 'The specified key does not exist.'}}
    mock_s3_client.get_object.side_effect = ClientError(error_response, 'get_object')

    guild_id = 'guild123'
    user_id = 'user456'
    filename = 'nonexistent.txt'
    result = read_user_data(guild_id, user_id, filename)
    assert result is None