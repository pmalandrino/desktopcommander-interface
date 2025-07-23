#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from unittest.mock import patch, MagicMock

import pytest
import requests

from core.ollama_service import check_ollama, generate_command
from core.models import CommandStatus


class TestCheckOllama:
    """Test Ollama service availability checks."""
    
    @patch('src.core.ollama_service.requests.get')
    def test_check_ollama_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "gemma3:4b"},
                {"name": "llama2"}
            ]
        }
        mock_get.return_value = mock_response
        
        status_text, status = check_ollama("gemma3:4b")
        
        assert status_text == "Ollama ready (gemma3:4b)"
        assert status == CommandStatus.SUCCESS
    
    @patch('src.core.ollama_service.requests.get')
    def test_check_ollama_model_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama2"}]
        }
        mock_get.return_value = mock_response
        
        status_text, status = check_ollama("gemma3:4b")
        
        assert status_text == "Model gemma3:4b not found"
        assert status == CommandStatus.ERROR
    
    @patch('src.core.ollama_service.requests.get')
    def test_check_ollama_not_responding(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        status_text, status = check_ollama("gemma3:4b")
        
        assert status_text == "Ollama not responding"
        assert status == CommandStatus.ERROR
    
    @patch('src.core.ollama_service.requests.get')
    def test_check_ollama_offline(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection error")
        
        status_text, status = check_ollama("gemma3:4b")
        
        assert status_text == "Ollama offline"
        assert status == CommandStatus.ERROR


class TestGenerateCommand:
    """Test command generation with Ollama."""
    
    @patch('src.core.ollama_service.requests.post')
    def test_generate_command_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "ls -la"
        }
        mock_post.return_value = mock_response
        
        command, status = generate_command(
            "list all files",
            "http://localhost:11434/api/generate",
            "gemma3:4b",
            30
        )
        
        assert command == "ls -la"
        assert status == CommandStatus.SUCCESS
    
    @patch('src.core.ollama_service.requests.post')
    def test_generate_command_with_markdown(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "```bash\nls -la\n```"
        }
        mock_post.return_value = mock_response
        
        command, status = generate_command(
            "list all files",
            "http://localhost:11434/api/generate",
            "gemma3:4b",
            30
        )
        
        assert command == "ls -la"
        assert status == CommandStatus.SUCCESS
    
    @patch('src.core.ollama_service.requests.post')
    def test_generate_command_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("Cannot connect")
        
        command, status = generate_command(
            "list files",
            "http://localhost:11434/api/generate",
            "gemma3:4b",
            30
        )
        
        assert "Cannot connect to Ollama" in command
        assert status == CommandStatus.ERROR
    
    @patch('src.core.ollama_service.requests.post')
    def test_generate_command_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        command, status = generate_command(
            "complex task",
            "http://localhost:11434/api/generate",
            "gemma3:4b",
            30
        )
        
        assert "Request timed out" in command
        assert status == CommandStatus.WARNING
    
    @patch('src.core.ollama_service.requests.post')
    def test_generate_command_no_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        
        command, status = generate_command(
            "do something",
            "http://localhost:11434/api/generate",
            "gemma3:4b",
            30
        )
        
        assert command == ""
        assert status == CommandStatus.ERROR