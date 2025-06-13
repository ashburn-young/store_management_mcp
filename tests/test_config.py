"""Tests for the shared configuration module."""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from google_business_analytics.shared.config import Config


class TestConfig:
    """Test cases for the Config class."""
    
    def test_default_config_loading(self):
        """Test loading default configuration when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_config = Path(temp_dir) / "nonexistent.yaml"
            config = Config(config_path=str(non_existent_config))
            
            # Should load defaults
            assert config.get('google_api.requests_per_minute') == 100
            assert config.get('processing.sentiment_threshold_positive') == 0.1
            assert config.get('development.use_mock_data') is True
    
    def test_config_file_loading(self, temp_config_dir):
        """Test loading configuration from YAML file."""
        config_path = Path(temp_config_dir) / "config" / "config.yaml"
        config = Config(config_path=str(config_path))
        
        assert config.get('google_api.api_key') == "test_api_key"
        assert config.get('google_api.requests_per_minute') == 10
        assert config.get('processing.min_theme_frequency') == 2
    
    def test_environment_variable_replacement(self):
        """Test environment variable replacement in config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Create config with environment variable
            config_content = """
google_api:
  api_key: "${TEST_API_KEY}"
  requests_per_minute: 100
"""
            config_file = config_dir / "config.yaml"
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            # Set environment variable
            with patch.dict(os.environ, {'TEST_API_KEY': 'env_test_key'}):
                config = Config(config_path=str(config_file))
                assert config.get('google_api.api_key') == 'env_test_key'
    
    def test_get_with_dot_notation(self, temp_config_dir):
        """Test getting values with dot notation."""
        config_path = Path(temp_config_dir) / "config" / "config.yaml"
        config = Config(config_path=str(config_path))
        
        # Test existing key
        assert config.get('google_api.api_key') == "test_api_key"
        
        # Test non-existent key with default
        assert config.get('non.existent.key', 'default_value') == 'default_value'
        
        # Test nested access
        assert config.get('processing.sentiment_threshold_positive') == 0.1
    
    def test_helper_methods(self, temp_config_dir):
        """Test convenience helper methods."""
        config_path = Path(temp_config_dir) / "config" / "config.yaml"
        config = Config(config_path=str(config_path))
        
        # Test helper methods
        google_config = config.get_google_api_config()
        assert google_config['api_key'] == "test_api_key"
        
        processing_config = config.get_processing_config()
        assert processing_config['sentiment_threshold_positive'] == 0.1
        
        dev_config = config.get_development_config()
        assert dev_config['use_mock_data'] is True

    def test_mock_data_path(self, temp_config_dir):
        """Test mock data path resolution."""
        config_path = Path(temp_config_dir) / "config" / "config.yaml"
        config = Config(config_path=str(config_path))
        
        mock_path = config.get_mock_data_path()
        
        # Create the data directory for this test
        mock_path.mkdir(parents=True, exist_ok=True)
        
        assert mock_path.exists()
        assert mock_path.name == "data"
    
    def test_use_mock_data_detection(self, temp_config_dir):
        """Test mock data usage detection."""
        config_path = Path(temp_config_dir) / "config" / "config.yaml"
        config = Config(config_path=str(config_path))
        
        # Should use mock data from config
        assert config.use_mock_data() is True
        
        # Test environment variable override
        with patch.dict(os.environ, {'USE_MOCK_DATA': 'false'}):
            # Environment variable should override config
            assert config.use_mock_data() is False
        
        with patch.dict(os.environ, {'USE_MOCK_DATA': 'true'}):
            assert config.use_mock_data() is True
