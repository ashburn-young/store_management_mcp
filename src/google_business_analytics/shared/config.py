"""Configuration management for Google Business Analytics MCP Server."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the MCP server."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. Defaults to config/config.yaml
        """
        # Load environment variables
        load_dotenv()
        
        # Set default config path
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Replace environment variables in YAML content
                content = self._replace_env_vars(content)
                self._config = yaml.safe_load(content) or {}
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}. Using defaults.")
            self._config = self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}. Using defaults.")
            self._config = self._get_default_config()
    
    def _replace_env_vars(self, content: str) -> str:
        """Replace ${VAR} placeholders with environment variables."""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, f"${{{var_name}}}")
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, content)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'google_api': {
                'api_key': os.getenv('GOOGLE_API_KEY', ''),
                'timeout': 30,
                'max_retries': 3,
                'requests_per_minute': 100
            },
            'processing': {
                'batch_size': 100,
                'sentiment_threshold_positive': 0.1,
                'sentiment_threshold_negative': -0.1,
                'theme_extraction_min_frequency': 3
            },
            'executive': {
                'alert_threshold_rating': 3.0,
                'alert_threshold_review_count': 10,
                'summary_period_days': 30,
                'top_issues_limit': 5
            },
            'mcp': {
                'collection_agent': {
                    'name': 'collection-agent',
                    'port': 3001
                },
                'aggregation_agent': {
                    'name': 'aggregation-agent',
                    'port': 3002
                }
            },
            'development': {
                'use_mock_data': True,
                'mock_data_path': 'data/',
                'debug': True
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'google_api.api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_google_api_config(self) -> Dict[str, Any]:
        """Get Google API configuration."""
        return self.get('google_api', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get data processing configuration."""
        return self.get('processing', {})
    
    def get_executive_config(self) -> Dict[str, Any]:
        """Get executive summary configuration."""
        return self.get('executive', {})
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP server configuration."""
        return self.get('mcp', {})
    
    def get_development_config(self) -> Dict[str, Any]:
        """Get development configuration."""
        return self.get('development', {})
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return os.getenv('ENVIRONMENT', 'development') == 'development'
    
    def use_mock_data(self) -> bool:
        """Check if should use mock data."""
        env_mock_value = os.getenv('USE_MOCK_DATA', '')
        
        # If environment variable is explicitly set, use its value
        if env_mock_value:
            return env_mock_value.lower() in ('true', '1', 'yes')
        
        # Otherwise use config value
        return self.get('development.use_mock_data', True)
    
    def get_mock_data_path(self) -> Path:
        """Get path to mock data directory."""
        mock_path = self.get('development.mock_data_path', 'data/')
        if not os.path.isabs(mock_path):
            # Make relative to project root
            project_root = Path(__file__).parent.parent.parent
            return project_root / mock_path
        return Path(mock_path)


# Global configuration instance
config = Config()
