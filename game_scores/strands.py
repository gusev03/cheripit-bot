import re
from typing import Optional


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