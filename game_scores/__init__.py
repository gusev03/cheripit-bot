"""
Game scores processing package.

This package contains modules for processing different word game scores
and providing appropriate responses.
"""

from .wordle import process_wordle_message
from .connections import process_connections_message
from .strands import process_strands_message

__all__ = [
    "process_wordle_message",
    "process_connections_message", 
    "process_strands_message",
] 