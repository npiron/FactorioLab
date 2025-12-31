"""
Simple demo agent - MOVEMENT DEMO

Makes the character move in a visible square pattern.
You'll see the player moving around in Factorio!
"""

DEMO_ACTIONS = [
    # Move in a square pattern - very visible!
    "move_to(Position(x=0, y=0))",
    "sleep(60)",
    "move_to(Position(x=10, y=0))",
    "sleep(60)",
    "move_to(Position(x=10, y=10))",
    "sleep(60)",
    "move_to(Position(x=0, y=10))",
    "sleep(60)",
    "move_to(Position(x=0, y=0))",
    "sleep(60)",
    # Do it again for emphasis!
    "move_to(Position(x=-10, y=0))",
    "sleep(60)",
    "move_to(Position(x=-10, y=-10))",
    "sleep(60)",
    "move_to(Position(x=0, y=-10))",
    "sleep(60)",
    "move_to(Position(x=0, y=0))",
    "print('Movement demo complete!')",
]


def get_demo_code(step: int) -> str:
    """Get the code for a demo step."""
    if step < len(DEMO_ACTIONS):
        return DEMO_ACTIONS[step]
    else:
        # After all actions, just sleep
        return "sleep(60)"
