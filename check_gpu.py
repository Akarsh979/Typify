#!/usr/bin/env python3
"""
Simple script to check GPU availability for llama-cpp-python
"""
import subprocess
import sys

def check_gpu():
    print("=== GPU Acceleration Check ===\n")
    
    # Check for NVIDIA GPU
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected!")
            print("You can enable GPU acceleration by setting n_gpu_layers=35 in main.py")
            print("\nGPU Info:")
            print(result.stdout)
            return True
    except FileNotFoundError:
        print("❌ nvidia-smi not found - No NVIDIA GPU or drivers not installed")
    
    # Check for other GPU types
    print("\n📋 Other acceleration options:")
    print("- CPU only: Current setup (works but slower)")
    print("- Metal (Mac): Not applicable on Windows")
    print("- OpenCL: Possible but requires special build")
    
    return False

def main():
    has_gpu = check_gpu()
    
    print(f"\n{'='*50}")
    print("RECOMMENDATION:")
    if has_gpu:
        print("🚀 Enable GPU acceleration for 5-10x speed improvement!")
        print("   Change this line in main.py:")
        print("   n_gpu_layers=0  ->  n_gpu_layers=35")
    else:
        print("💡 CPU optimizations applied. For faster performance:")
        print("   1. Consider getting a GPU (RTX 3060+ recommended)")
        print("   2. Use smaller models (Q4_K_S is good balance)")
        print("   3. Current optimizations should help with speed")
    
    print(f"{'='*50}")

if __name__ == "__main__":
    main() 