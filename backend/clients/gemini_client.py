"""
Gemini API client wrapper with retry logic and structured output support.
"""

import json
import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


class RateLimitError(Exception):
    """Custom exception for rate limit errors."""
    pass


class GeminiAPIError(Exception):
    """Base exception for Gemini API failures."""
    pass


class GeminiClient:
    """
    Client for interacting with Google Gemini API.
    Supports structured JSON output and retry logic.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment")

        genai.configure(api_key=self.api_key)

        # Generation configuration
        self.generation_config = {
            "temperature": 0.7,  # Balanced creativity and consistency
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        # Safety settings (disabled for business use case)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        # Initialize model - using Pro for better reliability
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from Gemini.

        Args:
            prompt: Instruction prompt
            schema: Optional JSON schema for validation

        Returns:
            Parsed JSON response

        Raises:
            RateLimitError: If rate limit is exceeded
            GeminiAPIError: If API call fails
        """
        try:
            # Add explicit JSON instruction to prompt
            json_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting, no explanation."

            # Use the existing model
            response = self.model.generate_content(json_prompt)

            # Extract JSON from response text
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            elif response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```

            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```

            response_text = response_text.strip()

            # Parse JSON response
            return json.loads(response_text)

        except json.JSONDecodeError as e:
            raise GeminiAPIError(f"Failed to parse JSON from Gemini response: {e}\nResponse: {response_text[:200]}")
        except Exception as e:
            error_str = str(e).lower()
            if "429" in str(e) or "quota" in error_str or "rate limit" in error_str:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            raise GeminiAPIError(f"Gemini API call failed: {e}")

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_text(self, prompt: str) -> str:
        """
        Generate text response from Gemini.

        Args:
            prompt: Instruction prompt

        Returns:
            Generated text

        Raises:
            RateLimitError: If rate limit is exceeded
            GeminiAPIError: If API call fails
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            error_str = str(e).lower()
            if "429" in str(e) or "quota" in error_str or "rate limit" in error_str:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            raise GeminiAPIError(f"Gemini API call failed: {e}")

    def health_check(self) -> bool:
        """
        Check if the Gemini API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.generate_text("Hello")
            return len(response) > 0
        except Exception:
            return False
