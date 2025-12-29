# Ollama Local Setup Guide

## Quick Start with Local Ollama

### 1. Install Ollama

Download and install Ollama from: https://ollama.com

### 2. Download the Model

```bash
# Pull the qwen2.5-7b model (or your preferred model)
ollama pull qwen2.5-7b
```

### 3. Start Ollama

Ollama runs automatically after installation. Verify it's running:

```bash
# Check if Ollama is running
ollama list

# Or test the API
curl http://localhost:11434/api/tags
```

### 4. Configure Your .env File

Add to your `.env` file:

```bash
# Use local Ollama
LLM_MODE=local

# Optional: Customize if Ollama is on different port
LLM_BASE_URL=http://localhost:11434/v1

# Optional: Use a different model
LLM_MODEL=qwen2.5-7b
```

### 5. Test the Connection

```python
import httpx

response = httpx.get("http://localhost:11434/api/tags")
print(response.json())
```

## Available Models

You can use any model supported by Ollama. Popular choices:

```bash
# Large language models
ollama pull qwen2.5-7b
ollama pull qwen2.5-14b
ollama pull llama3.2
ollama pull mistral
ollama pull codellama

# Then set in .env:
LLM_MODEL=qwen2.5-7b  # or your chosen model
```

## Switching Between Local and Remote

### Use Local Ollama
```bash
LLM_MODE=local
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5-7b
```

### Use Remote ELI Gateway
```bash
LLM_MODE=remote
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://gateway.eli.gaia.gic.ericsson.se/api/openai/v1
LLM_MODEL=qwen2.5-7b
```

### Auto-detect (Default)
```bash
# If base URL contains localhost, uses local mode
# Otherwise uses remote mode
LLM_MODE=auto
LLM_BASE_URL=http://localhost:11434/v1  # Will use local
# or
LLM_BASE_URL=https://remote-server.com/v1  # Will use remote
```

## Troubleshooting

### Ollama Not Running
```bash
# Start Ollama service
ollama serve

# Or on Windows, start the Ollama application
```

### Model Not Found
```bash
# List available models
ollama list

# Pull the model if not available
ollama pull qwen2.5-7b
```

### Connection Refused
- Check if Ollama is running: `ollama list`
- Verify the port (default: 11434)
- Check firewall settings

### Different Port
If Ollama is running on a different port:
```bash
LLM_BASE_URL=http://localhost:8080/v1
```

## Benefits of Local Ollama

1. **No Internet Required**: Works offline
2. **No API Keys**: No authentication needed
3. **Fast**: No network latency
4. **Private**: Data stays on your machine
5. **Free**: No API costs
6. **Customizable**: Use any Ollama-supported model

## Performance Tips

1. **Use GPU**: Ollama automatically uses GPU if available
2. **Model Size**: Smaller models (7B) are faster, larger (14B+) are more capable
3. **Quantization**: Use quantized models for better performance
   ```bash
   ollama pull qwen2.5:7b-q4_0  # Quantized version
   ```

