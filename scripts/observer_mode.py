"""
Observer Mode - Watch agent actions in real-time via screenshots
"""

from factorio_ai_lab.env_adapter import FleEnv
import time

print("🎥 Starting Observer Mode...")
print("   Screenshots will be saved to .fle/data/_screenshots/")

env = FleEnv()
obs = env.reset()

# Take initial screenshot
code = """
# Take screenshot of current state
game.take_screenshot('observer_view.png', show_gui=True, show_entity_info=True)
print('📸 Screenshot saved')
"""

for i in range(10):
    print(f"\n📸 Capture {i + 1}/10...")
    obs = env.step(code)
    time.sleep(2)  # Wait 2 seconds between captures

env.close()
print("\n✅ Observer mode complete!")
print("   Check .fle/data/_screenshots/ for images")
