"""
Configuration settings for the Typify application.
Centralizes all configurable parameters for easy maintenance.
"""
import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ModelConfig:
    """Model-related configuration."""
    model_repo: str = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
    model_filename: str = "mistral-7b-instruct-v0.2.Q4_K_S.gguf"
    model_path: str = "./models/mistral-7b-instruct-v0.2.Q4_K_S.gguf"
    cache_dir: str = "./models/.cache"
    
    # Performance settings
    n_ctx: int = 1024
    n_threads: int = 12
    n_batch: int = 1024
    n_gpu_layers: int = 0
    use_mmap: bool = True
    use_mlock: bool = False
    verbose: bool = False


@dataclass
class GenerationConfig:
    """Text generation configuration."""
    # Grammar correction
    grammar_max_tokens_multiplier: int = 4
    grammar_min_tokens: int = 100
    grammar_temperature: float = 0.3
    grammar_top_p: float = 0.9
    grammar_top_k: int = 40
    grammar_repeat_penalty: float = 1.05
    
    # Summarization
    summary_max_tokens: int = 200
    summary_min_tokens: int = 100
    summary_temperature: float = 0.2
    summary_top_p: float = 0.8
    summary_top_k: int = 40
    summary_repeat_penalty: float = 1.05
    
    # Tone change
    tone_max_tokens_multiplier: int = 2
    tone_min_tokens: int = 150
    tone_temperature: float = 0.2
    tone_top_p: float = 0.9
    tone_top_k: int = 40
    tone_repeat_penalty: float = 1.05


@dataclass
class CacheConfig:
    """Cache configuration."""
    max_cache_size: int = 100
    cleanup_batch_size: int = 20


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""
    grammar_fix_line: str = '<120>'  # F9
    grammar_fix_selection: str = '<121>'  # F10
    summarize: str = '<119>'  # F8
    change_tone: str = '<118>'  # F7
    exit_app: str = '<ctrl>+<shift>+e'


@dataclass
class AppConfig:
    """Main application configuration."""
    model: ModelConfig = None
    generation: GenerationConfig = None
    cache: CacheConfig = None
    hotkeys: HotkeyConfig = None
    
    # Environment settings
    disable_symlink_warning: bool = True
    
    # Stop tokens for different tasks
    stop_tokens: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.model is None:
            self.model = ModelConfig()
        if self.generation is None:
            self.generation = GenerationConfig()
        if self.cache is None:
            self.cache = CacheConfig()
        if self.hotkeys is None:
            self.hotkeys = HotkeyConfig()
        if self.stop_tokens is None:
            self.stop_tokens = {
                'default': ["[INST]", "</s>", "[/INST]"],
                'summarize': ["[INST]", "</s>", "[/INST]"],
                'tone_change': ["[INST]", "</s>", "[/INST]"],
            }


# Global configuration instance
CONFIG = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return CONFIG


def update_config_from_env():
    """Update configuration from environment variables."""
    config = get_config()
    
    # Model settings
    if os.getenv('MODEL_THREADS'):
        config.model.n_threads = int(os.getenv('MODEL_THREADS'))
    
    if os.getenv('MODEL_GPU_LAYERS'):
        config.model.n_gpu_layers = int(os.getenv('MODEL_GPU_LAYERS'))
    
    if os.getenv('MODEL_PATH'):
        config.model.model_path = os.getenv('MODEL_PATH')
    
    # Performance settings
    if os.getenv('CACHE_SIZE'):
        config.cache.max_cache_size = int(os.getenv('CACHE_SIZE'))


# Apply environment overrides
update_config_from_env() 