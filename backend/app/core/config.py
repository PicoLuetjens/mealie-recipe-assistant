from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./assistant.db"
    jwt_secret: str = "replace-with-a-long-random-secret"
    first_admin_email: str = "admin@example.invalid"
    first_admin_password: str = "change-me-before-first-start"
    openai_api_key: str = "replace-with-a-real-openai-api-key"
    openai_recipe_model: str = "gpt-4o-mini"
    openai_transcribe_model: str = "gpt-4o-mini-transcribe"
    openai_image_model: str = "gpt-image-1"
    mealie_base_url: str = "http://mealie:9000"
    mealie_api_token: str = "replace-with-the-token-of-the-mealie-service-user"

    @property
    def openai_ready(self) -> bool:
        return not self.openai_api_key.startswith("replace-with-")

    @property
    def mealie_ready(self) -> bool:
        return not self.mealie_api_token.startswith("replace-with-")


settings = Settings()

