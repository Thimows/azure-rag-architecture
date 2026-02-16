from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = ""

    AZURE_SEARCH_ENDPOINT: str = ""
    AZURE_SEARCH_API_KEY: str = ""
    AZURE_SEARCH_INDEX_NAME: str = "rag-index"

    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "documents"

    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str = ""
    AZURE_DOCUMENT_INTELLIGENCE_KEY: str = ""

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
