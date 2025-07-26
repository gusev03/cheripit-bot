from game_scores import process_strands_message


def test_strands_processing():
    """Test strands message processing with inline test data."""
    
    # Strands test data
    strands_valid = [
        ("Strands #507\n“Chips in”\n🔵🔵🔵🟡\n🔵🔵🔵", "Nice job solving today's strands!"),
    ]
    
    strands_invalid = []
    
    # Test valid cases
    for message, expected in strands_valid:
        response = process_strands_message(message)
        assert response == expected, f"Expected '{expected}' for message: {message}"
    
    # Test invalid cases
    for message in strands_invalid:
        response = process_strands_message(message)
        assert response is None, f"Should not match: {message}" 