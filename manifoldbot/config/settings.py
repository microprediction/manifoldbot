"""
Configuration management for ManifoldBot.

Handles loading and validation of bot configurations from YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


class DataSourceConfig(BaseModel):
    """Configuration for a data source."""

    type: str = Field(..., description="Type of data source (web, rss, api)")
    name: str = Field(..., description="Name of the data source")
    url: str = Field(..., description="URL or endpoint for the data source")
    selector: Optional[str] = Field(None, description="CSS selector for web scraping")
    poll_interval: int = Field(900, description="Polling interval in seconds")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed_types = ["web", "rss", "api"]
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}")
        return v


class AIConfig(BaseModel):
    """Configuration for AI analysis."""

    model: str = Field("gpt-4o-mini", description="OpenAI model to use")
    max_tokens: int = Field(2000, description="Maximum tokens for analysis")
    temperature: float = Field(0.1, description="Temperature for AI responses")
    confidence_threshold: float = Field(0.75, description="Minimum confidence for actions")


class UserConfig(BaseModel):
    """Configuration for a specific user to monitor."""
    
    username: str = Field(..., description="Manifold username")
    description: str = Field("", description="Description of user's market focus")
    specialties: List[str] = Field(default_factory=list, description="List of market specialties")
    example_market: Optional[str] = Field(None, description="Example market question")


class ManifoldConfig(BaseModel):
    """Configuration for Manifold Markets integration."""

    market_slug: str = Field(..., description="Manifold market slug to monitor")
    comment_only: bool = Field(True, description="Only post comments, don't trade")
    max_position_size: float = Field(5.0, description="Maximum position size in M$")
    default_probability: float = Field(0.55, description="Default probability for trades")
    monitored_users: List[UserConfig] = Field(default_factory=list, description="List of users to monitor")


class FilterConfig(BaseModel):
    """Configuration for content filtering."""

    keywords: Optional[Dict[str, List[str]]] = Field(None, description="Keyword filters")
    confidence_gates: Optional[Dict[str, bool]] = Field(None, description="Confidence gates")


class BotConfig(BaseModel):
    """Main bot configuration."""

    name: str = Field(..., description="Bot name")
    description: str = Field("", description="Bot description")
    data_sources: List[DataSourceConfig] = Field(..., description="List of data sources")
    ai: AIConfig = Field(default_factory=AIConfig, description="AI configuration")
    manifold: ManifoldConfig = Field(..., description="Manifold Markets configuration")
    filters: Optional[FilterConfig] = Field(None, description="Content filters")

    # Environment variables
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    manifold_api_key: Optional[str] = Field(None, description="Manifold API key")

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def load_openai_key(cls, v):
        return v or os.getenv("OPENAI_API_KEY")

    @field_validator("manifold_api_key", mode="before")
    @classmethod
    def load_manifold_key(cls, v):
        return v or os.getenv("MANIFOLD_API_KEY")


def load_config(config_path: str) -> BotConfig:
    """
    Load bot configuration from a YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Validated BotConfig object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    import yaml

    # Load environment variables
    load_dotenv()

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    try:
        return BotConfig(**config_data)
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")


def get_default_monitored_users() -> List[UserConfig]:
    """
    Get the default list of users to monitor.
    
    Returns:
        List of UserConfig objects for default monitored users
    """
    return [
        UserConfig(
            username="BoltonBailey",
            description="Macro/industrial questions tied to lithium production rankings and other econ tech topics",
            specialties=["lithium production", "macro economics", "industrial technology", "commodities"],
            example_market="Will the US be a top 3 lithium producer in 2033?"
        ),
        UserConfig(
            username="JoshDreckmeyr", 
            description="Frequent, clearly resolved gold (XAU/USD) price markets using standard data sources",
            specialties=["gold prices", "XAU/USD", "precious metals", "forex"],
            example_market="GOLD closes above $3,330 this week?"
        ),
        UserConfig(
            username="strutheo",
            description="Longer-horizon gold markets framed for max price by date, good for scenario thinking", 
            specialties=["gold price scenarios", "long-term forecasting", "precious metals"],
            example_market="Highest value gold reaches by end of 2027?"
        ),
        UserConfig(
            username="postjawline",
            description="Materials/science angles that still touch copper (e.g., Meissner-effect claims in Cu-doped apatite) with explicit resolution conditions",
            specialties=["materials science", "copper", "superconductivity", "scientific claims"],
            example_market="Meissner-effect claims in Cu-doped apatite"
        )
    ]


def create_example_config() -> str:
    """
    Create an example configuration file.

    Returns:
        YAML configuration string
    """
    return """# ManifoldBot Configuration Example
name: "Example Trading Bot"
description: "Monitors data sources and trades on Manifold Markets"

data_sources:
  - type: "web"
    name: "Example News Site"
    url: "https://example.com/news"
    selector: ".news-item"
    poll_interval: 900  # 15 minutes
    
  - type: "rss"
    name: "Example RSS Feed"
    url: "https://example.com/feed.xml"
    poll_interval: 1800  # 30 minutes

ai:
  model: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.1
  confidence_threshold: 0.75

manifold:
  market_slug: "your-username/your-market-slug"
  comment_only: true  # Start with comments only
  max_position_size: 5.0  # M$
  default_probability: 0.55
  monitored_users:
    - username: "BoltonBailey"
      description: "Macro/industrial questions tied to lithium production rankings and other econ tech topics"
      specialties: ["lithium production", "macro economics", "industrial technology", "commodities"]
      example_market: "Will the US be a top 3 lithium producer in 2033?"
    - username: "JoshDreckmeyr"
      description: "Frequent, clearly resolved gold (XAU/USD) price markets using standard data sources"
      specialties: ["gold prices", "XAU/USD", "precious metals", "forex"]
      example_market: "GOLD closes above $3,330 this week?"
    - username: "strutheo"
      description: "Longer-horizon gold markets framed for max price by date, good for scenario thinking"
      specialties: ["gold price scenarios", "long-term forecasting", "precious metals"]
      example_market: "Highest value gold reaches by end of 2027?"
    - username: "postjawline"
      description: "Materials/science angles that still touch copper with explicit resolution conditions"
      specialties: ["materials science", "copper", "superconductivity", "scientific claims"]
      example_market: "Meissner-effect claims in Cu-doped apatite"

filters:
  keywords:
    include: ["keyword1", "keyword2"]
    exclude: ["spam", "irrelevant"]
  
  confidence_gates:
    entity_match: true
    action_required: true
    evidence_required: true
"""
