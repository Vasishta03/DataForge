import ollama
import logging
from typing import Dict, Any

class MistralHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model_name = config.get('model_name', 'mistral')
        self.max_tokens = config.get('max_tokens', 2000)
        self.temperature = config.get('temperature', 0.7)
        self._verify_model()
    
    def _verify_model(self):
        """Check if Mistral model is available locally"""
        try:
            response = ollama.list()
            models = response.get('models', [])
            available = []
            for m in models:
                # Ollama's model dicts may have 'name' or 'model' as key
                model_name = m.get('name') or m.get('model')
                if model_name:
                    available.append(model_name.lower())
            
            self.logger.info(f"Available models: {available}")
            
            # Check for substring match (ollama model names can be like "mistral:latest")
            found = any(self.model_name in name for name in available)
            
            if not found:
                self.logger.warning(f"Model '{self.model_name}' not found. Attempting to pull...")
                self._pull_model()
            else:
                self.logger.info(f"Verified Ollama model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Model verification failed: {e}")
            raise
    
    def _pull_model(self):
        """Attempt to pull the model from Ollama"""
        try:
            self.logger.info(f"Pulling model: {self.model_name}")
            ollama.pull(self.model_name)
            self.logger.info(f"Successfully pulled model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to pull model: {e}")
            raise RuntimeError(f"Model '{self.model_name}' not available. Please run: ollama pull {self.model_name}")
    
    def generate(self, prompt: str) -> str:
        """Generate text using Ollama's API"""
        try:
            # Enhance prompt for CSV output
            enhanced_prompt = f"{prompt}\n\nIMPORTANT: Output ONLY CSV data with headers. No explanations, no markdown, no additional text."
            
            response = ollama.generate(
                model=self.model_name,
                prompt=enhanced_prompt,
                options={
                    'num_predict': self.max_tokens,
                    'temperature': self.temperature
                }
            )
            
            # Extract and clean CSV content
            return self._clean_csv_output(response.get('response', ''))
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            if "connection" in str(e).lower():
                raise ConnectionError("Ollama service not running. Please start with: ollama serve")
            raise
    
    def _clean_csv_output(self, output: str) -> str:
        """Extract clean CSV content from model output"""
        lines = output.strip().split('\n')
        csv_lines = []
        
        # Find first line that looks like a CSV header
        start_index = 0
        for i, line in enumerate(lines):
            if ',' in line and any(char.isalpha() for char in line):
                start_index = i
                break
        
        # Collect all CSV-like lines
        for line in lines[start_index:]:
            if ',' in line or any(char.isdigit() for char in line):
                csv_lines.append(line)
            else:
                break
                
        return '\n'.join(csv_lines)
    
    def close(self) -> None:
        """Clean up resources"""
        # Ollama manages its own resources
        pass
