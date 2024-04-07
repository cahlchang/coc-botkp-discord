import pytest
from yig.plugins.roll import analysis_roll_and_calculation

@pytest.mark.parametrize("input_value,expected", [
    ("STR", ("STR", "+", 0)),  # オペラントなし
    ("STR+20", ("STR", "+", 20)),  # 足し算
    ("CON-10", ("CON", "-", 10)),  # 引き算
    ("INT*2", ("INT", "*", 2)),    # 掛け算
    ("POW/2", ("POW", "/", 2)),    # 割り算
    ("SIZ+0", ("SIZ", "+", 0)),    # オペランドが0
    ("APP-0", ("APP", "-", 0)),    # オペランドがマイナス0
    ("DEX*5+10", ("DEX*5", "+", 10)),  # 式の途中にオペランド（正しくは解析できない例）
    ("STR*3-2", ("STR*3", "-", 2)),    # 複数のオペレーター（正しくは解析できない例）
])
def test_analysis_roll_and_calculation(input_value, expected):
    assert analysis_roll_and_calculation(input_value) == expected
