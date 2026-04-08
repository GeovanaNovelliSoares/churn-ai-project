import os
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Initialize the Groq client using the API key from the environment.
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Use a lighter model to keep latency down and reduce rate limit issues.
MODEL = "llama-3.1-8b-instant"


def call_llm(prompt):
    """Call the LLM with retry logic and return the generated text."""
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"Attempt {attempt+1} failed. Waiting...")
            time.sleep(6)

    return "Error generating response"


def strategist_agent(context):
    """Generate a retention strategy based on the customer profile context."""
    prompt = f"""
    You are a customer retention analyst.

    Analyze the profile:
    {context}

    Return:
    - The likely reason for churn
    - A concise retention strategy
    """

    return call_llm(prompt)


def writer_agent(strategy):
    """Generate a short persuasive email based on the retention strategy."""
    prompt = f"""
    You are a retention specialist.

    Based on the strategy:
    {strategy}

    Generate a short, direct, persuasive email.
    """

    return call_llm(prompt)