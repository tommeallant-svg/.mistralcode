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
        description="Directory where CSV files are stored"
    )
    upload_directory: str = Field(
        default="data/uploads",
        description="Directory for uploaded CSV files"
    )
    max_file_size_mb: int = Field(
        default=10,
        description="Maximum CSV file size in MB"
    )
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


class DatabaseConfig(BaseSettings):
    """PostgreSQL Configuration"""
    db_host: str = Field(
        default="localhost",
        description="Database host"
    )
    db_port: int = Field(
        default=5432,
        description="Database port"
    )
    db_name: str = Field(
        default="data_app",
        description="Database name"
    )
    db_user: str = Field(
        default="postgres",
        description="Database username"
    )
    db_password: str = Field(
        default="postgres",
        description="Database password"
    )
    db_pool_size: int = Field(
        default=5,
        description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        default=10,
        description="Database connection pool max overflow"
    )
    
    @property
    def database_url(self) -> str:
        """Construct the database URL"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


class AppConfig(BaseSettings):
    """Application Configuration"""
    app_name: str = Field(
        default="Data Web Application",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    debug: bool = Field(
        default=False,
        description="Run in debug mode"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host to bind to"
    )
    port: int = Field(
        default=8000,
        description="Port to bind to"
    )
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for security"
    )
    
    # Data source: 'csv' or 'postgres'
    data_source: str = Field(
        default="csv",
        description="Data source to use (csv or postgres)"
    )
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


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
