#!/usr/bin/env python3

import sys
from typing import Tuple

import requests

from core.models import CommandStatus


def get_available_models() -> Tuple[list, CommandStatus]:
    """Get list of available Ollama models."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models if m.get("name")]
            if model_names:
                return model_names, CommandStatus.SUCCESS
            return [], CommandStatus.WARNING
        return [], CommandStatus.ERROR
    except requests.RequestException:
        return [], CommandStatus.ERROR


def check_ollama(ollama_model: str) -> Tuple[str, CommandStatus]:
    """Check if Ollama is available and the model is installed."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if ollama_model in model_names:
                return f"Ollama ready ({ollama_model})", CommandStatus.SUCCESS
            return f"Model {ollama_model} not found", CommandStatus.ERROR
        return "Ollama not responding", CommandStatus.ERROR
    except requests.RequestException:
        return "Ollama offline", CommandStatus.ERROR


def generate_command(prompt: str, ollama_url: str, ollama_model: str, timeout: int) -> Tuple[str, CommandStatus]:
    """Generate a shell command using Ollama."""
    enhanced_prompt = f"""You are a helpful shell command expert. Generate a single shell command.
User request: {prompt}
Operating system: {sys.platform}
Important: Respond with ONLY the command, no explanations or markdown."""
    
    payload = {
        "model": ollama_model,
        "prompt": enhanced_prompt,
        "stream": False,
        "temperature": 0.7,
        "options": {"num_predict": 100}
    }
    
    try:
        resp = requests.post(ollama_url, json=payload, timeout=timeout)
        resp.raise_for_status()
        
        response_data = resp.json()
        if "response" in response_data:
            command = response_data["response"].strip().replace("```", "").strip()
            return command, CommandStatus.SUCCESS
        return "", CommandStatus.ERROR
            
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Please run: ollama serve", CommandStatus.ERROR
    except requests.exceptions.Timeout:
        return "Request timed out. Try a simpler prompt.", CommandStatus.WARNING
    except Exception as e:
        return f"Error: {str(e)}", CommandStatus.ERROR