import requests
import json
import boto3
import imghdr
import os
import copy
from botocore.exceptions import ClientError
from PIL import Image
from typing import List, Dict, Optional, Tuple

import yig.config


def write_user_data(guild_id: str, user_id: str, filename: str, content: str) -> bool:
    """
    Write user data to S3 bucket.

    Parameters
    ----------
    guild_id : str
        ID of the guild.
    user_id : str
        ID of the user.
    filename : str
        Name of the file to write the content.
    content : str
        Content to write to the file.

    Returns
    -------
    bool
        Returns True if the write operation was successful, False otherwise.
    """
    s3 = boto3.client("s3")
    user_dir = f"{guild_id}/{user_id}"
    obj_key = f"{user_dir}/{filename}"

    try:
        response = s3.put_object(
            Body=content,
            Bucket=yig.config.AWS_S3_BUCKET_NAME,
            Key=obj_key,
            ContentType="text/plain",
        )
    except Exception as e:
        print(f"Failed to write user data: {e}")
        return False

    return True


def read_user_data(guild_id: str, user_id: str, filename: str) -> dict:
    """
    Read user data from the specified file in the given user's directory in the S3 bucket.

    Parameters
    ----------
    guild_id : str
        ID of the guild where the user is located.
    user_id : str
        ID of the user who owns the data to be read.
    filename : str
        Name of the file containing the user data to be read.

    Returns
    -------
    dict
        The contents of the dictionary read from the file, or None if the file could not be read.
    """
    s3 = boto3.client("s3")
    key = f"{guild_id}/{user_id}/{filename}"

    try:
        response = s3.get_object(Bucket=yig.config.AWS_S3_BUCKET_NAME, Key=key)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print(f"Failed to read user data: {e}")
        raise e
    except Exception as e:
        print(f"Failed to read user data: {e}")
        raise e

    return json.loads(response["Body"].read().decode("utf-8"))


def get_state_data(guild_id: str, user_id: str) -> dict:
    """
    Returns the state data for a given user from a specified file path.

    Parameters
    ----------
    guild_id : str
        The ID of the guild.
    user_id : str
        The ID of the user.

    Returns
    -------
    dict
        A dictionary object containing the user's state data, or an empty dictionary if no data was found.
    """
    return read_user_data(guild_id, user_id, yig.config.STATE_FILE_PATH)

def get_user_param(guild_id: str, user_id: str, pc_id: str = "") -> dict:
    """
    Get the parameter for the specified user.

    Parameters
    ----------
    guild_id : str
        The ID of the guild to which the user belongs.
    user_id : str
        The ID of the user whose parameters to get.
    pc_id : str, optional
        The ID of the character sheet whose parameters to get. If not
        specified, pc_id is obtained from state_data.

    Returns
    -------
    dict
        The user's parameters.

    """
    if pc_id is None:
        state_data = get_state_data(guild_id, user_id)
        if not state_data:
            return {}
        pc_id = state_data.get("pc_id")

    return read_user_data(guild_id, user_id, f"{pc_id}.json")


def get_now_status(
    status_name: str,
    user_param: Dict,
    state_data: Dict,
    status_name_alias: Optional[str] = None,
) -> int:
    """
    Calculates and returns the current status.

    Parameters
    ----------
    status_name : str
        The name of the status.
    user_param : Dict[str, Any]
        User parameters.
    state_data : Dict[str, Any]
        State data.
    status_name_alias : Optional[str], default None
        The alias name of the status. If specified, the value of the alias name is obtained.

    Returns
    -------
    now_status : int
        The value of the current status.

    Notes
    -----
    This function calculates the current status based on the state data and returns its value.

    Examples
    --------
    >>> user_param = {'HP': 15, 'MP': 12}
    >>> state_data = {'HP': -2}
    >>> get_now_status('HP', user_param, state_data)
    13
    """
    now_status = (
        user_param[status_name]
        if status_name_alias is None
        else user_param[status_name_alias]
    )

    if status_name in state_data:
        now_status += int(state_data[status_name])
    return now_status


def get_basic_status(
    user_param: Dict[str, int], state_data: Dict[str, int]
) -> Tuple[int, int, int, int, int, int, int]:
    """
    Get basic status values of a user character.

    Parameters
    ----------
    user_param : dict
        Dictionary containing the user's character parameters, such as HP, MP, SAN, and DB.
    state_data : dict
        Dictionary containing the user's current state data, such as HP changes, MP changes, and SAN changes.

    Returns
    -------
    Tuple[int, int, int, int, int, int, int]
        A tuple containing the current HP, max HP, current MP, max MP, current SAN, max SAN, and DB values.
    """
    return (
        get_now_status("HP", user_param, state_data),
        user_param["HP"],
        get_now_status("MP", user_param, state_data),
        user_param["MP"],
        get_now_status("SAN", user_param, state_data, "現在SAN"),
        user_param["現在SAN"],
        user_param["DB"],
    )


def build_user_panel(
    title,
    field_name,
    field_value,
    color,
    name,
    now_hp,
    max_hp,
    now_mp,
    max_mp,
    now_san,
    max_san,
    db,
    image_url,
):
    return {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "title": title,
                "fields": [{"name": field_name, "value": field_value}],
                "description": "",
                "color": color,
                "thumbnail": {"url": image_url},
                "footer": {
                    "text": f"{name}    HP: {now_hp}/{max_hp} MP: {now_mp}/{max_mp} SAN: {now_san}/{max_san} DB: {db}",
                },
            }
        ],
    }


def write_session_data(team_id, path, content):
    try:
        s3_client = boto3.resource('s3')
        bucket = s3_client.Bucket(yig.config.AWS_S3_BUCKET_NAME)
        obj = bucket.Object(f"{team_id}/{path}")
        response = obj.put(
            Body=content,
            ContentEncoding='utf-8',
            ContentType='text/plane'
        )
    except ClientError as e:
        print(e)


def read_session_data(team_id, path):
    try:
        s3_client = boto3.resource('s3')
        bucket = s3_client.Bucket(yig.config.AWS_S3_BUCKET_NAME)
        obj = bucket.Object(f"{team_id}/{path}")
        response = obj.get()
        return response['Body'].read()
    except ClientError as e:
        print(e)
        return None


def get_basic_param():
    pass

def build_detail_user_panel(
    title,
    field_name,
    field_value,
    color,
    name,
    now_hp,
    max_hp,
    now_mp,
    max_mp,
    now_san,
    max_san,
    db,
    image_url,
):
    return {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "title": title,
                "description": "test",
                "color": color,
                "thumbnail": {"url": image_url},
                "fields": [{"name": field_name, "value": field_value}],
                "image": {"url": image_url},
                "footer": {
                    "text": "{name}    HP: {now_hp}/{max_hp} MP: {now_mp}/{max_mp} SAN: {now_san}/{max_san} DB: {db}",
                },
            },
            {
                "type": "rich",
                "title": title,
                "description": "test",
                "color": color,
                "thumbnail": {"url": image_url},
                "fields": [{"name": field_name, "value": field_value}],
                "image": {"url": image_url},
                "footer": {
                    "text": "{name}    HP: {now_hp}/{max_hp} MP: {now_mp}/{max_mp} SAN: {now_san}/{max_san} DB: {db}",
                },
            },
        ],
    }

