"""
Ultra-visible demo agent - impossible to miss!

Places a massive wall pattern that's immediately visible.
"""

VISUAL_DEMO_ACTIONS = [
    # Place a huge square of walls
    """
# Place 20 walls in a line
for i in range(20):
    place_entity(Prototype.StoneWall, position=Position(x=i, y=0))
""",
    """
# Place another line of walls
for i in range(20):
    place_entity(Prototype.StoneWall, position=Position(x=i, y=5))
""",
    """
# Place vertical walls
for i in range(5):
    place_entity(Prototype.StoneWall, position=Position(x=0, y=i))
""",
    """
# More vertical walls
for i in range(5):
    place_entity(Prototype.StoneWall, position=Position(x=20, y=i))
""",
    # Move player around visibly
    "move_to(Position(x=10, y=10))",
    "sleep(120)",  # Pause so you can see
    "move_to(Position(x=-10, y=-10))",
    "sleep(120)",
    "move_to(Position(x=0, y=0))",
    "sleep(120)",
]


def get_visual_demo_code(step: int) -> str:
    """Get ultra-visible demo code."""
    if step < len(VISUAL_DEMO_ACTIONS):
        return VISUAL_DEMO_ACTIONS[step]
    else:
        return "sleep(60)"
