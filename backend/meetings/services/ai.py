import os
import logging

import anthropic

log = logging.getLogger(__name__)

class AnthropicClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key) if self.api_key else None
        self.language_model = os.getenv("ANTHROPIC_MODEL", "").strip()


    async def summarize(self, text: str) -> str:
        """
        Summarizes the given text using the Anthropic API.
        """
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            return "No notes available to summarize yet."

        if not self.client or not self.language_model:
            raise ValueError("Anthropic API client or model is not configured. Please set ANTHROPIC_API_KEY and ANTHROPIC_MODEL environment variables.")

        prompt = f"Summarize the following meeting notes:\n\n{cleaned_text}\n\nSummary:"

        response = await self.client.messages.create(
            model=self.language_model,
            max_tokens=500,
            system="You are a helpful assistant that summarizes meeting notes. You limit your responses to a summary, without additional commentary, feedback or meta-communication.",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        content_text = "\n".join(block.text for block in response.content if hasattr(block, "text")).strip()
        if not content_text:
            raise ValueError("Received empty summary from Anthropic API.")
        return content_text

client = AnthropicClient()
