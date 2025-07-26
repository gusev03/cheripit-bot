from game_scores import process_wordle_message

def test_wordle_processing():
    """Test wordle message processing with inline test data."""
    
    # Wordle test data
    wordle_valid = [
        ("Wordle 1,497 5/6*\n\n⬛⬛🟨⬛⬛\n⬛⬛🟨🟩🟩\n🟩⬛⬛🟩🟩\n🟩🟩⬛🟩🟩\n🟩🟩🟩🟩🟩", "I think we can do better tomorrow!"),
        ("Wordle 1497 5/6\n\n⬜🟩⬜⬜⬜\n⬜🟩🟨⬜⬜\n⬜🟩⬜🟩🟩\n🟨🟩⬜🟩🟩\n🟩🟩🟩🟩🟩", "I think we can do better tomorrow!"),
        ("Wordle 1,496 4/6*\n\n⬛⬛⬛⬛🟩\n⬛⬛🟩⬛🟩\n⬛⬛🟩⬛🟩\n🟩🟩🟩🟩🟩", "Decent score!"),
        ("Wordle 1,025 3/6", "Good score!"),
        ("wordle 123 X/6", "You lost! ;("),
        ("WORDLE 456 1/6*", "You totally looked up the answer!"),
        ("Wordle 789 6/6", "That was a close one!"),
        ("wordle 100 2/6", "Yeeeesh what a score!"),
        ("Wordle 1500 1/6*", "You totally looked up the answer!"),
        ("wordle 999 X/6*", "You lost! ;("),
    ]
    
    wordle_invalid = [
        "Wordle 123 7/6",
        "wordle 123",
        "Just talking about wordle",
        "Wordle 123 3/7",
        "Something else 3/6",
        "⬛⬛🟨⬛⬛\n⬛⬛🟨🟩🟩\n🟩⬛⬛🟩🟩",
    ]
    
    # Test valid cases
    for message, expected in wordle_valid:
        response = process_wordle_message(message)
        assert response == expected, f"Expected '{expected}' for message: {message}"
    
    # Test invalid cases
    for message in wordle_invalid:
        response = process_wordle_message(message)
        assert response is None, f"Should not match: {message}" 