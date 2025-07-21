#!/usr/bin/env python3
"""
Desktop Commander Launcher
Automatically selects the best version to run
"""

import subprocess
import sys
import os

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        return resp.status_code == 200
    except:
        return False

def main():
    print("🚀 Desktop Commander Launcher")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import gradio
        import requests
    except ImportError:
        print("📦 Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed!")
    
    # Check Ollama
    if not check_ollama():
        print("\n⚠️  Ollama is not running!")
        print("Please start Ollama in another terminal: ollama serve")
        print("\nWould you like to:")
        print("1. Exit and start Ollama first")
        print("2. Continue anyway (limited functionality)")
        
        choice = input("\nYour choice (1/2): ")
        if choice == "1":
            print("\n💡 Start Ollama with: ollama serve")
            sys.exit(0)
    else:
        print("✅ Ollama is running")
    
    # Select version
    print("\n🎨 Available versions:")
    print("1. UX-Enhanced (Recommended) - Beautiful, modern interface")
    print("2. Simple - Basic interface with direct execution")
    print("3. Full - Desktop Commander integration")
    print("4. Enhanced - Advanced features")
    
    choice = input("\nSelect version (1-4) [default: 1]: ").strip() or "1"
    
    versions = {
        "1": "app_ux.py",
        "2": "app_simple.py",
        "3": "app.py",
        "4": "app_enhanced.py"
    }
    
    selected_file = versions.get(choice, "app_ux.py")
    
    if not os.path.exists(selected_file):
        print(f"❌ {selected_file} not found!")
        sys.exit(1)
    
    print(f"\n🎯 Launching {selected_file}...")
    print("=" * 50)
    
    # Run the selected version
    subprocess.run([sys.executable, selected_file])

if __name__ == "__main__":
    main()