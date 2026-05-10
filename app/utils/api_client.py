"""Minimal DeepSeek API client."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request


class DeepSeekAPIError(Exception):
    """Raised when the DeepSeek API call fails."""


class DeepSeekAPIClient:
    """Simple HTTP client for DeepSeek chat completion."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = (base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip("/")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.timeout = timeout

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.8,
        max_tokens: int = 512,
    ) -> str:
        """Call DeepSeek chat completion and return plain text."""
        if not self.api_key:
            raise DeepSeekAPIError("Missing DEEPSEEK_API_KEY.")

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        req = request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise DeepSeekAPIError(
                f"DeepSeek API HTTP error {exc.code}: {error_body}"
            ) from exc
        except error.URLError as exc:
            raise DeepSeekAPIError(f"DeepSeek API connection error: {exc}") from exc

        return self._extract_content(response_data)

    def _extract_content(self, response_data: dict[str, Any]) -> str:
        """Extract the assistant text from the API response."""
        choices = response_data.get("choices", [])
        if not choices:
            raise DeepSeekAPIError("DeepSeek API returned no choices.")

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if not isinstance(content, str) or not content.strip():
            raise DeepSeekAPIError("DeepSeek API returned empty content.")

        return content.strip()
