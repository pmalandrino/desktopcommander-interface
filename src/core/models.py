#!/usr/bin/env python3

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class CommandStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class CommandEntry:
    timestamp: str
    prompt: str
    command: str
    output: str
    status: CommandStatus

    def __post_init__(self):
        if len(self.output) > 500:
            self.output = self.output[:500] + "..."


@dataclass
class Config:
    ollama_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "gemma3:4b"
    command_timeout: int = 30

    @classmethod
    def from_env(cls):
        return cls(
            ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
            ollama_model=os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
            command_timeout=int(os.environ.get("COMMAND_TIMEOUT", "30"))
        )


@dataclass
class AppState:
    command_history: List[CommandEntry] = field(default_factory=list)
    config: Config = field(default_factory=Config.from_env)
    dry_run_mode: bool = False
    safe_mode: bool = False