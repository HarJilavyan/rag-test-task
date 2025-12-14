from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


@dataclass
class LLMClient:
    """
    Thin wrapper around OpenAI chat completion API.
    """
    model: str | None = None

    def __post_init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please create a .env file with OPENAI_API_KEY."
            )

        # The official SDK picks up OPENAI_API_KEY from env internally,
        # but we can still create a client explicitly.
        self._client = OpenAI(api_key=api_key)

        if self.model is None:
            self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        """
        Simple chat completion helper.
        """
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = resp.choices[0].message.content
        return content.strip() if content else ""
