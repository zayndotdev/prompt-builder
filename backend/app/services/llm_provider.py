import asyncio
import logging
from typing import Optional, List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    Resilient Multi-Provider LLM Router.
    Routes calls between Groq, Gemini, Mistral, and Cohere with automatic fallback.
    """

    def __init__(self):
        self._groq_client = None
        self._gemini_client = None
        self._mistral_client = None
        self._cohere_client = None
        self._init_clients()

    def _init_clients(self):
        # 1. Initialize Groq
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.startswith("gsk_"):
            try:
                from groq import AsyncGroq
                self._groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
                logger.info("Groq client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

        # 2. Initialize Gemini (Google GenAI)
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

        # 3. Initialize Mistral
        if settings.MISTRAL_API_KEY:
            try:
                from mistralai.client import Mistral
                self._mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)
                logger.info("Mistral client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Mistral client: {e}")

        # 4. Initialize Cohere
        if settings.COHERE_API_KEY:
            try:
                import cohere
                self._cohere_client = cohere.AsyncClientV2(api_key=settings.COHERE_API_KEY)
                logger.info("Cohere client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere client: {e}")

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        preferred_provider: str = "groq",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Generate text with automatic multi-provider fallback.
        Tries preferred_provider first, then cascades to available fallbacks.
        """
        providers_order = [preferred_provider]
        fallbacks = ["groq", "gemini", "mistral", "cohere"]
        for p in fallbacks:
            if p not in providers_order:
                providers_order.append(p)

        last_error = None
        for provider in providers_order:
            try:
                if provider == "groq" and self._groq_client:
                    return await self._call_groq(prompt, system_prompt, temperature, max_tokens)
                elif provider == "gemini" and self._gemini_client:
                    return await self._call_gemini(prompt, system_prompt, temperature)
                elif provider == "mistral" and self._mistral_client:
                    return await self._call_mistral(prompt, system_prompt, temperature, max_tokens)
                elif provider == "cohere" and self._cohere_client:
                    return await self._call_cohere(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}. Trying fallback...")
                last_error = e
                continue

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

    async def _call_groq(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Use 70b versatile for deep reasoning, 8b instant for high-throughput
        model = settings.GROQ_DEFAULT_MODEL
        response = await self._groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content or ""

    async def _call_gemini(self, prompt: str, system_prompt: str, temperature: float) -> str:
        def _sync_gemini():
            contents = prompt
            config = {}
            if system_prompt:
                config["system_instruction"] = system_prompt
            config["temperature"] = temperature
            
            response = self._gemini_client.models.generate_content(
                model=settings.GEMINI_DEFAULT_MODEL,
                contents=contents,
                config=config if config else None
            )
            return response.text or ""

        return await asyncio.to_thread(_sync_gemini)

    async def _call_mistral(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str:
        def _sync_mistral():
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self._mistral_client.chat.complete(
                model=settings.MISTRAL_DEFAULT_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""

        return await asyncio.to_thread(_sync_mistral)

    async def _call_cohere(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._cohere_client.chat(
            model=settings.COHERE_DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        # Handle Cohere V2 message output
        if hasattr(response, "message") and hasattr(response.message, "content"):
            content_blocks = response.message.content
            if isinstance(content_blocks, list) and len(content_blocks) > 0:
                return getattr(content_blocks[0], "text", "")
            elif hasattr(content_blocks, "text"):
                return content_blocks.text
        return str(response)

    def get_status(self) -> Dict[str, bool]:
        """Returns availability of each provider."""
        return {
            "groq": self._groq_client is not None,
            "gemini": self._gemini_client is not None,
            "mistral": self._mistral_client is not None,
            "cohere": self._cohere_client is not None,
        }

llm_provider = LLMProvider()
