"""
Simple demo agent that performs visible Factorio actions.

Uses only BASIC FLE commands that are guaranteed to work.
"""

DEMO_ACTIONS = [
    # Step 0-4: Place a visible line of walls
    "place_entity('stone-wall', position={'x': 0, 'y': 0})",
    "place_entity('stone-wall', position={'x': 1, 'y': 0})",
    "place_entity('stone-wall', position={'x': 2, 'y': 0})",
    "place_entity('stone-wall', position={'x': 3, 'y': 0})",
    "place_entity('stone-wall', position={'x': 4, 'y': 0})",
    # Step 5-9: Place another line
    "place_entity('stone-wall', position={'x': 0, 'y': 2})",
    "place_entity('stone-wall', position={'x': 1, 'y': 2})",
    "place_entity('stone-wall', position={'x': 2, 'y': 2})",
    "place_entity('stone-wall', position={'x': 3, 'y': 2})",
    "place_entity('stone-wall', position={'x': 4, 'y': 2})",
    # Step 10-14: Connect them
    "place_entity('stone-wall', position={'x': 0, 'y': 1})",
    "place_entity('stone-wall', position={'x': 4, 'y': 1})",
    "sleep(120)",  # Pause so user can see
    "print('Demo complete - you should see walls!')",
    "score()",
]


def get_demo_code(step: int) -> str:
    """Get the code for a demo step."""
    if step < len(DEMO_ACTIONS):
        return DEMO_ACTIONS[step]
    else:
        # After all actions, just sleep
        return "sleep(60)"
