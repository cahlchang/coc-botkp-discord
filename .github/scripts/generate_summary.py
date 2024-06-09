import openai
import os

def generate_summary():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    engine = os.getenv("OPENAI_MODEL")
    
    prompt = "Generate a summary for a pull request based on the recent commits."
    
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    
    summary = response.choices[0].text.strip()
    
    # Output the summary to be used in the GitHub Actions workflow
    print(f"::set-output name=summary::{summary}")

if __name__ == "__main__":
    try:
        generate_summary()
    except Exception as e:
        print(e)
        exit(1)
