"""
Unified LLM provider — switch between Gemini and Groq via ``LLM_PROVIDER`` env var.

Both providers expose the same :class:`LLMProvider` interface so downstream
agents and services are completely backend-agnostic.

Usage::

    from app.services.llm_provider import get_llm

    llm = get_llm()
    response = await llm.chat("Summarise the refund policy.")
    print(response.content)
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Standardised response
# ---------------------------------------------------------------------------


class LLMResponse:
    """Standardised wrapper around any LLM provider's raw response.

    Attributes:
        content:  The generated text.
        model:    Model identifier that produced the response.
        usage:    Optional dict with token-usage stats
                  (``prompt_tokens``, ``completion_tokens``).
    """

    def __init__(
        self,
        content: str,
        model: str,
        usage: Optional[dict[str, int]] = None,
    ) -> None:
        self.content = content
        self.model = model
        self.usage = usage or {}

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"LLMResponse(model={self.model!r}, "
            f"content={self.content[:80]!r}..., "
            f"usage={self.usage})"
        )

    # Convenience helpers -------------------------------------------------

    def json(self) -> dict:
        """Parse ``self.content`` as JSON.  Raises ``json.JSONDecodeError``."""
        return json.loads(self.content)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class LLMProvider:
    """Abstract base class every concrete LLM backend must implement."""

    async def chat(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send a single-turn chat request and return an :class:`LLMResponse`.

        Args:
            prompt:        The user message / main prompt.
            system_prompt: Optional system-level instruction.
            temperature:   Sampling temperature (0 – 2).
            json_mode:     If ``True``, instruct the model to return valid JSON.

        Returns:
            An :class:`LLMResponse` wrapping the generated text.
        """
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------


class GeminiProvider(LLMProvider):
    """Google Gemini provider using the ``google-genai`` SDK."""

    def __init__(self) -> None:
        try:
            from google import genai  # noqa: WPS433
        except ImportError as exc:
            raise ImportError(
                "google-genai is required for the Gemini provider. "
                "Install it with:  pip install google-genai"
            ) from exc

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Add it to your .env file or environment variables."
            )

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL
        # Pre-import types so it's ready at call time
        from google.genai import types as _types
        self._types = _types
        logger.info("GeminiProvider initialised (model=%s)", self.model)

    async def chat(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate content via Google Gemini.

        Uses the synchronous ``generate_content`` endpoint wrapped in the
        async interface for consistency.  For truly async I/O, swap to the
        ``aio`` client when the SDK supports it.
        """
        import asyncio
        config = self._types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            temperature=temperature,
        )
        if json_mode:
            config.response_mime_type = "application/json"

        try:
            # Run sync SDK call in a thread so we don't block the event loop
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=config,
            )
        except Exception:
            logger.exception("Gemini API call failed")
            raise

        content = response.text or ""
        return LLMResponse(content=content, model=self.model)


# ---------------------------------------------------------------------------
# Groq
# ---------------------------------------------------------------------------


class GroqProvider(LLMProvider):
    """Groq provider using the official ``groq`` Python SDK."""

    def __init__(self) -> None:
        try:
            from groq import Groq  # noqa: WPS433
        except ImportError as exc:
            raise ImportError(
                "groq is required for the Groq provider. "
                "Install it with:  pip install groq"
            ) from exc

        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to your .env file or environment variables."
            )

        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        logger.info("GroqProvider initialised (model=%s)", self.model)

    async def chat(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a chat completion via Groq.

        The Groq SDK is synchronous; this method wraps the call so callers
        can always ``await`` uniformly.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4096,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        logger.debug(
            "Groq request  model=%s  temperature=%.2f  json_mode=%s",
            self.model,
            temperature,
            json_mode,
        )

        try:
            import asyncio
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                **kwargs
            )
        except Exception:
            logger.exception("Groq API call failed")
            raise

        choice = response.choices[0]
        content = choice.message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
        }

        logger.debug(
            "Groq response  length=%d chars  usage=%s", len(content), usage
        )

        return LLMResponse(content=content, model=self.model, usage=usage)


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_provider: Optional[LLMProvider] = None


def get_llm() -> LLMProvider:
    """Return the configured :class:`LLMProvider` singleton.

    The provider is chosen at first call based on
    ``settings.LLM_PROVIDER`` (``"gemini"`` or ``"groq"``).

    Returns:
        A ready-to-use :class:`LLMProvider` instance.

    Raises:
        ValueError: If ``LLM_PROVIDER`` is set to an unsupported value.
    """
    global _provider  # noqa: WPS420

    if _provider is None:
        provider_name = settings.LLM_PROVIDER.lower().strip()
        logger.info("Initialising LLM provider: %s", provider_name)

        if provider_name == "groq":
            _provider = GroqProvider()
        elif provider_name == "gemini":
            _provider = GeminiProvider()
        else:
            raise ValueError(
                f"Unsupported LLM_PROVIDER={provider_name!r}. "
                "Choose 'gemini' or 'groq'."
            )

    return _provider
