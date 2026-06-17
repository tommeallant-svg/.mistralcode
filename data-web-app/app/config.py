"""
Configuration management for the application.
Supports both CSV and PostgreSQL configurations.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class CSVConfig(BaseSettings):
    """CSV Configuration"""
    csv_directory: str = Field(
        default="data/csv",
        description="Directory where CSV files are stored",
        alias="CSV_DIRECTORY"
    )
    upload_directory: str = Field(
        default="data/uploads",
        description="Directory for uploaded CSV files",
        alias="UPLOAD_DIRECTORY"
    )
    max_file_size_mb: int = Field(
        default=10,
        description="Maximum CSV file size in MB",
        alias="MAX_FILE_SIZE_MB"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        populate_by_name=True,
        extra='ignore'
    )


class DatabaseConfig(BaseSettings):
    """PostgreSQL Configuration"""
    db_host: str = Field(
        default="localhost",
        description="Database host",
        alias="DB_HOST"
    )
    db_port: int = Field(
        default=5432,
        description="Database port",
        alias="DB_PORT"
    )
    db_name: str = Field(
        default="data_app",
        description="Database name",
        alias="DB_NAME"
    )
    db_user: str = Field(
        default="postgres",
        description="Database username",
        alias="DB_USER"
    )
    db_password: str = Field(
        default="postgres",
        description="Database password",
        alias="DB_PASSWORD"
    )
    db_pool_size: int = Field(
        default=5,
        description="Database connection pool size",
        alias="DB_POOL_SIZE"
    )
    db_max_overflow: int = Field(
        default=10,
        description="Database connection pool max overflow",
        alias="DB_MAX_OVERFLOW"
    )
    
    @property
    def database_url(self) -> str:
        """Construct the database URL"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        populate_by_name=True,
        extra='ignore'
    )


class AppConfig(BaseSettings):
    """Application Configuration"""
    app_name: str = Field(
        default="Data Web Application",
        description="Application name",
        alias="APP_NAME"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version",
        alias="APP_VERSION"
    )
    debug: bool = Field(
        default=False,
        description="Run in debug mode",
        alias="APP_DEBUG"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host to bind to",
        alias="APP_HOST"
    )
    port: int = Field(
        default=8000,
        description="Port to bind to",
        alias="APP_PORT"
    )
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for security",
        alias="APP_SECRET_KEY"
    )
    
    # Data source: 'csv' or 'postgres'
    data_source: str = Field(
        default="csv",
        description="Data source to use (csv or postgres)",
        alias="APP_DATA_SOURCE"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        populate_by_name=True,
        extra='ignore'
    )


class Settings:
    """Main settings class that aggregates all configurations"""
    app: AppConfig = AppConfig()
    csv: CSVConfig = CSVConfig()
    database: DatabaseConfig = DatabaseConfig()
    
    @classmethod
    def from_env(cls):
        """Load settings from environment variables"""
        return cls()


# Global settings instance
settings = Settings.from_env()
