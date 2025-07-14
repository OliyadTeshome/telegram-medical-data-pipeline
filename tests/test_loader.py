"""Tests for the postgres loader module."""

import pytest
from unittest.mock import Mock, patch
from src.loader.postgres_loader import PostgresLoader


class TestPostgresLoader:
    """Test cases for PostgresLoader class."""

    def test_loader_initialization(self):
        """Test that loader can be initialized with valid config."""
        config = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password"
        }
        
        with patch('src.loader.postgres_loader.create_engine'):
            loader = PostgresLoader(config)
            assert loader is not None

    def test_loader_config_validation(self):
        """Test that loader validates required config parameters."""
        with pytest.raises(ValueError):
            PostgresLoader({})

    @pytest.mark.asyncio
    async def test_load_messages_mock(self):
        """Test loading messages with mocked database."""
        config = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password"
        }
        
        mock_messages = [
            {"id": 1, "text": "Test message 1", "channel": "@test"},
            {"id": 2, "text": "Test message 2", "channel": "@test"}
        ]
        
        with patch('src.loader.postgres_loader.create_engine') as mock_engine:
            mock_session = Mock()
            mock_engine.return_value.begin.return_value.__enter__.return_value = mock_session
            
            loader = PostgresLoader(config)
            result = await loader.load_messages(mock_messages)
            
            assert result is True 