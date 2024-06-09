import os
from openai import OpenAI

def generate_summary():
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
    )

    engine = os.getenv("OPENAI_MODEL")
    prompt = "最近のコミットに基づいてプルリクエストの概要を生成してください。"

    response = client.chat.completions.create(
        model=engine,
        messages=[
            {"role": "system", "content": "You are a helpful assistant specializing in generating pull request summaries based on recent commits."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.5,
    )

    summary = response.choices[0].message.content.strip()
    with open(os.environ['GITHUB_ENV'], 'a') as env_file:
        env_file.write(f"SUMMARY={summary}\n")

if __name__ == "__main__":
    try:
        generate_summary()
    except Exception as e:
        print(e)
        exit(1)
