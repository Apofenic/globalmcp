"""
Config Loader - Manages MCP configuration files
"""
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loader for MCP configuration files including Jira, GitHub, and filesystem configs"""
    
    def __init__(self):
        self.configs: Dict[str, Any] = {}
        self.vscode_config_path = Path.cwd() / ".vscode" / "mcp.json"
        
    async def load_configs(self, config_path: Optional[str] = None):
        """Load all MCP configurations"""
        if config_path:
            self.vscode_config_path = Path(config_path)
        
        try:
            # Load VS Code MCP configuration
            await self._load_vscode_config()
            
            # Load additional configuration files
            await self._load_service_configs()
            
            logger.info("MCP configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load MCP configurations: {e}")
            # Create default config if none exists
            await self._create_default_config()
    
    async def _load_vscode_config(self):
        """Load VS Code MCP configuration file"""
        if self.vscode_config_path.exists():
            try:
                with open(self.vscode_config_path, 'r') as f:
                    vscode_config = json.load(f)
                
                self.configs["vscode"] = vscode_config
                logger.info(f"Loaded VS Code MCP config from {self.vscode_config_path}")
                
            except Exception as e:
                logger.error(f"Failed to load VS Code config: {e}")
                raise
        else:
            logger.info("No VS Code MCP config found, will create default")
    
    async def _load_service_configs(self):
        """Load service-specific configurations"""
        config_dir = Path.cwd() / "config"
        
        # Load individual service configs
        service_configs = [
            "jira_config.json",
            "github_config.json", 
            "filesystem_config.json",
            "model_registry.json"
        ]
        
        for config_file in service_configs:
            config_path = config_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    
                    service_name = config_file.replace("_config.json", "").replace(".json", "")
                    self.configs[service_name] = config_data
                    logger.info(f"Loaded {service_name} config")
                    
                except Exception as e:
                    logger.warning(f"Failed to load {config_file}: {e}")
    
    async def _create_default_config(self):
        """Create default MCP configuration files"""
        logger.info("Creating default MCP configuration")
        
        # Create .vscode directory if it doesn't exist
        self.vscode_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default VS Code MCP configuration
        default_vscode_config = {
            "mcpServers": {
                "globalmcp": {
                    "command": "python",
                    "args": ["-m", "mcp.server"],
                    "env": {
                        "MCP_SERVER_HOST": "localhost",
                        "MCP_SERVER_PORT": "8000"
                    }
                },
                "jira": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-jira"],
                    "env": {
                        "JIRA_URL": "${JIRA_URL}",
                        "JIRA_USERNAME": "${JIRA_USERNAME}",
                        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
                    }
                },
                "github": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
                    }
                },
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
                    "env": {}
                }
            }
        }
        
        # Save VS Code config
        with open(self.vscode_config_path, 'w') as f:
            json.dump(default_vscode_config, f, indent=2)
        
        self.configs["vscode"] = default_vscode_config
        
        # Create config directory and service configs
        await self._create_service_configs()
        
        logger.info(f"Created default MCP config at {self.vscode_config_path}")
    
    async def _create_service_configs(self):
        """Create default service configuration files"""
        config_dir = Path.cwd() / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Jira configuration
        jira_config = {
            "url": "${JIRA_URL}",
            "username": "${JIRA_USERNAME}",
            "api_token": "${JIRA_API_TOKEN}",
            "project_key": "DEV",
            "default_issue_type": "Task"
        }
        
        # GitHub configuration  
        github_config = {
            "personal_access_token": "${GITHUB_PERSONAL_ACCESS_TOKEN}",
            "default_owner": "${GITHUB_OWNER}",
            "default_repo": "${GITHUB_REPO}"
        }
        
        # Filesystem configuration
        filesystem_config = {
            "allowed_paths": [
                "/Users/anthonylubrino/globalmcp",
                "/tmp/mcp_workspace"
            ],
            "readonly": False,
            "max_file_size_mb": 10
        }
        
        # Model registry configuration
        model_registry_config = {
            "models": {
                "phi3": "ollama://phi3",
                "mistral": "ollama://mistral",
                "llama3": "ollama://llama3"
            },
            "complexity_mapping": {
                "simple": "ollama://phi3",
                "moderate": "ollama://mistral", 
                "complex": "ollama://llama3"
            }
        }
        
        configs_to_create = [
            ("jira_config.json", jira_config),
            ("github_config.json", github_config),
            ("filesystem_config.json", filesystem_config),
            ("model_registry.json", model_registry_config)
        ]
        
        for filename, config_data in configs_to_create:
            config_path = config_dir / filename
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Store in configs dict
            service_name = filename.replace("_config.json", "").replace(".json", "")
            self.configs[service_name] = config_data
        
        logger.info("Created default service configuration files")
    
    def get_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific service"""
        return self.configs.get(service_name)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all loaded configurations"""
        return self.configs.copy()
    
    async def update_config(self, service_name: str, config_data: Dict[str, Any]):
        """Update configuration for specific service"""
        self.configs[service_name] = config_data
        
        # Save to file if it's a known service
        if service_name == "vscode":
            config_path = self.vscode_config_path
        else:
            config_path = Path.cwd() / "config" / f"{service_name}_config.json"
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Updated {service_name} configuration")
