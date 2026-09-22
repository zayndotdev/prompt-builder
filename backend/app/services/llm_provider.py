import asyncio
import logging
from typing import Optional, List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    Resilient Multi-Provider LLM Router.
    Routes calls between Cohere, Groq, Gemini, and Mistral with immediate fast-failover.
    """

    def __init__(self):
        self._groq_client = None
        self._gemini_client = None
        self._mistral_client = None
        self._cohere_client = None
        self._init_clients()

    def _init_clients(self):
        # 1. Initialize Cohere (Primary robust enterprise model)
        if settings.COHERE_API_KEY:
            try:
                import cohere
                self._cohere_client = cohere.ClientV2(api_key=settings.COHERE_API_KEY)
                logger.info("Cohere client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere client: {e}")

        # 2. Initialize Groq (Sub-second fast model)
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.startswith("gsk_"):
            try:
                from groq import AsyncGroq
                self._groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
                logger.info("Groq client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

        # 3. Initialize Gemini (Google GenAI)
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

        # 4. Initialize Mistral
        if settings.MISTRAL_API_KEY:
            try:
                from mistralai.client import Mistral
                self._mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)
                logger.info("Mistral client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Mistral client: {e}")

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        preferred_provider: str = "cohere",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Generate text with automatic multi-provider fallback.
        Tries preferred provider first, cascades immediately on rate limits or errors.
        """
        providers_order = [preferred_provider]
        fallbacks = ["cohere", "groq", "mistral", "gemini"]
        for p in fallbacks:
            if p not in providers_order:
                providers_order.append(p)

        # Deprioritize providers known to be quota exhausted (e.g. daily free limit)
        if not hasattr(self, "_quota_exhausted"):
            self._quota_exhausted = set()
        
        active_order = [p for p in providers_order if p not in self._quota_exhausted]
        for p in providers_order:
            if p not in active_order:
                active_order.append(p)

        last_error = None
        # Try two passes in case of transient 429 / RPM cooldowns
        for attempt in range(2):
            for provider in active_order:
                try:
                    res = ""
                    if provider == "cohere" and self._cohere_client:
                        res = await asyncio.wait_for(
                            self._call_cohere(prompt, system_prompt, temperature, max_tokens),
                            timeout=90.0
                        )
                    elif provider == "groq" and self._groq_client:
                        groq_tokens = min(max_tokens, 1000)
                        res = await asyncio.wait_for(
                            self._call_groq(prompt, system_prompt, temperature, groq_tokens),
                            timeout=45.0
                        )
                    elif provider == "mistral" and self._mistral_client:
                        res = await asyncio.wait_for(
                            self._call_mistral(prompt, system_prompt, temperature, max_tokens),
                            timeout=45.0
                        )
                    elif provider == "gemini" and self._gemini_client:
                        res = await asyncio.wait_for(
                            self._call_gemini(prompt, system_prompt, temperature),
                            timeout=45.0
                        )
                    if res and len(res.strip()) > 0:
                        return res
                    raise ValueError(f"Provider {provider} returned empty response")
                except asyncio.TimeoutError:
                    logger.warning(f"Provider {provider} timed out after waiting. Trying next provider...")
                    last_error = TimeoutError(f"Provider {provider} timed out")
                    await asyncio.sleep(0.5)
                    continue
                except Exception as e:
                    err_str = str(e) or type(e).__name__
                    logger.warning(f"Provider {provider} error: {err_str[:120]}. Trying next provider...")
                    last_error = e
                    if "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str:
                        self._quota_exhausted.add(provider)
                        await asyncio.sleep(1.5)
                    continue

            if attempt == 0:
                logger.info("All providers experienced transient errors on first pass. Waiting 3s for cooldown before retry...")
                await asyncio.sleep(3.0)

        raise RuntimeError(f"All LLM providers failed after 2 passes. Last error: {last_error}")

    async def _call_cohere(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str:
        def _sync_cohere():
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self._cohere_client.chat(
                model=settings.COHERE_DEFAULT_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            if hasattr(response, "message") and hasattr(response.message, "content"):
                content_blocks = response.message.content
                if isinstance(content_blocks, list) and len(content_blocks) > 0:
                    return getattr(content_blocks[0], "text", "")
                elif hasattr(content_blocks, "text"):
                    return content_blocks.text
            return str(response)

        return await asyncio.to_thread(_sync_cohere)

    async def _call_groq(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._groq_client.chat.completions.create(
            model=settings.GROQ_DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content or ""

    async def _call_gemini(self, prompt: str, system_prompt: str, temperature: float) -> str:
        def _sync_gemini():
            from google.genai import types
            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_prompt if system_prompt else None
            )
            response = self._gemini_client.models.generate_content(
                model=settings.GEMINI_DEFAULT_MODEL,
                contents=prompt,
                config=config
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

    def get_status(self) -> Dict[str, bool]:
        """Returns availability of each provider."""
        return {
            "cohere": self._cohere_client is not None,
            "groq": self._groq_client is not None,
            "gemini": self._gemini_client is not None,
            "mistral": self._mistral_client is not None,
        }

llm_provider = LLMProvider()
