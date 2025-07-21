#!/usr/bin/env python3
"""
Test script to verify Ollama and Desktop Commander connectivity
"""

import requests
import subprocess
import json
import sys
import time
import select

def test_ollama():
    """Test Ollama connection and model availability."""
    print("Testing Ollama connection...")
    try:
        # Test connection
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            print("✅ Ollama is running")
            
            # Check for gemma3:4b model
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            if "gemma3:4b" in model_names:
                print("✅ gemma3:4b model is available")
                
                # Test generation
                print("\nTesting generation...")
                payload = {
                    "model": "gemma3:4b",
                    "prompt": "Generate a shell command to list files. Respond with only the command.",
                    "stream": False
                }
                gen_resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
                if gen_resp.status_code == 200:
                    response = gen_resp.json().get("response", "").strip()
                    print(f"✅ Generation successful: {response}")
                    return True
                else:
                    print("❌ Generation failed")
                    return False
            else:
                print(f"❌ gemma3:4b model not found. Available models: {', '.join(model_names)}")
                print("\nTo install the model, run: ollama pull gemma3:4b")
                return False
        else:
            print("❌ Ollama is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure it's running with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_desktop_commander():
    """Test Desktop Commander availability."""
    print("\nTesting Desktop Commander...")
    try:
        # First, just check if npx can find the package
        check_result = subprocess.run(
            ["npx", "-y", "--yes", "@wonderwhy-er/desktop-commander", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Desktop Commander starts up even with --help, so we check if it starts
        if "desktop-commander" in check_result.stdout.lower() or "desktop-commander" in check_result.stderr.lower():
            print("✅ Desktop Commander is available")
        else:
            # Try a different approach - test actual execution
            print("Testing Desktop Commander installation...")
        
        # Test a simple command execution
        print("\nTesting command execution...")
        
        # Create the MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Then send a simple command
        mcp_command = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "execute_command",
                "arguments": {"command": "echo 'Hello from Desktop Commander'"}
            }
        }
        
        proc = subprocess.Popen(
            ["npx", "-y", "--yes", "@wonderwhy-er/desktop-commander"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Send initialization
        proc.stdin.write(json.dumps(mcp_request) + "\n")
        proc.stdin.flush()
        
        # Wait a bit for initialization
        import time
        time.sleep(1)
        
        # Send command
        proc.stdin.write(json.dumps(mcp_command) + "\n")
        proc.stdin.flush()
        
        # Try to read output with timeout
        import select
        timeout = 5
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < timeout:
            if proc.poll() is not None:
                break
            
            # Check if there's output available
            ready, _, _ = select.select([proc.stdout], [], [], 0.1)
            if ready:
                line = proc.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    # Check if we got a successful response
                    try:
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            print("✅ Command execution successful")
                            return True
                    except:
                        pass
        
        # Terminate the process
        proc.terminate()
        
        # If we got here, check if we at least got some Desktop Commander output
        all_output = "\n".join(output_lines)
        if "desktop-commander" in all_output.lower() or "jsonrpc" in all_output:
            print("✅ Desktop Commander is responding (initialization successful)")
            return True
        else:
            print("❌ Desktop Commander not responding properly")
            print(f"Output received: {all_output[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Desktop Commander timed out")
        print("\nThis might be normal on first run - Desktop Commander may need to download dependencies.")
        print("Try running manually: npx -y @wonderwhy-er/desktop-commander")
        return False
    except FileNotFoundError:
        print("❌ npx not found. Make sure Node.js and npm are installed.")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Desktop Commander UI - Setup Test")
    print("=" * 50)
    
    ollama_ok = test_ollama()
    dc_ok = test_desktop_commander()
    
    print("\n" + "=" * 50)
    if ollama_ok and dc_ok:
        print("✅ All systems ready! You can now run: python app.py")
        sys.exit(0)
    else:
        print("❌ Some components need attention. Please fix the issues above.")
        sys.exit(1)