"""
This is the "Master Instruction Template" from the project brief.
Raw user input (product name, platform, tone) never goes straight to the model.
It is always compiled into this locked template first, so the model always
gets the same structural instructions and brand-safety guardrails, no matter
what the user typed.
"""

from dataclasses import dataclass


@dataclass
class PlatformConfig:
    name: str
    max_chars: int
    style_notes: str
    use_hashtags: bool
    temperature: float
    top_p: float


# Platform-specific constraints, injected as conditional logic before the
# payload is sent to the model (per the "Platform-Specific Filtering" slide).
PLATFORM_CONFIGS = {
    "linkedin": PlatformConfig(
        name="LinkedIn",
        max_chars=1300,
        style_notes="Professional, insight-driven, no excessive emojis.",
        use_hashtags=True,
        temperature=0.5,
        top_p=0.9,
    ),
    "instagram": PlatformConfig(
        name="Instagram",
        max_chars=2200,
        style_notes="Casual, visual, emoji-friendly, hook in the first line.",
        use_hashtags=True,
        temperature=0.85,
        top_p=0.95,
    ),
    "email": PlatformConfig(
        name="Email",
        max_chars=1500,
        style_notes="Structured, persuasive, clear subject-to-body flow, minimal emojis.",
        use_hashtags=False,
        temperature=0.3,
        top_p=0.85,
    ),
    "twitter": PlatformConfig(
        name="Twitter/X",
        max_chars=280,
        style_notes="Punchy, concise, one idea only, witty hook.",
        use_hashtags=True,
        temperature=0.8,
        top_p=0.95,
    ),
}


def get_platform_config(platform: str) -> PlatformConfig:
    key = platform.strip().lower()
    if key not in PLATFORM_CONFIGS:
        valid = ", ".join(PLATFORM_CONFIGS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Choose from: {valid}")
    return PLATFORM_CONFIGS[key]


def compile_prompt(product_name: str, description: str, tone: str, platform: str) -> str:
    """
    Dynamic Compilation step: f-strings merge user variables into the
    hidden master template. The application layer is the gatekeeper --
    the end user only ever supplies raw facts, never the structural prompt.
    """
    cfg = get_platform_config(platform)

    hashtag_line = (
        "Include 3-5 relevant hashtags."
        if cfg.use_hashtags
        else "Do not include hashtags."
    )

    return f"""You are a professional marketing copywriter.

Product name: {product_name}
Product description: {description}
Target platform: {cfg.name}
Required tone: {tone}

Platform rules (must follow strictly):
- Style: {cfg.style_notes}
- Hard limit: the "body" field must stay under {cfg.max_chars} characters.
- {hashtag_line}

Write marketing copy for this product that fits the platform and tone above.
Return only the structured fields requested -- no extra commentary."""