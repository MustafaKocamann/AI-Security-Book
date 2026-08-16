import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def groq_llm(temperature: float = 0.2, model: str = "llama-3.3-70b-versatile") -> ChatOpenAI:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    return ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        model=model,
        temperature=temperature,
    )

def gemini_llm(temperature: float = 0.3, model: str = "gemini-2.5-flash") -> ChatOpenAI:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    return ChatOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key,
        model=model,
        temperature=temperature,
    )
