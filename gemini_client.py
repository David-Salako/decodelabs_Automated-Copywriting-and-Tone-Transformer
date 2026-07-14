"""
Thin wrapper around the Gemini API (google-genai SDK).
Handles client setup, temperature/top_p injection, and structured
(Pydantic-validated) output.
"""

import asyncio
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

from schemas import MarketingCopy
from prompt_templates import compile_prompt, get_platform_config

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DEFAULT_MODEL = "gemini-2.0-flash"


def _get_env_value(key: str) -> str | None:
    value = os.getenv(key)
    if value:
        return value.strip()

    candidate_paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    seen = set()
    for env_path in candidate_paths:
        if env_path in seen:
            continue
        seen.add(env_path)
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip().lstrip("\ufeff")
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    name, _, val = line.partition("=")
                    if name.strip() == key:
                        return val.strip().strip('"').strip("'")
    return None


def _get_client() -> genai.Client:
    api_key = _get_env_value("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Create a .env file (see .env.example) "
            "with your Gemini API key from Google AI Studio."
        )
    # New-format Gemini auth keys are plain strings just like before --
    # just pass them straight into api_key. No prefix or encoding needed.
    return genai.Client(api_key=api_key)


def _build_config(platform: str) -> types.GenerateContentConfig:
    cfg = get_platform_config(platform)
    return types.GenerateContentConfig(
        temperature=cfg.temperature,
        top_p=cfg.top_p,
        response_mime_type="application/json",
        response_schema=MarketingCopy,
    )


def generate_copy(
    product_name: str, description: str, tone: str, platform: str, model: str | None = None
) -> MarketingCopy:
    """Synchronous single generation -- used by the CLI's real-time mode."""
    client = _get_client()
    prompt = compile_prompt(product_name, description, tone, platform)
    selected_model = model or _get_env_value("GEMINI_MODEL") or DEFAULT_MODEL

    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=selected_model,
                contents=prompt,
                config=_build_config(platform),
            )
            return MarketingCopy.model_validate_json(response.text)
        except Exception as exc:
            message = str(exc).lower()
            if "429" in message or "resource_exhausted" in message or "quota" in message:
                if attempt < 3:
                    delay = 2**attempt + 1
                    time.sleep(delay)
                    continue
            raise


async def generate_copy_async(
    product_name: str, description: str, tone: str, platform: str, model: str | None = None
) -> MarketingCopy:
    client = _get_client()
    prompt = compile_prompt(product_name, description, tone, platform)
    selected_model = model or _get_env_value("GEMINI_MODEL") or DEFAULT_MODEL

    for attempt in range(1, 4):
        try:
            response = await client.aio.models.generate_content(
                model=selected_model,
                contents=prompt,
                config=_build_config(platform),
            )
            return MarketingCopy.model_validate_json(response.text)
        except Exception as exc:
            message = str(exc).lower()
            if "429" in message or "resource_exhausted" in message or "quota" in message:
                if attempt < 3:
                    delay = 2**attempt + 1
                    await asyncio.sleep(delay)
                    continue
            raise