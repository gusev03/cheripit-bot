import re
from typing import Optional
from dotenv import load_dotenv
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

load_dotenv()

WORDLE_AI_ENABLED = os.getenv("WORDLE_AI_ENABLED") == "true"

def process_wordle_message(message: str, use_ai: bool = False) -> Optional[str]:
    """
    Process a message for wordle scores and return appropriate response.
    
    Args:
        message: The message text to process
        
    Returns:
        Response message if wordle score detected, None otherwise
    """

    try:
        pattern = r"(?i)wordle\s+\d+(?:,\d+)?\s+([0-6X])(?=/6\*?)"
        matches = re.findall(pattern, message)
        
        if not matches: # No world score found in user's message
            return None
        
        if use_ai and WORDLE_AI_ENABLED:
            return ai_wordle_response(message)
        else:
            return basic_wordle_response(score=matches[0])
    except Exception as e:
        return None

def basic_wordle_response(score: str) -> Optional[str]:
    """
    Generate a response for a wordle score using a basic pattern matching approach.

    Args:
        message: The message text to process
        
    Returns:
        Response message for the wordle score, None if score is invalid
    """
    match score:
        case "X":
            return "You lost! ;("
        case "1":
            return "You totally looked up the answer!"
        case "2":
            return "Yeeeesh what a score!"
        case "3":
            return "Good score!"
        case "4":
            return "Decent score!"
        case "5":
            return "I think we can do better tomorrow!"
        case "6":
            return "That was a close one!"
        case _:
            return None

def ai_wordle_response(message: str) -> str:
    """
    Generate a response for a wordle score using an LLM (grok-3-mini).
    
    Args:
        message: The message text to process
        
    Returns:
        Response message for the wordle score, None if error
    """
    try:
        xai_client = Client(api_key=os.getenv("XAI_API_KEY"))
        system_prompt = """You are a friendly, slightly sassy bot that responds to people sharing their Wordle scores. 

Wordle is a word guessing game where players have 6 attempts to guess a 5-letter word. Scores are typically shared like "Wordle 1,234 3/6" where the number before the slash is how many guesses it took (1-6), or "X" if they failed.

Scoring context:
- 1/6: Extremely lucky (almost impossible without cheating)
- 2/6: Very impressive, often lucky
- 3/6: Good solid score
- 4/6: Decent, average performance
- 5/6: Cutting it close but still got it
- 6/6: Just barely made it
- X/6: Failed to solve it

Your personality:
- Be brief and casual (1-2 sentences max)
- Slightly playful and teasing but not mean
- Celebrate good scores, gently roast bad ones
- Use casual language, emojis are fine
- Be encouraging even when teasing
- Acknowledge when someone is really struggling or doing really well

Examples of good responses:
- For 1/6: "No way you didn't cheat! 🤔"
- For 3/6: "Solid work! 💪"
- For 6/6: "Whew, cutting it close there!"
- For X/6: "Ouch! Tomorrow's a new day 😅"

Respond to the Wordle score in the message with a brief, engaging comment."""
        chat = xai_client.chat.create(model="grok-3-mini")
        chat.append(system(system_prompt))
        chat.append(user(message))
        return chat.sample().content
    except Exception as e:
        return None