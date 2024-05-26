import os
import json
from openai import OpenAI
import requests

# GitHub environment variables
GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
GITHUB_EVENT_PATH = os.getenv('GITHUB_EVENT_PATH')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# OpenAI API key
client = OpenAI(
  api_key=os.getenv('OPENAI_API_KEY'),
)

# Model and prompt settings
openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
review_prompt = os.getenv('REVIEW_PROMPT', 'Please review the following code changes:')

# Retrieve PR information
with open(GITHUB_EVENT_PATH, 'r') as f:
    event = json.load(f)
pr_number = event['pull_request']['number']

# Retrieve PR changes
url = f'https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{pr_number}/files'
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
response = requests.get(url, headers=headers)
files = response.json()

# Summarize the changes
diff_text = ""
for file in files:
    filename = file['filename']
    patch = file.get('patch', '')
    diff_text += f'File: {filename}\n{patch}\n\n'

# Request review from ChatGPT
response = client.chat.completions.create(
    model=openai_model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"{review_prompt}\n\n{diff_text}"}
    ]
)

review_comment = response.choices[0].message.content

# Post review comment on GitHub
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
