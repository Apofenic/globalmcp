"""
Routing Service - Prompt complexity classification and model routing
"""
import re
import asyncio
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RoutingService:
    """Service for classifying prompt complexity and routing to appropriate models"""
    
    def __init__(self):
        self.complexity_patterns = {
            "simple": [
                r"\b(fix|format|indent|rename|import)\b",
                r"\b(add|remove|delete)\s+\w+\s*(comment|log|print)\b",
                r"\bgenerate\s+(getter|setter|constructor)\b",
                r"\b(what|where|when|how)\s+is\b"
            ],
            "moderate": [
                r"\b(refactor|optimize|implement|create)\b",
                r"\b(add|write|build)\s+(function|method|class)\b",
                r"\b(test|debug|fix)\s+(bug|issue|error)\b",
                r"\b(explain|describe|analyze)\b.*\b(code|algorithm|pattern)\b"
            ],
            "complex": [
                r"\b(architect|design|migrate|transform)\b",
                r"\b(integrate|connect|sync)\s+.*\b(api|database|service)\b",
                r"\b(performance|security|scalability)\s+(issue|concern|optimization)\b",
                r"\b(multi|cross)[-\s](platform|service|thread|process)\b",
                r"\b(deploy|ci\/cd|infrastructure|docker|kubernetes)\b"
            ]
        }
        
    async def classify_complexity(
        self, 
        prompt: str, 
        context: str = ""
    ) -> str:
        """
        Classify prompt complexity based on patterns and content analysis
        
        Args:
            prompt: The prompt to classify
            context: Additional context for classification
            
        Returns:
            Complexity level: "simple", "moderate", or "complex"
        """
        full_text = f"{prompt} {context}".lower()
        
        # Count pattern matches for each complexity level
        complexity_scores = {}
        
        for complexity, patterns in self.complexity_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, full_text, re.IGNORECASE))
                score += matches
            complexity_scores[complexity] = score
        
        # Add heuristic scoring
        complexity_scores = self._add_heuristic_scores(full_text, complexity_scores)
        
        # Determine final complexity
        if complexity_scores["complex"] > 0:
            classification = "complex"
        elif complexity_scores["moderate"] > complexity_scores["simple"]:
            classification = "moderate"
        else:
            classification = "simple"
            
        logger.info(f"Classified prompt as '{classification}' (scores: {complexity_scores})")
        return classification
    
    def _add_heuristic_scores(
        self, 
        text: str, 
        scores: Dict[str, int]
    ) -> Dict[str, int]:
        """Add heuristic-based scoring to complexity classification"""
        
        # Length-based heuristics
        word_count = len(text.split())
        if word_count > 100:
            scores["complex"] += 2
        elif word_count > 50:
            scores["moderate"] += 1
        else:
            scores["simple"] += 1
            
        # Technical keyword density
        technical_keywords = [
            "algorithm", "architecture", "framework", "library", "protocol",
            "asynchronous", "concurrent", "distributed", "microservice",
            "authentication", "authorization", "encryption", "validation"
        ]
        
        tech_score = sum(1 for keyword in technical_keywords if keyword in text)
        if tech_score >= 3:
            scores["complex"] += tech_score
        elif tech_score >= 1:
            scores["moderate"] += tech_score
            
        # Code complexity indicators
        code_indicators = ["class", "function", "method", "interface", "enum", "struct"]
        code_score = sum(1 for indicator in code_indicators if indicator in text)
        
        if code_score >= 3:
            scores["moderate"] += 1
        elif code_score >= 5:
            scores["complex"] += 1
            
        return scores
    
    async def generate_response(
        self,
        prompt: str,
        model_endpoint: str,
        context: str = "",
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response using the specified model endpoint
        
        Args:
            prompt: The prompt to process
            model_endpoint: Model endpoint URL or identifier
            context: Additional context
            max_tokens: Maximum tokens for response
            
        Returns:
            Generated response text
        """
        try:
            # If model_endpoint is an Ollama model identifier
            if model_endpoint.startswith("ollama://"):
                return await self._generate_ollama_response(
                    prompt, model_endpoint, context, max_tokens
                )
            # If it's a direct HTTP endpoint
            elif model_endpoint.startswith("http"):
                return await self._generate_http_response(
                    prompt, model_endpoint, context, max_tokens
                )
            else:
                # Mock response for unsupported endpoints
                logger.warning(f"Unsupported model endpoint: {model_endpoint}")
                return await self._generate_mock_response(prompt, model_endpoint)
                
        except Exception as e:
            logger.error(f"Error generating response with {model_endpoint}: {e}")
            return f"Error: Failed to generate response using {model_endpoint}"
    
    async def _generate_ollama_response(
        self,
        prompt: str,
        model_endpoint: str,
        context: str,
        max_tokens: Optional[int]
    ) -> str:
        """Generate response using Ollama API"""
        model_name = model_endpoint.replace("ollama://", "")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": f"{context}\n\n{prompt}" if context else prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens or 512
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No response generated")
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return f"Ollama API error: {response.status_code}"
                    
        except httpx.ConnectError:
            logger.warning("Ollama not available, returning mock response")
            return await self._generate_mock_response(prompt, model_endpoint)
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return f"Ollama request failed: {e}"
    
    async def _generate_http_response(
        self,
        prompt: str,
        model_endpoint: str,
        context: str,
        max_tokens: Optional[int]
    ) -> str:
        """Generate response using generic HTTP endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    model_endpoint,
                    json={
                        "prompt": f"{context}\n\n{prompt}" if context else prompt,
                        "max_tokens": max_tokens or 512
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", result.get("text", "No response"))
                else:
                    return f"HTTP API error: {response.status_code}"
                    
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            return f"HTTP request failed: {e}"
    
    async def _generate_mock_response(self, prompt: str, model_endpoint: str) -> str:
        """Generate mock response for testing/demo purposes"""
        complexity = await self.classify_complexity(prompt)
        
        mock_responses = {
            "simple": f"[MOCK SIMPLE] Processing: {prompt[:50]}...",
            "moderate": f"[MOCK MODERATE] Analyzing and implementing: {prompt[:50]}...",
            "complex": f"[MOCK COMPLEX] Architecting solution for: {prompt[:50]}..."
        }
        
        return mock_responses.get(complexity, f"[MOCK] Processed via {model_endpoint}")
