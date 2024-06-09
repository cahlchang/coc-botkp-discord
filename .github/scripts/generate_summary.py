import os
from openai import OpenAI
import subprocess

def get_all_commit_details():
    try:
        commit_messages = subprocess.run(
            ["git", "log", "--pretty=format:%s"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ).stdout.strip()

        commit_diff = subprocess.run(
            ["git", "diff", "origin/main...HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ).stdout

        return commit_messages, commit_diff
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit details: {e.stderr}")
        return "", ""

def generate_summary():
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
    )

    engine = os.getenv("OPENAI_MODEL")
    prompt = "最近のコミットに基づいてプルリクエストの概要を生成してください。"

    commit_messages, commit_diff = get_all_commit_details()
    prompt = f"以下のコミットメッセージと変更内容に基づいてプルリクエストの概要を生成してください。またGitHubマークダウン記法でわかりやすくしてください。\n\nコミットメッセージ:\n{commit_messages}\n\n変更内容:\n{commit_diff}"


    response = client.chat.completions.create(
        model=engine,
        messages=[
            {"role": "system", "content": "You are a helpful assistant specializing in generating pull request summaries based on recent commits."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5,
    )

    summary = response.choices[0].message.content.strip()
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output_file:
        output_file.write(f"summary={summary}\n")
#    summary_safe = summary.replace('\n', '%0A').replace('\r', '%0D')
    # with open(os.environ['GITHUB_ENV'], 'a') as env_file:
    #     env_file.write(f'SUMMARY="{summary}"\n')

if __name__ == "__main__":
    try:
        generate_summary()
    except Exception as e:
        print(e)
        exit(1)
