import os
from dotenv import load_dotenv

load_dotenv(override=True)


def get_openai_base_url() -> str:
    return os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com")


def get_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN no configurado en .env")
    return token


def get_langsmith_config() -> dict:
    return {
        "api_key": os.getenv("LANGCHAIN_API_KEY"),
        "project": os.getenv("LANGCHAIN_PROJECT", "ingenieria_soluciones_con_ia"),
        "endpoint": os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
        "tracing": os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
    }


def get_model_config() -> dict:
    return {
        "model": os.getenv("MODEL_NAME", "gpt-4o"),
        "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.4")),
        "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "800")),
    }
