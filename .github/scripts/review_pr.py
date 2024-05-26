import os
import json
import openai
import requests

# GitHub環境変数
GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
GITHUB_EVENT_PATH = os.getenv('GITHUB_EVENT_PATH')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# OpenAI APIキー
openai.api_key = os.getenv('OPENAI_API_KEY')

# モデルとプロンプトの設定
openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
review_prompt = os.getenv('REVIEW_PROMPT', 'Please review the following code changes:')

# PRの情報を取得
with open(GITHUB_EVENT_PATH, 'r') as f:
    event = json.load(f)
pr_number = event['pull_request']['number']

# PRの変更内容を取得
url = f'https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{pr_number}/files'
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
response = requests.get(url, headers=headers)
files = response.json()

# 変更内容をテキストにまとめる
diff_text = ""
for file in files:
    filename = file['filename']
    patch = file.get('patch', '')
    diff_text += f'File: {filename}\n{patch}\n\n'

# ChatGPTにレビューコメントを依頼
response = openai.ChatCompletion.create(
    model=openai_model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"{review_prompt}\n\n{diff_text}"}
    ],
    max_tokens=500
)

review_comment = response['choices'][0]['message']['content']

# GitHubにレビューコメントを投稿
review_url = f'https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{pr_number}/reviews'
review_data = {
    "body": review_comment,
    "event": "COMMENT"
}
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}
requests.post(review_url, headers=headers, json=review_data)
