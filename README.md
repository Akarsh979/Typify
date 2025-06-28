# Typify - Free Offline Typing Assistant

A powerful typing assistant inspired by Grammarly, designed to help you write better without any subscriptions, purchases, or internet connection. Typify runs completely offline on your local machine, providing instant grammar corrections, text summarization, and tone adjustments.

## 🌟 Why Typify?

**Inspired by Grammarly, but better:**
- ✅ **Completely FREE** - No subscriptions or hidden costs
- ✅ **100% OFFLINE** - Works without internet connection
- ✅ **Privacy First** - Your text never leaves your computer
- ✅ **No Account Required** - Start using immediately
- ✅ **System-wide** - Works in any application (Word, Browser, Notepad, etc.)

Unlike Grammarly's premium features that require expensive subscriptions, Typify gives you professional-grade writing assistance for free, while keeping your data completely private.

## 🚀 Features

### Grammar & Writing Assistance
- **Smart Grammar Correction** - Fix typos, punctuation, and grammar errors
- **Text Summarization** - Create concise summaries of long text
- **Tone Adjustment** - Convert casual text to professional tone
- **Real-time Processing** - Instant corrections as you type

### System Integration
- **Global Hotkeys** - Works in any application system-wide
- **Clipboard Integration** - Seamless text processing
- **Smart Caching** - Remembers recent corrections for faster processing
- **Background Operation** - Runs quietly in the system tray

## 🎮 How to Use

Once installed, use these keyboard shortcuts in any application:

| Hotkey | Function |
|--------|----------|
| `F9` | Fix grammar for current line |
| `F10` | Fix grammar for selected text |
| `F8` | Summarize selected text |
| `F7` | Change tone to formal/professional |
| `Ctrl+Shift+E` | Exit Typify |

## 🛠️ Installation & Setup

### Prerequisites
- Windows 10/11 (Linux and macOS support coming soon)
- Python 3.8 or higher
- At least 8GB RAM (16GB recommended)
- 4.5GB free disk space for the AI model

### Step 1: Download and Install

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/your-repo/typify.git
   cd typify
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/macOS
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Model Setup

The app will automatically download the required AI model on first run. This is a one-time process:

1. **First-time setup** (automatic)
   ```bash
   python main.py
   ```
   
2. **The app will:**
   - Download the Mistral-7B model (~4.1GB)
   - Set up the model in the `models/` folder
   - Initialize the configuration

### Step 3: Configuration (Optional)

You can customize Typify's behavior by modifying `config.py` or using environment variables:

#### Basic Configuration
```python
# config.py
MODEL_THREADS = 8           # CPU threads to use
CACHE_SIZE = 200           # Number of cached results
RESPONSE_TIMEOUT = 30      # Max processing time in seconds
```

#### Environment Variables
```bash
# For better performance
set MODEL_THREADS=16
set MODEL_GPU_LAYERS=35    # If you have a GPU

# For memory management
set CACHE_SIZE=100
```

### Step 4: Run Typify

```bash
python main.py
```

The app will:
- Start in the background
- Show a notification when ready
- Begin listening for hotkeys
- Create a system tray icon (coming soon)

## ⚡ Performance Optimization

### GPU Acceleration (Recommended)
If you have an NVIDIA GPU, you can significantly speed up Typify:

1. **Check GPU compatibility**
   ```bash
   python check_gpu.py
   ```

2. **Enable GPU acceleration**
   ```bash
   set MODEL_GPU_LAYERS=35
   python main.py
   ```

### Performance Tips
- **More RAM = Better Performance** - 16GB+ recommended
- **SSD Storage** - Faster model loading
- **Close Unnecessary Apps** - More resources for Typify
- **Adjust Thread Count** - Set `MODEL_THREADS` to match your CPU cores

## 🔧 Configuration Options

### Model Settings
```python
# config.py
MODEL_PATH = "./models/mistral-7b-instruct-v0.2.Q4_K_S.gguf"
MODEL_THREADS = 8          # Adjust based on your CPU
MODEL_GPU_LAYERS = 0       # Set to 35+ if you have a GPU
```

### Application Behavior
```python
CACHE_SIZE = 200           # Number of cached corrections
RESPONSE_TIMEOUT = 30      # Maximum wait time
AUTO_COPY = True          # Automatically copy corrected text
SHOW_NOTIFICATIONS = True  # Show completion notifications
```

### Hotkey Customization
```python
# Modify hotkeys in config.py
HOTKEYS = {
    'fix_line': 'f9',
    'fix_selection': 'f10',
    'summarize': 'f8',
    'change_tone': 'f7',
    'exit': 'ctrl+shift+e'
}
```

## 🚦 Quick Start Guide

1. **Install Python 3.8+**
2. **Download Typify**
3. **Run**: `pip install -r requirements.txt`
4. **Start**: `python main.py`
5. **Wait for model download** (first time only)
6. **Start typing** and use hotkeys!

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10, Linux, macOS
- **RAM**: 8GB
- **Storage**: 5GB free space
- **CPU**: 4 cores, 2.0GHz+

### Recommended Requirements
- **RAM**: 16GB+
- **Storage**: SSD with 10GB+ free space
- **CPU**: 8+ cores, 3.0GHz+
- **GPU**: NVIDIA GPU with 6GB+ VRAM (optional but recommended)

## 🔍 Troubleshooting

### Common Issues

**App won't start:**
- Check Python version: `python --version`
- Verify dependencies: `pip install -r requirements.txt`
- Check available RAM (need at least 8GB)

**Hotkeys not working:**
- Run as administrator (Windows)
- Check if other apps use the same hotkeys
- Verify Typify is running in background

**Slow performance:**
- Enable GPU acceleration
- Increase `MODEL_THREADS` in config
- Close other memory-intensive applications
- Check available RAM

**Model download fails:**
- Check internet connection
- Verify firewall settings
- Ensure sufficient disk space

### Performance Optimization
- **GPU Users**: Set `MODEL_GPU_LAYERS=35` for 3-5x speed improvement
- **CPU Users**: Adjust `MODEL_THREADS` to match your CPU cores
- **Memory**: Close unnecessary applications to free up RAM

## 🎯 Architecture

Typify is built with clean architecture principles based on SOLID design patterns, ensuring maintainability, extensibility, and reliable performance.

---

**Start writing better today - completely free and offline!** 