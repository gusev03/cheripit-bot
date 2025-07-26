from game_scores import process_connections_message

def test_connections_processing():
    """Test connections message processing with inline test data."""
    
    # Connections test data
    connections_valid = [
        ("Connections\nPuzzle #775\n🟩🟦🟦🟦\n🟦🟦🟦🟦\n🟨🟨🟨🟨\n🟩🟩🟩🟩\n🟪🟪🟪🟪", "Nice job solving the Connections!"),
        ("Connections\nPuzzle #773\n🟦🟦🟦🟦\n🟩🟩🟩🟩\n🟨🟨🟨🟨\n🟪🟪🟪🟪", "Nice job solving the Connections!"),
        ("connections #456\n🟨🟨🟨🟨\n🟩🟩🟩🟩\n🟦🟦🟦🟦\n🟪🟪🟪🟪", "Nice job solving the Connections!"),
        ("Connections puzzle 789 🟨🟨🟨🟨 🟩🟩🟩🟩 🟦🟦🟦🟦 🟪🟪🟪🟪", "Nice job solving the Connections!"),
        ("Connections #100\n🟨🟨🟨🟨\n🟩🟩🟩🟩\n🟦🟦🟦🟦\n🟪🟪🟪🟨\n🟩🟦🟪🟨\n🟨🟩🟦🟪", "You lost! Better luck tomorrow!"),
        ("Connecions #500\n🟨🟨🟨🟨\n🟩🟩🟩🟩\n🟦🟪🟨🟩\n🟪🟦🟨🟩\n🟨🟩🟦🟪\n🟪🟨🟩🟦", "You lost! Better luck tomorrow!"),
    ]
    
    connections_invalid = [
        "Just talking about connections",
        "Random text with emojis 🟨🟩",
        "🟨🟨🟨🟨\n🟩🟩🟩🟩\n🟦🟦🟦🟦\n🟪🟪🟪🟪",
        "Connections #123\n🟨🟨🟨\n🟩🟩🟩🟩",
    ]
    
    # Test valid cases
    for message, expected in connections_valid:
        response = process_connections_message(message)
        assert response == expected, f"Expected '{expected}' for message: {message}"
    
    # Test invalid cases
    for message in connections_invalid:
        response = process_connections_message(message)
        assert response is None, f"Should not match: {message}" 