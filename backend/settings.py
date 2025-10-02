from typing import Optional

from dotenv import load_dotenv
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Database
    database_url: str
    blueprint_database_url: str

    # API Key
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    def get_model(self, llm_provider: str, llm_model: str, ollama_base_url: str | None = None) -> Model:
        if llm_provider == "openai":
            return OpenAIChatModel(model_name=llm_model, provider="openai")
        elif llm_provider == "anthropic":
            return AnthropicModel(model_name=llm_model)
        elif llm_provider == "google":
            return GoogleModel(model_name=llm_model)
        elif llm_provider == "ollama":
            from pydantic_ai.providers.ollama import OllamaProvider
            assert ollama_base_url is not None, "OLLAMA_BASE_URL must be set to use Ollama"
            return OpenAIChatModel(
                model_name=llm_model,
                provider=OllamaProvider(base_url=ollama_base_url),
            )
        else:
            raise ValueError(f"Invalid LLM: {llm_provider}")


settings = Settings()
