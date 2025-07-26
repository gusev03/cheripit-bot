import re
from typing import Optional


def process_wordle_message(message: str) -> Optional[str]:
    """
    Process a message for wordle scores and return appropriate response.
    
    Args:
        message: The message text to process
        
    Returns:
        Response message if wordle score detected, None otherwise
    """
    pattern = r"(?i)wordle\s+\d+(?:,\d+)?\s+([0-6X])(?=/6\*?)"
    matches = re.findall(pattern, message)
    
    if not matches:
        return None
    
    score = matches[0]
    
    if score == "X":
        return "You lost! ;("
    elif score == "1":
        return "You totally looked up the answer!"
    elif score == "2":
        return "Yeeeesh what a score!"
    elif score == "3":
        return "Good score!"
    elif score == "4":
        return "Decent score!"
    elif score == "5":
        return "I think we can do better tomorrow!"
    elif score == "6":
        return "That was a close one!"
    else:
        return "Are you sure that's a valid score?"


def process_connections_message(message: str) -> Optional[str]:
    """
    Process a message for connections scores and return appropriate response.
    
    Args:
        message: The message text to process
        
    Returns:
        Response message if connections score detected, None otherwise
    """
    pattern = r"connections\s*(?:puzzle\s*)?#?\d+\s*((?:(?:🟨|🟩|🟦|🟪){4}\s*){1,6})"
    matches = re.findall(pattern, message, re.IGNORECASE)
    
    if not matches:
        return None
    
    circles_str = matches[0]
    rows = circles_str.strip().split()
    is_loss = len(rows) == 6 and len(set(rows[-1])) > 1
    
    if is_loss:
        return "You lost! Better luck tomorrow!"
    else:
        return "Nice job solving the Connections!"


def process_strands_message(message: str) -> Optional[str]:
    """
    Process a message for strands scores and return appropriate response.
    
    Args:
        message: The message text to process
        
    Returns:
        Response message if valid strands score detected, None otherwise
    """
    pattern = r'(?i)strands\s*#?\d+\s*\n?[\u201c"][^""\u201c\u201d]+[\u201d"]\s*\n?((?:(?:🔵|🟡)+\s*\n?)+)'
    matches = re.findall(pattern, message, re.MULTILINE | re.DOTALL)
    
    if not matches:
        return None
    
    circles_str = matches[0]
    yellow_count = circles_str.count('🟡')
    
    # Valid strands score must have exactly 1 yellow
    if yellow_count == 1:
        return "Nice job solving today's strands!"
    
    return None 