"""
Model Registry - Manages LLM endpoints and routing configuration
"""
from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Registry for managing model endpoints and routing configuration"""
    
    def __init__(self):
        self.models: Dict[str, str] = {}
        self.complexity_mapping: Dict[str, str] = {}
        self.default_models = {
            "simple": "ollama://phi3",
            "moderate": "ollama://mistral",
            "complex": "ollama://llama3"
        }
        
    async def initialize(self, config_path: Optional[str] = None):
        """Initialize model registry with configuration"""
        if config_path is None:
            config_path = Path.cwd() / "config" / "model_registry.json"
        
        try:
            if Path(config_path).exists():
                await self._load_config(config_path)
            else:
                logger.info("No model registry config found, using defaults")
                await self._use_defaults()
        except Exception as e:
            logger.error(f"Failed to initialize model registry: {e}")
            await self._use_defaults()
    
    async def _load_config(self, config_path: str):
        """Load model configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.models = config.get("models", {})
            self.complexity_mapping = config.get("complexity_mapping", {})
            
            logger.info(f"Loaded model registry from {config_path}")
            logger.info(f"Available models: {list(self.models.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load model config: {e}")
            raise
    
    async def _use_defaults(self):
        """Use default model configuration"""
        self.models = {
            "phi3": "ollama://phi3",
            "mistral": "ollama://mistral", 
            "llama3": "ollama://llama3",
            "mock-simple": "mock://simple",
            "mock-moderate": "mock://moderate",
            "mock-complex": "mock://complex"
        }
        
        self.complexity_mapping = self.default_models.copy()
        
        logger.info("Using default model registry configuration")
    
    def get_model_for_complexity(self, complexity: str) -> str:
        """Get model endpoint for given complexity level"""
        model_endpoint = self.complexity_mapping.get(complexity)
        
        if not model_endpoint:
            # Fallback to default if not configured
            model_endpoint = self.default_models.get(complexity, "mock://default")
            logger.warning(f"No model configured for complexity '{complexity}', using fallback")
        
        logger.info(f"Routing {complexity} complexity to {model_endpoint}")
        return model_endpoint
    
    def register_model(self, name: str, endpoint: str):
        """Register a new model endpoint"""
        self.models[name] = endpoint
        logger.info(f"Registered model '{name}' -> '{endpoint}'")
    
    def set_complexity_mapping(self, complexity: str, model_name: str):
        """Set model for specific complexity level"""
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not registered")
        
        self.complexity_mapping[complexity] = self.models[model_name]
        logger.info(f"Mapped complexity '{complexity}' to model '{model_name}'")
    
    def get_available_models(self) -> Dict[str, str]:
        """Get all available models"""
        return self.models.copy()
    
    def get_complexity_mappings(self) -> Dict[str, str]:
        """Get current complexity to model mappings"""
        return self.complexity_mapping.copy()
    
    async def save_config(self, config_path: str):
        """Save current configuration to file"""
        config = {
            "models": self.models,
            "complexity_mapping": self.complexity_mapping
        }
        
        # Ensure directory exists
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved model registry to {config_path}")
