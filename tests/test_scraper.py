"""Tests for the telegram scraper module."""

import pytest
from unittest.mock import Mock, patch
from src.scraper.telegram_scraper import TelegramScraper


class TestTelegramScraper:
    """Test cases for TelegramScraper class."""

    def test_scraper_initialization(self):
        """Test that scraper can be initialized with valid config."""
        config = {
            "api_id": "test_id",
            "api_hash": "test_hash",
            "phone": "test_phone"
        }
        
        with patch('src.scraper.telegram_scraper.TelegramClient'):
            scraper = TelegramScraper(config)
            assert scraper is not None

    def test_scraper_config_validation(self):
        """Test that scraper validates required config parameters."""
        with pytest.raises(ValueError):
            TelegramScraper({})

    @pytest.mark.asyncio
    async def test_scrape_messages_mock(self):
        """Test scraping messages with mocked client."""
        config = {
            "api_id": "test_id",
            "api_hash": "test_hash",
            "phone": "test_phone"
        }
        
        mock_messages = [
            Mock(id=1, text="Test message 1", date="2024-01-01"),
            Mock(id=2, text="Test message 2", date="2024-01-02")
        ]
        
        with patch('src.scraper.telegram_scraper.TelegramClient') as mock_client:
            mock_client.return_value.get_messages.return_value = mock_messages
            
            scraper = TelegramScraper(config)
            messages = await scraper.scrape_messages("@test_channel", limit=2)
            
            assert len(messages) == 2
            assert messages[0].text == "Test message 1" 