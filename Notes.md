# Notes: Lazy Initialization & Dependency Injection

## 1. Lazy Initialization Pattern

### Definition
**Lazy Initialization** delays the creation of an object until it's actually needed, rather than creating it immediately when the program starts.

### Example from `clipboard_service.py`

```python
# Global variable starts as None (not created yet)
_clipboard_service: Optional[ClipboardService] = None

def get_clipboard_service() -> ClipboardService:
    """Get the singleton clipboard service instance."""
    global _clipboard_service
    if _clipboard_service is None:              # Check if not created
        _clipboard_service = ClipboardService()  # Create only when needed
    return _clipboard_service
```

### What's happening:
1. **Module load**: `_clipboard_service = None` (no object created)
2. **First call**: `get_clipboard_service()` → creates `ClipboardService()`
3. **Subsequent calls**: Returns the same instance (singleton)

### Benefits:
- **Memory efficiency**: Object only created if actually used
- **Faster startup**: Module loads quickly without expensive object creation
- **Error handling**: If creation fails, it fails when used, not at import
- **Testing**: Easier to replace/mock before first use

### Alternative (Eager Initialization):
```python
# Object created immediately when module loads
_clipboard_service = ClipboardService()  # Created right away!

def get_clipboard_service() -> ClipboardService:
    return _clipboard_service  # Always exists
```

---

## 2. Dependency Injection Pattern

### Definition
**Dependency Injection** provides dependencies (objects that a class needs) from the outside, rather than creating them internally.

### Example from `clipboard_service.py`

```python
class ClipboardService:
    def __init__(self, controller: Optional[Controller] = None):
        # Accept controller from outside OR create default
        self.controller = controller or Controller()
```

### What's happening:
1. **Constructor accepts dependency**: `controller` parameter
2. **Flexible creation**: Can inject custom controller or use default
3. **Loose coupling**: Class doesn't hardcode specific `Controller()` creation

### Usage Examples:

**Production (default):**
```python
service = ClipboardService()  # Uses Controller() internally
```

**Testing (injected):**
```python
mock_controller = Mock()
service = ClipboardService(controller=mock_controller)  # Inject fake controller
```

**Custom (injected):**
```python
custom_controller = CustomController(delay=0.5)
service = ClipboardService(controller=custom_controller)  # Inject custom controller
```

### Benefits:
- **Testability**: Can inject mock objects for testing
- **Flexibility**: Can use different implementations
- **Loose coupling**: Class doesn't depend on specific implementations
- **Error isolation**: Dependency creation failures handled outside class

### Alternative (Direct Creation):
```python
class ClipboardService:
    def __init__(self):
        self.controller = Controller()  # Hardcoded dependency!
        # ❌ Can't test easily
        # ❌ Can't customize
        # ❌ Tightly coupled
```

---

## 3. How They Work Together in `clipboard_service.py`

### The Complete Pattern:
```python
# 1. Lazy singleton variable
_clipboard_service: Optional[ClipboardService] = None

# 2. Class with dependency injection
class ClipboardService:
    def __init__(self, controller: Optional[Controller] = None):
        self.controller = controller or Controller()

# 3. Lazy factory function
def get_clipboard_service() -> ClipboardService:
    global _clipboard_service
    if _clipboard_service is None:
        _clipboard_service = ClipboardService()  # Could inject controller here
    return _clipboard_service
```

### Real-world Usage:

**Normal usage:**
```python
# Lazy: Only creates ClipboardService when first called
clipboard = get_clipboard_service()
clipboard.copy_to_clipboard()
```

**Testing:**
```python
# Reset singleton for testing
_clipboard_service = None

# Create with mock dependency
mock_controller = Mock()
test_service = ClipboardService(controller=mock_controller)

# Or modify the singleton factory for testing
def get_test_clipboard_service():
    return ClipboardService(controller=Mock())
```

---

## 4. Key Takeaways

### Lazy Initialization:
- **When**: Use when object creation is expensive or might not be needed
- **Benefits**: Better performance, memory efficiency, flexible testing
- **Pattern**: Check if None → Create if needed → Return existing

### Dependency Injection:
- **When**: Use when class needs external objects/services
- **Benefits**: Better testing, flexibility, loose coupling
- **Pattern**: Accept dependency in constructor → Use provided or create default

### Together they enable:
- **Flexible architecture**: Easy to customize and extend
- **Testable code**: Can inject mocks and control creation timing
- **Efficient resource usage**: Create only what you need, when you need it
- **Maintainable code**: Clear separation of concerns and responsibilities

---

## 5. Mock Objects and Mock() - Testing Made Easy

### Definition
**Mock objects** are fake objects used in testing that pretend to be real objects. `Mock()` from Python's `unittest.mock` creates these fake objects dynamically.

### How Mock Works (The Magic!)

Mock doesn't need to know what methods the real object has. It creates methods **on-the-fly** when you try to use them:

```python
from unittest.mock import Mock

# Create a completely empty mock object
mock_controller = Mock()

# Mock doesn't have press() method yet...
print(hasattr(mock_controller, 'press'))  # False

# But the moment you call it, Mock creates it!
mock_controller.press(Key.ctrl)  # Method created automatically!
print(hasattr(mock_controller, 'press'))  # True now!

# Same with any method name you try to use
mock_controller.release('c')     # Creates release() method
mock_controller.any_method()     # Creates any_method() method
mock_controller.dance()          # Creates dance() method
```

### Example: Testing `clipboard_service.py` with Mock

**The Real ClipboardService (what we want to test):**
```python
class ClipboardService:
    def __init__(self, controller: Optional[Controller] = None):
        self.controller = controller or Controller()
    
    def copy_to_clipboard(self):
        # This would actually press keyboard keys!
        self.controller.press(Key.ctrl)
        self.controller.press('c')
        self.controller.release('c')
        self.controller.release(Key.ctrl)
```

**Testing WITHOUT Mock (❌ Problems):**
```python
# This would actually press Ctrl+C on your keyboard!
service = ClipboardService()  # Uses real Controller()
service.copy_to_clipboard()   # Actually presses keys! 😱
# Your clipboard gets modified during testing!
```

**Testing WITH Mock (✅ Safe):**
```python
from unittest.mock import Mock

# Create fake controller
mock_controller = Mock()

# Inject the fake controller
service = ClipboardService(controller=mock_controller)

# Now test safely - no real keyboard interaction!
service.copy_to_clipboard()

# Verify the right methods were called
mock_controller.press.assert_called_with(Key.ctrl)
mock_controller.press.assert_called_with('c')
mock_controller.release.assert_called_with('c')
mock_controller.release.assert_called_with(Key.ctrl)
```

### What Mock Records

Mock objects remember everything that happens to them:

```python
mock_controller = Mock()
service = ClipboardService(controller=mock_controller)
service.copy_to_clipboard()

# Check what methods were called
print(mock_controller.method_calls)
# Output: [call.press(<Key.ctrl: 65508>), call.press('c'), call.release('c'), call.release(<Key.ctrl: 65508>)]

# Check how many times press() was called
print(mock_controller.press.call_count)  # 2

# Check the arguments of specific calls
print(mock_controller.press.call_args_list)
# Output: [call(<Key.ctrl: 65508>), call('c')]
```

### Real Test Example

```python
import unittest
from unittest.mock import Mock
from pynput.keyboard import Key

class TestClipboardService(unittest.TestCase):
    def test_copy_to_clipboard(self):
        # Arrange: Create mock and service
        mock_controller = Mock()
        service = ClipboardService(controller=mock_controller)
        
        # Act: Call the method we want to test
        service.copy_to_clipboard()
        
        # Assert: Verify the right keys were pressed in right order
        expected_calls = [
            mock_controller.press.call(Key.ctrl),
            mock_controller.press.call('c'),
            mock_controller.release.call('c'),
            mock_controller.release.call(Key.ctrl)
        ]
        mock_controller.assert_has_calls(expected_calls, any_order=False)
    
    def test_paste_from_clipboard(self):
        mock_controller = Mock()
        service = ClipboardService(controller=mock_controller)
        
        service.paste_from_clipboard()
        
        # Verify Ctrl+V was pressed
        mock_controller.press.assert_any_call(Key.ctrl)
        mock_controller.press.assert_any_call('v')
```

### Why This Works So Well with Dependency Injection

**The Perfect Combination:**
1. **Dependency Injection** makes it possible to inject Mock objects
2. **Mock objects** make testing safe and controllable
3. **Together** they enable comprehensive testing without side effects

```python
# Production: Real dependencies
clipboard = ClipboardService()  # Uses real Controller
clipboard.copy_to_clipboard()   # Actually copies text

# Testing: Mock dependencies  
mock_controller = Mock()
clipboard = ClipboardService(controller=mock_controller)  # Uses fake Controller
clipboard.copy_to_clipboard()   # Safe! No real copying
```

### Key Benefits of Mock Objects:

- **Safety**: No real side effects during testing
- **Control**: You control what the mock returns
- **Verification**: You can verify what methods were called
- **Isolation**: Test your code without external dependencies
- **Speed**: Much faster than real objects
- **Reliability**: Tests don't fail due to external factors

### Mock vs Real Object Summary:

| Aspect | Real Controller | Mock Controller |
|--------|----------------|-----------------|
| **Keyboard interaction** | Actually presses keys | No real key presses |
| **Testing safety** | Can interfere with system | Completely safe |
| **Speed** | Slower (real hardware) | Fast (in-memory only) |
| **Verification** | Can't verify calls | Records all interactions |
| **Dependencies** | Needs real keyboard | No external dependencies |
| **Reliability** | Can fail due to system state | Always predictable | 



# Typify - Production Ready

A modular, scalable grammar correction application built with SOLID principles and dependency injection.

## 🏗️ Architecture

The application follows clean architecture principles with clear separation of concerns:

```
Grammar_Clone/
├── config.py                 # Configuration management
├── logging_config.py         # Centralized logging setup
├── main.py                   # Production-ready main application
├── main.py                  # Original application (kept for reference)
├── models/                  # Domain models and interfaces
│   ├── __init__.py
│   ├── llm_interface.py     # Abstract interfaces (SOLID - ISP, DIP)
│   └── llama_provider.py    # Concrete LLM implementation
├── services/                # Business logic and services
│   ├── __init__.py
│   ├── cache_service.py     # Caching with LRU strategy
│   ├── clipboard_service.py # Clipboard operations
│   ├── hotkey_service.py    # Global hotkey management
│   └── text_processors.py  # Text processing implementations
├── requirements.txt
└── logs/                   # Application logs (auto-created)
```

## 🎯 SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- **`CacheService`**: Only handles caching operations
- **`ClipboardService`**: Only handles clipboard operations  
- **`HotkeyService`**: Only manages global hotkeys
- **`GrammarCorrector`**: Only handles grammar correction
- **`TextSummarizer`**: Only handles text summarization
- **`ToneChanger`**: Only handles tone modification

### Open/Closed Principle (OCP)
- New text processors can be added by implementing `ITextProcessor`
- New LLM providers can be added by implementing `ILLMProvider`
- New hotkey handlers can be registered without modifying existing code

### Liskov Substitution Principle (LSP)
- All text processors implement the same interface and can be substituted
- Any LLM provider implementing `ILLMProvider` can replace the current one

### Interface Segregation Principle (ISP)
- Specific interfaces for each operation: `IGrammarCorrector`, `ITextSummarizer`, `IToneChanger`
- Clients only depend on interfaces they need

### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions (`ILLMProvider`, `ITextProcessor`)
- Dependencies are injected, not hardcoded
- Easy to mock for testing

## 🚀 Features

- **Grammar Correction**: Fix typos, grammar, and punctuation errors
- **Text Summarization**: Create concise summaries of selected text
- **Tone Modification**: Change text tone to formal/professional
- **Intelligent Caching**: LRU cache with configurable limits
- **Global Hotkeys**: System-wide keyboard shortcuts
- **Robust Logging**: Structured logging with rotation
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Graceful error handling and recovery

## 🎮 Hotkeys

| Hotkey | Function |
|--------|----------|
| `F9` | Fix grammar for current line |
| `F10` | Fix grammar for selected text |
| `F8` | Summarize selected text |
| `F7` | Change tone to formal |
| `Ctrl+Shift+E` | Exit application |

## 🛠️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Grammar_Clone
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the production application**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

Configure the application via environment variables or modify `config.py`:

### Model Configuration
```bash
export MODEL_THREADS=16          # Number of CPU threads
export MODEL_GPU_LAYERS=35       # GPU layers (if GPU available)
export MODEL_PATH="/path/to/model.gguf"  # Custom model path
```

### Performance Configuration
```bash
export CACHE_SIZE=200            # Maximum cache entries
```

### Example Configuration
```python
# config.py modifications
CONFIG.model.n_threads = 16
CONFIG.generation.grammar_temperature = 0.2
CONFIG.cache.max_cache_size = 200
```

## 📊 Monitoring & Logging

The application provides comprehensive logging and monitoring:

### Log Files
- **Console**: Real-time application status
- **File**: Detailed logs in `logs/grammar_clone.log`
- **Rotation**: Automatic log rotation (10MB, 5 backups)

### Cache Statistics
Monitor cache performance through logs:
```
Cache statistics: {
  'grammar_cache_size': 45,
  'summary_cache_size': 12,
  'tone_cache_size': 8
}
```

### Performance Metrics
All operations include timing information:
```
Grammar correction took: 2.34 seconds
Summarization took: 1.87 seconds
```

## 🧪 Testing & Development

### Adding New Text Processors

1. **Create the processor**
   ```python
   class CustomProcessor(BaseTextProcessor, ITextProcessor):
       def process_text(self, text: str, **kwargs) -> TextProcessingResult:
           # Implementation here
           pass
   ```

2. **Register with dependency injection**
   ```python
   custom_processor = CustomProcessor(
       llm_provider=llm_provider,
       cache_service=cache_service
   )
   ```

### Adding New LLM Providers

1. **Implement the interface**
   ```python
   class CustomLLMProvider(ILLMProvider):
       def generate_response(self, prompt, **kwargs):
           # Implementation here
           pass
   ```

2. **Replace in factory function**
   ```python
   def create_custom_llm_provider():
       return CustomLLMProvider()
   ```

### Adding New Hotkeys

1. **Create handler function**
   ```python
   def custom_handler():
       # Handler implementation
       pass
   ```

2. **Register with hotkey service**
   ```python
   hotkey_service.register_handler('<key>', custom_handler)
   ```

## 🔧 Troubleshooting

### Common Issues

1. **Model Download Fails**
   - Check internet connection
   - Verify disk space (model is ~4.1GB)
   - Check `logs/grammar_clone.log` for details

2. **Hotkeys Not Working**
   - Run as administrator (Windows)
   - Check if other applications are using the same hotkeys
   - Verify hotkey service initialization in logs

3. **Performance Issues**
   - Adjust `MODEL_THREADS` environment variable
   - Reduce cache size if memory is limited
   - Consider GPU acceleration if available

### Debug Mode
Enable debug logging:
```python
setup_logging(level="DEBUG")
```

## 📈 Scalability Features

- **Thread-Safe Caching**: Multiple operations can run concurrently
- **Memory Management**: Automatic cache cleanup and size limits
- **Resource Optimization**: Configurable model parameters
- **Modular Design**: Easy to add new features without breaking existing code
- **Configuration Management**: Environment-based configuration for different deployments

## 🔄 Migration from Original

To migrate from the original `main.py`:

1. **Backup your current setup**
2. **Update imports** if you've customized the code
3. **Run the new version**: `python main.py`
4. **Configure** via environment variables or `config.py`

The new version maintains all original functionality while providing better structure and extensibility.

## 🤝 Contributing

When contributing:
1. Follow SOLID principles
2. Add appropriate logging
3. Include error handling
4. Update configuration if needed
5. Maintain interface compatibility

## 📄 License

[Your License Here] 