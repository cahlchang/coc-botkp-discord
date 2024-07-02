import pytest
import re
from yig.plugins.user import parse_string

def test_parse_string():
    # 正常なケース
    assert parse_string('hp+3') == ('hp', '+', 3)
    assert parse_string('mp-10') == ('mp', '-', 10)
    assert parse_string('strength+50') == ('strength', '+', 50)
    assert parse_string('agility-25') == ('agility', '-', 25)
    assert parse_string('dexterity+7') == ('dexterity', '+', 7)

    # 異常なケース
    with pytest.raises(ValueError, match=re.escape("Invalid input format: 'invalid+value'. Expected format is 'letters+digits' or 'letters-digits'")):
        parse_string('invalid+value')
    with pytest.raises(ValueError, match=re.escape("Invalid input format: 'hp++3'. Expected format is 'letters+digits' or 'letters-digits'")):
        parse_string('hp++3')
    with pytest.raises(ValueError, match=re.escape("Invalid input format: '123+abc'. Expected format is 'letters+digits' or 'letters-digits'")):
        parse_string('123+abc')
