# deploy lambda
lambroll deploy --function=function.json --src="."

# pip install command
pip3 install -r requirements.txt -t . --platform manylinux2014_x86_64 --implementation cp --python 3.9 --only-binary=:all: --upgrade

# log
aws logs tail /aws/lambda/cocbotkp-discord-docker --follow

# test

python -m pytest


#TODO
とりあえず全コマンドが動くように

実装済み
跳躍（roll_skill）
sanc
sanc 1d4/1d20
キック-20
組み付き*2
こぶし+20
APP*5
con
信用/2


後でよくする
init
status
add_image -> originalも残す

変える
'u HP+5' -> changeにしたけどupdateに戻す

実装中

テスト済み
handler
1D100

未実装
'result'
'reload'
'start' -> 実装が大きく変わる
'join UE6P69HFH',

'update SAN+10',
'join UE6P69HFH',
'hide 心理学',
'hide 心理学+20',
'hide 心理学-20',
'hide 心理学*2',
'hide 心理学/2',
'hide やっほー',
'result',
'order DEX',
'select',
'leave UE6P69HFH',
'kp order DEX',
'help',
'openhelp',
'history <https://charasheet.vampire-blood.net/3395789>',
'init <https://charasheet.vampire-blood.net/3668130>', # 7版のテスト
'威圧',
'ヒプノーシス',


不要？
loadimg

'list chara 図書館>80',
'listchara ラテン語',
