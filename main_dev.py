from pynput import keyboard
from pynput.keyboard import Key, Controller
import sys
import pyperclip
import time
import os
from string import Template
from llama_cpp import Llama

# Disable HuggingFace symlink warning
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

controller = Controller()

# Simple cache for repeated corrections
correction_cache = {}
summarize_cache = {}
tone_change_cache = {}

def download_model_if_needed():
    """Download the model if it doesn't exist locally"""
    model_path = "./models/mistral-7b-instruct-v0.2.Q4_K_S.gguf"
    
    if os.path.exists(model_path):
        print(f"Model found at: {model_path}")
        return model_path
    
    print("Model not found locally. Downloading...")
    
    try:
        from huggingface_hub import hf_hub_download
        
        # Create models directory if it doesn't exist
        os.makedirs("./models", exist_ok=True)
        
        # Set cache directory to D: drive to avoid C: drive space issues
        cache_dir = os.path.abspath("./models/.cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        print("Downloading Mistral-7B model (~4.1 GB). This may take a while...")
        print(f"Downloading to: {os.path.abspath('./models')}")
        
        # Download directly to models folder, bypassing default cache
        downloaded_path = hf_hub_download(
            repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
            filename="mistral-7b-instruct-v0.2.Q4_K_S.gguf",
            cache_dir=cache_dir,  # Use local cache on D: drive
            local_files_only=False,
            force_download=False
        )
        
        # Copy to final location
        expected_path = "./models/mistral-7b-instruct-v0.2.Q4_K_S.gguf"
        if downloaded_path != expected_path:
            import shutil
            print(f"Moving model to final location...")
            shutil.copy2(downloaded_path, expected_path)
        
        print(f"Model downloaded successfully to: {os.path.abspath(expected_path)}")
        return expected_path
        
    except ImportError:
        print("Error: huggingface_hub not installed.")
        print("Please install it with: pip install huggingface_hub")
        print("Or download the model manually from:")
        print("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_S.gguf")
        return None
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Please download the model manually from:")
        print("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_S.gguf")
        return None

# Initialize Llama model
model_path = download_model_if_needed()

if model_path and os.path.exists(model_path):
    try:
        print("Loading model... This may take a moment.")
        llm = Llama(
            model_path=model_path,
            n_ctx=1024,  # Reduced context window for faster processing
            n_threads=12,  # Increased threads (adjust based on your CPU)
            n_batch=1024,  # Batch size for processing
            n_gpu_layers=0,  # Set to 35+ if you have a compatible GPU
            use_mmap=True,  # Memory mapping for faster loading
            use_mlock=False,  # Don't lock memory (saves RAM)
            verbose=False  # Reduce debug output
        )
        MODEL_LOADED = True
        print("Model loaded successfully! Grammar correction is ready.")
    except Exception as e:
        print(f"Warning: Could not load Llama model: {e}")
        print("Please check the model file and try again.")
        MODEL_LOADED = False
else:
    print("Model not available. Running in pass-through mode.")
    MODEL_LOADED = False

PROMPT_TEMPLATE = Template(
    """[INST] Fix all typos, grammar, and punctuation errors in the following text. Keep the same meaning and preserve line breaks. Only return the corrected text without any explanations.

Text to fix: $text [/INST]"""
)

SUMMARIZE_TEMPLATE = Template(
    """[INST] Summarize the following text in a concise and clear manner. Keep the main points and key information. Make it about 1/3 the length of the original.Only return the summarized text without any explanations.

Text to summarize: $text [/INST]"""
)

TONE_CHANGE_TEMPLATE = Template(
    """[INST] Rewrite the following text to make it more formal and professional while keeping the same meaning. Use appropriate business language and tone. Only return the formal text without any explanations.

Text to make formal: $text [/INST]"""
)

def fix_text(text):
    if not MODEL_LOADED:
        print("Model not loaded, returning original text")
        return text
    
    # Check cache first
    text_key = text.strip().lower()
    if text_key in correction_cache:
        print("Using cached correction")
        return correction_cache[text_key]
    
    try:
        prompt = PROMPT_TEMPLATE.substitute(text=text)
        
        # Debug: Show the prompt being sent
        print(f"Prompt being sent: {prompt}")
        
        # Start timing
        start_time = time.time()
        
        # Use Llama to generate response
        response = llm(
            prompt,
            max_tokens=max(100, len(text) * 4),  # More generous token limit
            temperature=0.3,  # Balanced creativity and consistency
            top_p=0.9,
            top_k=40,  # Reduced for faster sampling
            stop=["[INST]", "</s>", "[/INST]"],  # Mistral-specific stop tokens
            echo=False,
            repeat_penalty=1.05,
            stream=False  # Ensure no streaming for consistent timing
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Extract the generated text
        fixed_text = response['choices'][0]['text'].strip()
        
        # Debug output
        print(f"Original: '{text[:50]}...'")
        print(f"Fixed: '{fixed_text[:50]}...'")
        print(f"Response length: {len(fixed_text)} chars")
        print(f"Grammar correction took: {response_time:.2f} seconds")
        
        # More lenient response validation
        if not fixed_text:
            print("Warning: Empty response, returning original text")
            return text

        # If response is too short compared to original, it might be incomplete
        if len(fixed_text) < len(text) * 0.3 and len(text) > 10:
            print("Warning: Response seems too short, returning original text")
            return text

        # Cache the result for future use
        correction_cache[text_key] = fixed_text
        
        # Limit cache size to prevent memory issues
        if len(correction_cache) > 100:
            # Remove oldest entries (simple approach)
            keys_to_remove = list(correction_cache.keys())[:20]
            for key in keys_to_remove:
                del correction_cache[key]
            
        return fixed_text
        
    except Exception as e:
        print(f"Error fixing text: {e}")
        return text

def summarize_text(text):
    """Summarize the given text"""
    if not MODEL_LOADED:
        print("Model not loaded, returning original text")
        return text
    
    # Check cache first
    text_key = text.strip().lower()
    if text_key in summarize_cache:
        print("Using cached summary")
        return summarize_cache[text_key]
    
    try:
        prompt = SUMMARIZE_TEMPLATE.substitute(text=text)
        
        # Start timing
        start_time = time.time()
        
        # Use Llama to generate response
        response = llm(
            prompt,
            max_tokens=min(200, max(100, len(text))),  # Summary should be shorter
            temperature=0.2,
            top_p=0.8,
            top_k=40,
            stop=["[INST]", "</s>", "[/INST]"],
            echo=False,
            repeat_penalty=1.05,
            stream=False
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Extract the generated text
        summary_text = response['choices'][0]['text'].strip()
        
        # Quick validation
        if not summary_text:
            print("Warning: Empty summary, returning original text")
            return text
        
        # Debug output
        print(f"Original: '{text[:50]}...'")
        print(f"Summarized: '{summary_text[:50]}...'")
        print(f"Response length: {len(summary_text)} chars")
        print(f"Summarization took: {response_time:.2f} seconds")        
        
        # Cache the result
        summarize_cache[text_key] = summary_text
        
        # Limit cache size
        if len(summarize_cache) > 50:
            keys_to_remove = list(summarize_cache.keys())[:10]
            for key in keys_to_remove:
                del summarize_cache[key]
        
        return summary_text
        
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return text

def change_tone_formal(text):
    """Change the tone of text to be more formal"""
    if not MODEL_LOADED:
        print("Model not loaded, returning original text")
        return text
    
    # Check cache first
    text_key = text.strip().lower()
    if text_key in tone_change_cache:
        print("Using cached tone change")
        return tone_change_cache[text_key]
    
    try:
        prompt = TONE_CHANGE_TEMPLATE.substitute(text=text)
        
        # Start timing
        start_time = time.time()
        
        # Use Llama to generate response
        response = llm(
            prompt,
            max_tokens=max(150, len(text) * 2),  # Allow for expansion in formal language
            temperature=0.2,  # Lower temperature for more consistent formal tone
            top_p=0.9,
            top_k=40,
            stop=["[INST]", "</s>", "[/INST]"],
            echo=False,
            repeat_penalty=1.05,
            stream=False
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Extract the generated text
        formal_text = response['choices'][0]['text'].strip()
        
        # Quick validation
        if not formal_text or len(formal_text) < len(text) * 0.3:
            print("Warning: Invalid formal tone response, returning original text")
            return text
        
        # Debug output
        print(f"Original: '{text[:50]}...'")
        print(f"Formal: '{formal_text[:50]}...'")
        print(f"Response length: {len(formal_text)} chars")
        print(f"Tone change took: {response_time:.2f} seconds")        
        
        # Cache the result
        tone_change_cache[text_key] = formal_text
        
        # Limit cache size
        if len(tone_change_cache) > 50:
            keys_to_remove = list(tone_change_cache.keys())[:10]
            for key in keys_to_remove:
                del tone_change_cache[key]
        
        return formal_text
        
    except Exception as e:
        print(f"Error changing tone: {e}")
        return text

def copy_to_clipboard():
    controller.press(Key.ctrl)
    controller.press('c')
    controller.release('c')
    controller.release(Key.ctrl)

def paste_text():
    controller.press(Key.ctrl)
    controller.press('v')
    controller.release('v')
    controller.release(Key.ctrl)

def select_current_line():
    # Move cursor to start of line
    controller.press(Key.home)
    controller.release(Key.home)
    # Hold Shift and press End to select to end of line
    controller.press(Key.shift)
    controller.press(Key.end)
    controller.release(Key.end)
    controller.release(Key.shift)    

def fix_current_line():
    select_current_line()
    fix_selection()
    pass

def fix_selection():
    # 1. Copy to clipboard
    copy_to_clipboard()

    # 2. Get the text from clipboard
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. Fix the text
    fixed_text = fix_text(text)

    # 4. Copy back to clipboard
    pyperclip.copy(fixed_text)

    # 5. Insert text
    paste_text()

def summarize_selection():
    # 1. Copy to clipboard
    copy_to_clipboard()

    # 2. Get the text from clipboard
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. Summarize the text
    summarized_text = summarize_text(text)

    # 4. Copy back to clipboard
    pyperclip.copy(summarized_text)

    # 5. Insert text
    paste_text()

def change_tone_selection():
    # 1. Copy to clipboard
    copy_to_clipboard()

    # 2. Get the text from clipboard
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. Change tone to formal
    formal_text = change_tone_formal(text)

    # 4. Copy back to clipboard
    pyperclip.copy(formal_text)

    # 5. Insert text
    paste_text()

def on_f9():
    print('f9 pressed')
    fix_current_line()

def on_f10():
    print('f10 pressed')
    fix_selection()

def on_f8():
    print('F8 pressed - Summarizing text')
    summarize_selection()

def on_f7():
    print('F7 pressed - Changing tone to formal')
    change_tone_selection()

def exit_program():
    print('Exiting program...')
    sys.exit(0)

# print(Key.f8.value,Key.f7.value);    

with keyboard.GlobalHotKeys({
        '<120>': on_f9,                    # F9 - Grammar correction
        '<121>': on_f10,                   # F10 - Grammar correction (selected text)
        '<119>': on_f8,                    # F8 - Summarize
        '<118>': on_f7,                    # F7 - Change tone to formal
        '<ctrl>+<shift>+e': exit_program,  # Ctrl+Shift+E - Exit
        }) as hotKeys:
    hotKeys.join()    
    
