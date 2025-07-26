import re
from typing import Optional


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