#!/usr/bin/env python3

from datetime import datetime
from typing import List

from core.models import CommandEntry, CommandStatus


def add_to_history(
    history: List[CommandEntry],
    prompt: str,
    command: str,
    output: str,
    status: CommandStatus
) -> CommandEntry:
    """Add a command to the history."""
    entry = CommandEntry(
        timestamp=datetime.now().strftime("%H:%M:%S"),
        prompt=prompt,
        command=command,
        output=output,
        status=status
    )
    history.append(entry)
    return entry