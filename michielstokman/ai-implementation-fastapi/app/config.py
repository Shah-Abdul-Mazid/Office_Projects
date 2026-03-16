from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    ai_model: str = Field(default='gpt-4.1-mini', alias='AI_MODEL')
    openai_api_key: str = Field(default='', alias='OPENAI_API_KEY')
    elevenlabs_api_key: str = Field(default='', alias='ELEVENLABS_API_KEY')
    use_mock_ai: bool = Field(default=True, alias='USE_MOCK_AI')
    min_words: int = Field(default=900, alias='MIN_WORDS')
    max_words: int = Field(default=1500, alias='MAX_WORDS')
    output_dir: str = Field(default='./michielstokman/ai-implementation-fastapi/output', alias='OUTPUT_DIR')


settings = Settings()
