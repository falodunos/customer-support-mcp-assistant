import os

from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TRACING_ENABLED: bool = os.getenv("OPENAI_TRACING_ENABLED", "true").lower() in {
        "true",
        "1",
        "yes",
    }