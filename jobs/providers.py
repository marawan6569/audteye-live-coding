import random
import time
import uuid
from dataclasses import dataclass


class ProviderTimeout(Exception):
    """Raised when the provider takes too long. Retryable."""


class ProviderRateLimit(Exception):
    """Raised when we hit provider rate limits. Retryable with backoff."""


class ProviderInvalidPrompt(Exception):
    """Raised when the prompt is rejected. NOT retryable."""


class ProviderInternalError(Exception):
    """Generic provider failure. Retryable."""


@dataclass
class GenerationResult:
    image_url: str
    cost_usd: float


def generate(prompt: str) -> GenerationResult:
    """
    Simulates an external image generation API.
    Behavior is intentionally flaky to mirror production reality.

    DO NOT modify this function during the interview.
    """
    # Simulate latency: 2-8 seconds typical, occasionally much longer
    latency = random.choices(
        [random.uniform(2, 8), random.uniform(15, 30)],
        weights=[0.85, 0.15],
    )[0]
    time.sleep(latency)

    if latency > 12:
        raise ProviderTimeout("Provider timeout after 12s")

    roll = random.random()
    if roll < 0.10:
        raise ProviderInternalError("Provider 500")
    if roll < 0.15:
        raise ProviderRateLimit("Rate limit exceeded, retry after 5s")
    if "FORBIDDEN" in prompt.upper():
        raise ProviderInvalidPrompt("Prompt rejected by safety filter")

    return GenerationResult(
        image_url=f"https://fake-cdn.designar.ai/{uuid.uuid4()}.png",
        cost_usd=round(random.uniform(0.02, 0.08), 4),
    )
