import re
import random
import math
import json


from yig.bot import listener
from yig.bot import Bot
from yig.util.data import get_user_param, get_basic_status, read_user_data, add_dice_log, get_dice_logs, build_user_panel

# set_state_data,
from yig.util.view import get_pc_image_url
import yig.config


@listener("cc")
def roll_skill(bot: Bot):
    """
    Perform a roll of skills and return the result data.

    Parameters:
    -----------
    bot : Bot
        Discord bot instance.

    Returns:
    --------
    Dict
        Responce data.
    """

    # Get user's status information
    state_data = read_user_data(
        bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, filename=yig.config.STATE_FILE_PATH
    )

    user_param = get_user_param(
        bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, pc_id=state_data["pc_id"]
    )

    # Analyze parameters from bot's value
    roll, operant, num_arg = analysis_roll_and_calculation(
        value=bot.action_data["options"][0]["value"]
    )

    # Convert the skill name to the corresponding skill name if there is an alias for the skill name
    alias_roll = {"こぶし": "こぶし（パンチ）"}
    if roll in alias_roll.keys():
        roll = alias_roll[roll]

    # If the user does not have the corresponding skill in their list of skills
    if roll.upper() not in user_param:
        return f"{roll} その技能は覚えていません", "gray"

    # Get the detailed information of the skill
    data = user_param[roll.upper()]

    # Roll the dice
    num_rand = sum(roll_dice(1, 100))

    if roll.upper() in yig.config.LST_USER_STATUS_NAME:
        num = int(data)
    else:
        num = int(data[-1])

    # Calculate the target value
    num_targ = calculation(number_x=num, operant=operant, number_y=num_arg)

    # Perform success/failure judgement
    if user_param["game"] == "coc":
        result, color = judge_1d100_with_6_ver(target=num_targ, dice=num_rand)
    else:
        result, color = judge_1d100_with_7_ver(target=num_targ, dice=num_rand)

    add_dice_log(
        bot=bot,
        guild_id=bot.guild_id,
        channel_id=bot.channel_id,
        user_id=bot.user_id,
        pc_id=state_data["pc_id"],
        roll=roll.upper(),
        num_targ=f"{num}{operant}{num_arg}",
        num_rand=num_rand,
        result=result
    )

    # Get status information.
    now_hp, max_hp, now_mp, max_mp, now_san, max_san, db = get_basic_status(
        user_param, state_data
    )
    image_url = get_pc_image_url(
        bot.guild_id, bot.user_id, state_data["pc_id"], state_data["ts"]
    )

    # Create a data to be returned
    return_object = {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "title": f"{result}",
                "fields": [
                    {
                        "name": f"{roll} {num_rand}/{num_targ} ({num}{operant}{num_arg})",
                        "value": "",
                    }
                ],
                "description": "",
                "color": color,
                "thumbnail": {"url": image_url},
                "footer": {
                    "text": "%s    HP: %s/%s MP: %s/%s SAN: %s/%s DB: %s"
                    % (
                        user_param["name"],
                        now_hp,
                        max_hp,
                        now_mp,
                        max_mp,
                        now_san,
                        max_san,
                        db,
                    ),
                },
            }
        ],
    }
    return return_object


@listener("dice")
def roll_dice(bot: Bot):
    """
    Perform a roll of dice and return the result data.

    Parameters:
    -----------
    bot : Bot
        Discord bot instance.

    Returns:
    --------
    Dict
        Responce data.
    """
    # Get user's status information
    now_hp, max_hp, now_mp, max_mp, now_san, max_san, db = 0, 0, 0, 0, 0, 0, 0
    image_url = "https://d13xcuicr0q687.cloudfront.net/public/noimage.jpg"
    user_name = "Unknown"
    try:
        state_data = read_user_data(
            bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, filename=yig.config.STATE_FILE_PATH
        )

        user_param = get_user_param(
            bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, pc_id=state_data["pc_id"]
        )

        now_hp, max_hp, now_mp, max_mp, now_san, max_san, db = get_basic_status(
            user_param, state_data
        )

        image_url = get_pc_image_url(
            bot.guild_id, bot.user_id, state_data["pc_id"], state_data["ts"]
        )
        user_name = user_param["name"]
    except Exception as _:
        pass

    str_message, str_detail, sum_result = create_post_message_rolls_result(
        bot.action_data["options"][0]["value"]
    )
    msg = f"*{sum_result}* 【ROLLED】\n {str_detail}"


    return {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "title": "ダイスロール",
                "fields": [{"name": str(sum_result), "value": msg}],
                "description": str_message,
                "color": yig.config.COLOR_INFO,
                "thumbnail": {"url": image_url},
                "footer": {
                    "text": "%s    HP: %s/%s MP: %s/%s SAN: %s/%s DB: %s"
                    % (
                        user_name,
                        now_hp,
                        max_hp,
                        now_mp,
                        max_mp,
                        now_san,
                        max_san,
                        db,
                    ),
                },
            }
        ],
    }


@listener("sanc")
def sanity_check(bot: Bot):
    state_data = read_user_data(
        bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, filename=yig.config.STATE_FILE_PATH
    )

    user_param = get_user_param(
        bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, pc_id=state_data["pc_id"]
    )
    c_san = int(user_param["現在SAN"])
    if "SAN" in state_data:
        d_san = int(state_data["SAN"])
    else:
        d_san = 0
    sum_san = c_san + d_san
    message, color, reduce_message = get_sanc_result(bot.action_data, sum_san)
    now_hp, max_hp, now_mp, max_mp, now_san, max_san, db = get_basic_status(
        user_param, state_data
    )
    image_url = get_pc_image_url(
        bot.guild_id, bot.user_id, state_data["pc_id"], state_data["ts"]
    )
    return_obj = {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "title": "SANチェック",
                "fields": [{"name": message, "value": reduce_message}],
                "description": "",
                "color": color,
                "thumbnail": {"url": image_url},
                "footer": {
                    "text": "%s    HP: %s/%s MP: %s/%s SAN: %s/%s DB: %s"
                    % (
                        user_param["name"],
                        now_hp,
                        max_hp,
                        now_mp,
                        max_mp,
                        now_san,
                        max_san,
                        db,
                    ),
                },
            }
        ],
    }
    return return_obj


@listener("result")
def show_result(bot) -> list[dict]:
    user_data = read_user_data(
        bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, filename=yig.config.STATE_FILE_PATH
    )

    user_param = get_user_param(
        bot=bot, guild_id=bot.guild_id, user_id=bot.user_id, pc_id=user_data["pc_id"]
    )
    now_hp, max_hp, now_mp, max_mp, now_san, max_san, db = get_basic_status(
        user_param, user_data
    )

    result_items = get_dice_logs(bot=bot,
                                guild_id=bot.guild_id,
                                channel_id=bot.channel_id,
                                user_id=bot.user_id,
                                pc_id=user_data["pc_id"])
    image_url = get_pc_image_url(bot.guild_id, bot.user_id, user_data['pc_id'], user_data['ts'])
    result_message = ""
    # cnt_msg = 60

    for item in result_items:
        symbols = {"クリティカル": "🌟",
                    "イクストリーム": "✨️",
                    "ハード": "🟡",
                    "成功": "🟢",
                    "失敗": "❌️",
                    "ファンブル": "☠️"}

        result_message += "%s *%s* *%s* *%s* (%s)\n" % (symbols[item["Result"]], item["Result"], item["RollResult"], item["NumRand"], item["NumTarg"])

    if result_message == "":
        result_message = "No Result"

    return build_user_panel(
        "RESULT",
        "",
        result_message,
        yig.config.COLOR_INFO,
        "name",
        now_hp,
        max_hp,
        now_mp,
        max_mp,
        now_san,
        max_san,
        db,
        image_url,
    )


def analysis_roll_and_calculation(value: str) -> tuple[str, str, int]:
    """
    Analyze a roll value and extract its components for calculation.

    Parameters
    ----------
    value : str
        A string representing a roll, potentially with a supplementary formula.

    Returns
    -------
    tuple[str, str, int, str]
        A tuple containing the roll, the operator, the operand, and the difficulty rating.

    Notes
    -----
    The expected format for the `value` string is a roll expression, optionally followed by a `+`, `-`, `*`, or `/`
    operator and an integer operand. The roll expression can also have a difficulty rating at the end, which is a space
    followed by the letter `N`, `H`, or `E` (normal, hard, or extreme).

    Examples
    --------
    >>> analysis_roll_and_calculation("DEX*5)
    ("DEX", "+", 30)

    """
    proc = r"^(.*)(\+|\-|\*|\/)(\d+)$"
    result_parse = re.match(proc, value)
    operant = "+"
    number = 0

    if result_parse:
        roll, operant, number = result_parse.groups()
        number = int(number)
    else:
        roll = value

    return roll, operant, number


def calculation(number_x: int, operant: str, number_y: int) -> int:
    """
    Perform a calculation from two values.

    Parameters
    ----------
    number_x : int
        The first operand.     (ex. 30)
    operant : str
        The operator to apply. (ex. +)
    number_y : int
        The second operand.    (ex. 20)

    Returns
    -------
    int
        The result of the calculation.
    """
    op_dict = {
        "+": lambda x, y: x + y,
        "-": lambda x, y: x - y,
        "*": lambda x, y: x * y,
        "/": lambda x, y: math.floor(x / y),
    }

    return op_dict[operant](number_x, number_y)


def eval_roll_or_value(text: str) -> list[int]:
    try:
        return [int(text)]
    except ValueError:
        dice_matcher = re.fullmatch(r"(\d+)D(\d+)", text, re.IGNORECASE)
        if dice_matcher is None:
            return [0]
        dice_count, dice_type = map(int, dice_matcher.groups())
        return (
            roll_dice(dice_count, dice_type)
            if dice_count > 0 and dice_type > 0
            else [0]
        )


def create_post_message_rolls_result(key: str) -> tuple[str, str, int]:
    # ダイスロールと数値、演算子を抽出する正規表現パターン
    pattern = re.compile(r"(\d+[dD]\d+|\d+)|([-+])")
    items = pattern.findall(key)

    str_message = ""
    sum_result = 0
    str_detail = ""
    current_operation = "+"

    for item in items:
        match, operation = item
        if operation:
            # 演算子が見つかった場合、現在の演算子を更新
            current_operation = operation
            continue

        # ダイスロールまたは数値の処理
        if "d" in match.lower():
            roll_results = eval_roll_or_value(match)
            dice_sum = sum(roll_results)
            str_detail += f"{match}".ljust(8) + ", ".join(map(str, roll_results))
        else:
            # 数値の場合、リストとして処理して統一的に扱う
            dice_sum = int(match)
            roll_results = [dice_sum]
            str_detail += match.ljust(8)

        # 加算または減算を実行
        sum_result = (
            sum_result + dice_sum if current_operation == "+" else sum_result - dice_sum
        )
        str_message += f"{current_operation}{match}" if str_message else match
        str_detail += f" [{'plus' if current_operation == '+' else 'minus'}]\n"

    return str_message.strip(), str_detail.strip(), sum_result


def judge_1d100_with_6_ver(target: int, dice: int) -> tuple[str, str]:
    """
    Judge 1d100 dice result, and return text and color for value.
    Result is critical, success, failure or fumble.

    Parameters
    ----------
    target :int
        The target value, usually a skill value.
    dice :int
        The result of the 1d100 dice roll.

    Returns:
    -------
    Tuple[str, str]:
        A tuple containing the value and color for the value.
    """
    if dice <= target:
        if dice <= 5:
            return "クリティカル", yig.config.COLOR_CRITICAL
        return "成功", yig.config.COLOR_SUCCESS

    if dice >= 96:
        return "ファンブル", yig.config.COLOR_FUMBLE
    return "失敗", yig.config.COLOR_FAILURE


def judge_1d100_with_7_ver(target: int, dice: int) -> tuple[str, str]:
    """
    Judge the 1d100 dice result and return a tuple of a value and the color for value.

    Parameters
    ----------
    target : int
        The target value to compare against the dice value.
    dice : int
        The dice value to compare against the target value.

    Returns
    -------
    tuple of (str, str, str)
        A tuple of a value and the color for value.

    Notes
    -----
    The result is critical, success, failure, or fumble.

    If the dice is greater than the target, the result is failure or fumble.
    If the dice is greater than half the target and the level of difficulty is hard, the result is failure.
    If the dice is greater than one-fifth the target and the level of difficulty is extreme, the result is failure.
    If the dice is less than or equal to one-fifth the target, the result is extreme.
    If the dice is less than or equal to half the target, the result is hard.
    Otherwise, the result is success.
    """
    if dice > target:
        if target >= 50 and dice == 100 or dice >= 96:
            return "ファンブル", yig.config.COLOR_FUMBLE
        return "失敗", yig.config.COLOR_FAILURE

    if dice <= math.floor(target / 5):
        return "イクストリーム", yig.config.COLOR_CRITICAL
    elif dice <= math.floor(target / 2):
        return "ハード", yig.config.COLOR_SUCCESS

    return "成功", yig.config.COLOR_NORMAL_SUCCESS


def get_sanc_result(data: dict, pc_san: int) -> tuple[str, str, str]:
    """
    Check SAN and return result message and color.
    Arguments:
        cmd {str} -- command text
        pc_san {int} -- PC's SAN value
    Returns:
        str -- report message
        str -- color that indicates success or failure
        str -- value SAN Damage
    """
    dice_result = sum(roll_dice(1, 100))
    is_success = pc_san >= dice_result
    if is_success:
        color = yig.config.COLOR_SUCCESS
        result_word = "成功"
    else:
        color = yig.config.COLOR_FAILURE
        result_word = "失敗"

    message = f"{result_word}  {dice_result}/{pc_san}"
    reduce_message = ""
    if "options" in data:
        match_result = split_alternative_roll_or_value(data["options"][0]["value"])
        if match_result:
            san_roll = match_result[0] if is_success else match_result[1]
            san_damage = sum(roll_or_parse_dice(san_roll))
            reduce_message = f"減少値 {san_damage}"
    return message, color, reduce_message


def split_alternative_roll_or_value(cmd) -> tuple[str, str]:
    """
    Split text 2 roll or value.
    Alternative roll is like following.
    - 0/1
    - 1/1D3
    - 1D20/1D100
    Arguments:
        cmd {str}
    Returns:
        tuple of 2 str or None
    """
    element_matcher = r"(\d+D?\d*)"
    result = re.fullmatch(f"{element_matcher}/{element_matcher}", cmd.upper())
    if result is None or len(result.groups()) != 2:
        return None, None
    return result.groups()


def roll_or_parse_dice(text: str) -> list[int]:
    """
    Roll one or more dice or parse a single number from a text string.

    Parameters
    ----------
    text : str
        The input string to parse or dice to roll. Should be a single integer
        or a string of the form "NdM" where N is the number of dice to roll and
        M is the number of sides on each die.

    Returns
    -------
    List[int]
        A list of integers representing the results of rolling the specified
        number and type of dice. If the input is a single integer, the result
        will be a list containing that integer.

    Raises
    ------
    ValueError
        If the input string is not in the correct format or contains invalid
        values for the number of dice or sides.

    Examples
    --------
    >>> roll_or_parse_dice("3")
    [3]

    >>> roll_or_parse_dice("2D6")
    [5, 1]
    """
    if text.isdigit():
        return [int(text)]

    dice_matcher = re.fullmatch(r"(\d+)D(\d+)", text)
    if dice_matcher is None:
        raise ValueError(f"Invalid input: {text}")

    match_numbers = dice_matcher.groups()
    dice_count = int(match_numbers[0])
    dice_type = int(match_numbers[1])
    if dice_count < 0 or dice_type < 0:
        raise ValueError("Number of dice and sides must be positive integers.")

    return roll_dice(dice_count, dice_type)


def roll_dice(dice_count: int, dice_type: int) -> list[int]:
    """
    Get multiple and various dice roll result.
    ex) `roll_dice(2, 6)` means 2D6 and return each result like [2, 5].
    Arguments:
        dice_count {int} -- [description]
        dice_type {int} -- [description]
    Returns:
        List[int] -- All dice results
    """
    return [random.randint(1, dice_type) for _ in range(dice_count)]
