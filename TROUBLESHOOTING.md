# Troubleshooting Guide

## Common Issues and Solutions

### 1. Ollama Connection Issues

**Problem**: "Cannot connect to Ollama" error

**Solutions**:
- Make sure Ollama is running: `ollama serve`
- Check if Ollama is listening on the correct port:
  ```bash
  curl http://localhost:11434/api/tags
  ```
- If using a different port, update `OLLAMA_URL` in `app.py`

**Problem**: "Model gemma3:4b not found"

**Solutions**:
- Pull the model: `ollama pull gemma3:4b`
- List available models: `ollama list`
- If using a different model, update `OLLAMA_MODEL` in `app.py`

### 2. Desktop Commander Issues

**Problem**: "Desktop Commander not found"

**Solutions**:
- Install globally: `npm install -g @wonderwhy-er/desktop-commander`
- Or use npx (already configured in the app)
- Check installation: `npx -y @wonderwhy-er/desktop-commander --version`

**Problem**: "Command execution failed" or "Permission denied"

**Solutions**:
- Check Desktop Commander's allowed directories configuration
- Some commands may be blocked by security settings
- Try simpler commands first (e.g., `echo "test"`)

### 3. Python/Gradio Issues

**Problem**: "ModuleNotFoundError: No module named 'gradio'"

**Solutions**:
```bash
pip install -r requirements.txt
# or
pip install gradio requests
```

**Problem**: "Port 7860 is already in use"

**Solutions**:
- Change the port in `app.py` (search for `server_port=7860`)
- Or kill the process using the port:
  ```bash
  lsof -ti:7860 | xargs kill -9
  ```

### 4. Command Generation Issues

**Problem**: LLM generates incorrect or overly complex commands

**Solutions**:
- Be more specific in your prompts
- Edit the generated command before executing
- Adjust the prompt template in `app.py`
- Try different temperature settings

**Problem**: Commands take too long to generate

**Solutions**:
- Check Ollama performance: `ollama ps`
- Try a smaller model if needed
- Reduce `num_predict` in the Ollama parameters

### 5. File Access Issues

**Problem**: "Path not allowed" errors

**Solutions**:
- Check Desktop Commander's `allowedDirectories` configuration
- Add your working directory to the allowed list
- Use absolute paths when specifying files

### 6. Performance Issues

**Problem**: Slow response times

**Solutions**:
- Ensure Ollama has enough resources
- Check system memory usage
- Consider using a smaller model
- Restart Ollama service if it's been running for a long time

## Debug Mode

To enable more detailed logging, modify `app.py`:

```python
# Add at the top of the file
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing Individual Components

### Test Ollama only:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:4b",
  "prompt": "Say hello",
  "stream": false
}'
```

### Test Desktop Commander only:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"execute_command","arguments":{"command":"echo test"}}}' | npx -y @wonderwhy-er/desktop-commander
```

## Getting Help

1. Run the test script: `python test_setup.py`
2. Check the logs in the terminal where you started the app
3. Look for error messages in the Gradio interface
4. Verify all services are running with the "Refresh Status" button

## Advanced Configuration

Create a `config.py` file (copy from `config_example.py`) to customize:
- Model settings
- Command templates  
- UI preferences
- Security settings