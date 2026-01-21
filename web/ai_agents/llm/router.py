import logging
import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ModelTier:
    name: str
    models: List[str]
    description: str

class ModelRouter:
    """Routes LLM requests to appropriate models based on task type and availability."""

    TIERS = {
        "reasoning": ModelTier(
            name="reasoning",
            models=["gpt-4o", "claude-3-5-sonnet-20240620", "gemini-1.5-pro"],
            description="High-reasoning models for planning and complex analysis."
        ),
        "data_processing": ModelTier(
            name="data_processing",
            models=["gpt-4o-mini", "claude-3-haiku-20240307", "gemini-1.5-flash"],
            description="Fast, low-cost models for information extraction and tool output processing."
        ),
        "summary": ModelTier(
            name="summary",
            models=["gpt-4o-mini", "gemini-1.5-flash"],
            description="Terse models for conversation summarization."
        )
    }

    def __init__(self, default_tier: str = "reasoning"):
        self.default_tier = default_tier
        self._circuit_breakers: Dict[str, bool] = {} # model -> is_open

    def get_model(self, tier: str = None, task_description: str = "") -> str:
        """Get the best available model for a given tier/task."""
        target_tier = tier or self.default_tier
        if target_tier not in self.TIERS:
            target_tier = self.default_tier

        tier_info = self.TIERS[target_tier]
        
        # Filter out models with open circuit breakers
        available_models = [m for m in tier_info.models if not self._circuit_breakers.get(m, False)]
        
        if not available_models:
            logger.warning(f"No available models in tier {target_tier}. Resetting circuit breakers.")
            for m in tier_info.models:
                self._circuit_breakers[m] = False
            available_models = tier_info.models

        # For now, just pick the first one or random? 
        # OpenAI usually first, but we can do random if we want load balancing
        return available_models[0]

    def report_failure(self, model: str):
        """Open circuit breaker for a failing model."""
        logger.error(f"Model failure reported: {model}. Opening circuit breaker.")
        self._circuit_breakers[model] = True

    def report_success(self, model: str):
        """Close circuit breaker for a successful model."""
        if self._circuit_breakers.get(model, False):
            logger.info(f"Model success reported: {model}. Closing circuit breaker.")
            self._circuit_breakers[model] = False
