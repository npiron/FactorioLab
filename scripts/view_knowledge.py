"""
Megabase Knowledge Viewer
Visualize curriculum progress and phase-specific patterns
"""

import json
from pathlib import Path

PHASES = {
    1: {"name": "Early Game", "goal": "Mining → Smelting → Green Circuits"},
    2: {"name": "Mid Game", "goal": "Oil → Plastics → Red Circuits"},
    3: {"name": "Late Game", "goal": "Roboports + Rails + Modules"},
    4: {"name": "Modular Bases", "goal": "Stampable blocks"},
    5: {"name": "UPS Optimization", "goal": "Refactor + reduce entities"},
}


def view_megabase_knowledge(kb_file=None):
    # Default to project root's data/knowledge/megabase_knowledge.json
    if kb_file is None:
        project_root = Path(__file__).parent.parent
        kb_file = project_root / "data" / "knowledge" / "megabase_knowledge.json"
    else:
        kb_file = Path(kb_file)

    if not kb_file.exists():
        print("❌ No megabase knowledge base found.")
        print("   Run megabase_learning_agent.py first!")
        return

    with open(kb_file) as f:
        kb = json.load(f)

    # Header
    print("\n" + "=" * 70)
    print(" " * 15 + "🏗️  MEGABASE CURRICULUM PROGRESS")
    print("=" * 70)

    # Current Phase
    current_phase = kb["current_phase"]
    phase_info = PHASES[current_phase]

    print(f"\n🎯 CURRENT PHASE: {current_phase} - {phase_info['name']}")
    print(f"   Goal: {phase_info['goal']}")
    print("=" * 70)

    # Stats
    stats = kb["stats"]
    total = stats["total_experiments"]
    success_rate = (stats["successful"] / total * 100) if total > 0 else 0

    print("\n📊 OVERALL STATISTICS:")
    print(f"   Total Experiments: {total}")
    print(f"   Successful: {stats['successful']} ({success_rate:.1f}%)")
    print(f"   Failed: {stats['failed']}")
    print(f"   Current PS: {stats.get('current_ps', 0)}")
    print(f"   Max PS: {stats.get('max_ps', 0)}")

    # Phase Progress
    print("\n🎓 CURRICULUM PROGRESSION:")
    print("-" * 70)

    for phase_num in range(1, 6):
        icon = "🟢" if phase_num < current_phase else ("🔵" if phase_num == current_phase else "⚪")
        status = (
            "COMPLETED"
            if phase_num < current_phase
            else ("IN PROGRESS" if phase_num == current_phase else "LOCKED")
        )
        phase_key = f"phase_{phase_num}"
        patterns_count = len(kb["building_blocks"].get(phase_key, []))

        print(f"\n{icon} Phase {phase_num}: {PHASES[phase_num]['name']} - {status}")
        print(f"   Goal: {PHASES[phase_num]['goal']}")
        print(f"   Patterns Learned: {patterns_count}")

        if patterns_count > 0 and phase_num <= current_phase:
            print("   📦 Building Blocks:")
            for i, pattern in enumerate(kb["building_blocks"][phase_key][:3], 1):
                print(f"      {i}. {pattern['type']}")
                print(f"         {pattern['code'][:60]}...")

    # Recent Activity
    recent_success = kb["successful_patterns"][-5:]
    if recent_success:
        print(f"\n✅ RECENT SUCCESSES ({len(recent_success)} of {len(kb['successful_patterns'])}):")
        print("-" * 70)
        for exp in reversed(recent_success):
            phase = exp.get("phase", "?")
            print(f"\n   Phase {phase} | {exp['timestamp'][:19]}")
            print(f"   💻 {exp['pattern'][:70]}...")
            if exp.get("metrics"):
                print(f"   📊 Metrics: {exp['metrics']}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 70)

    if current_phase == 1:
        print("   • Focus on basic resource gathering and smelting")
        print("   • Build stable power generation")
        print("   • Automate green circuit production")
    elif current_phase == 2:
        print("   • Set up oil processing")
        print("   • Automate plastic and red circuit production")
        print("   • Advance tech tree")
    elif current_phase == 3:
        print("   • Deploy roboport network")
        print("   • Set up rail infrastructure")
        print("   • Research and deploy modules")
    elif current_phase == 4:
        print("   • Design reusable production blocks")
        print("   • Build modular, expandable systems")
        print("   • Focus on throughput")
    else:
        print("   • Minimize entity count")
        print("   • Optimize inserter activity")
        print("   • Remove balancers where possible")

    if success_rate < 50:
        print("   ⚠️  Low success rate - review error patterns")
    elif success_rate > 80:
        print("   ✨ Excellent progress! Consider advancing phase")

    total_patterns = sum(len(v) for v in kb["building_blocks"].values())
    if total_patterns >= 10 * current_phase:
        print(f"   🎓 Ready to advance to Phase {current_phase + 1}!")

    print("\n" + "=" * 70)
    print(f"📁 Knowledge base: {kb_file}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        view_megabase_knowledge(sys.argv[1])
    else:
        view_megabase_knowledge()
