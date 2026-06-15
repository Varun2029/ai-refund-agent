"""
Application configuration — loads from environment variables with sensible defaults.
Switch LLM providers via the LLM_PROVIDER env var ("gemini" | "groq").
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration singleton."""

    # --- Database ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./refund_platform.db",
    )

    # --- JWT ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # --- LLM Provider ---
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")  # "gemini" | "groq"

    # --- Google Gemini ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # --- Groq ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # --- CORS ---
    CORS_ORIGINS: list[str] = json.loads(
        os.getenv("CORS_ORIGINS", '["*"]')
    )

    # --- SMTP (Mailtrap) ---
    SMTP_HOST: str = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "2525"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "support@refundai.com")


settings = Settings()
