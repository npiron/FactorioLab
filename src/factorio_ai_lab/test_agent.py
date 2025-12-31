"""
Simple Test Agent - Discovering Working FLE Commands

This agent uses ONLY the most basic commands to test what works.
"""

TEST_ACTIONS = [
    # Test 1: Simple print
    "print('Test 1: Hello from FLE agent!')",
    "sleep(30)",
    # Test 2: Math
    "result = 2 + 2\nprint(f'Test 2: 2+2 = {result}')",
    "sleep(30)",
    # Test 3: Try to get player info (simplest possible)
    "print('Test 3: Trying to access game state...')",
    "sleep(30)",
    # Test 4-10: More movement tests (we know this works!)
    "move_to(Position(x=5, y=0))",
    "sleep(60)",
    "move_to(Position(x=5, y=5))",
    "sleep(60)",
    "move_to(Position(x=0, y=5))",
    "sleep(60)",
    "move_to(Position(x=0, y=0))",
    "print('Test complete!')",
]


def get_test_code(step: int) -> str:
    """Get test code."""
    if step < len(TEST_ACTIONS):
        return TEST_ACTIONS[step]
    else:
        return "sleep(60)"
