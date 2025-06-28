"""
Concrete implementation of LLM provider using llama-cpp-python.
Implements the ILLMProvider interface.
"""
import os
import time
import logging
from typing import Dict, Any, Optional
from llama_cpp import Llama

from .llm_interface import ILLMProvider
from config import get_config


logger = logging.getLogger(__name__)


class LlamaCppProvider(ILLMProvider):
    """LLM provider implementation using llama-cpp-python."""
    
    def __init__(self):
        self.config = get_config()
        self.llm: Optional[Llama] = None
        self._model_loaded = False
        
    def load_model(self) -> bool:
        """Load the Llama model."""
        try:
            if self._model_loaded and self.llm:
                return True
                
            model_config = self.config.model
            
            if not os.path.exists(model_config.model_path):
                logger.error(f"Model file not found: {model_config.model_path}")
                return False
            
            logger.info("Loading Llama model... This may take a moment.")
            
            self.llm = Llama(
                model_path=model_config.model_path,
                n_ctx=model_config.n_ctx,
                n_threads=model_config.n_threads,
                n_batch=model_config.n_batch,
                n_gpu_layers=model_config.n_gpu_layers,
                use_mmap=model_config.use_mmap,
                use_mlock=model_config.use_mlock,
                verbose=model_config.verbose
            )
            
            self._model_loaded = True
            logger.info("Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._model_loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model_loaded and self.llm is not None
    
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        stop_tokens: list,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from the Llama model."""
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            start_time = time.time()
            
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop=stop_tokens,
                echo=False,
                repeat_penalty=kwargs.get('repeat_penalty', 1.05),
                stream=False
            )
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'response': response,
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'success': False,
                'response': None,
                'processing_time': 0,
                'error': str(e)
            }


class ModelDownloader:
    """Handles model downloading and setup."""
    
    def __init__(self):
        self.config = get_config()
    
    def download_model_if_needed(self) -> Optional[str]:
        """Download the model if it doesn't exist locally."""
        model_config = self.config.model
        
        if os.path.exists(model_config.model_path):
            logger.info(f"Model found at: {model_config.model_path}")
            return model_config.model_path
        
        logger.info("Model not found locally. Downloading...")
        
        try:
            from huggingface_hub import hf_hub_download
            
            # Create models directory if it doesn't exist
            os.makedirs("./models", exist_ok=True)
            
            # Set cache directory to avoid C: drive space issues
            cache_dir = os.path.abspath(model_config.cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
            
            logger.info(f"Downloading {model_config.model_filename} (~4.1 GB). This may take a while...")
            logger.info(f"Downloading to: {os.path.abspath('./models')}")
            
            # Download directly to models folder
            downloaded_path = hf_hub_download(
                repo_id=model_config.model_repo,
                filename=model_config.model_filename,
                cache_dir=cache_dir,
                local_files_only=False,
                force_download=False
            )
            
            # Copy to final location if needed
            if downloaded_path != model_config.model_path:
                import shutil
                logger.info("Moving model to final location...")
                shutil.copy2(downloaded_path, model_config.model_path)
            
            logger.info(f"Model downloaded successfully to: {os.path.abspath(model_config.model_path)}")
            return model_config.model_path
            
        except ImportError:
            logger.error("huggingface_hub not installed. Please install it with: pip install huggingface_hub")
            self._print_manual_download_instructions()
            return None
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            self._print_manual_download_instructions()
            return None
    
    def _print_manual_download_instructions(self):
        """Print manual download instructions."""
        model_config = self.config.model
        logger.info("Or download the model manually from:")
        logger.info(f"https://huggingface.co/{model_config.model_repo}/resolve/main/{model_config.model_filename}")


def create_llm_provider() -> LlamaCppProvider:
    """Factory function to create and initialize LLM provider."""
    provider = LlamaCppProvider()
    
    # Download model if needed
    downloader = ModelDownloader()
    model_path = downloader.download_model_if_needed()
    
    if model_path and provider.load_model():
        return provider
    else:
        logger.warning("LLM provider not available. Running in fallback mode.")
        return provider 