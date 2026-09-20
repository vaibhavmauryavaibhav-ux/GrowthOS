"""
Cognitive Load & Break Recommender Plugin
Monitors session duration and prompts tactical biological resets before fatigue degrades retention.
"""

from plugins.base_plugin import GrowthOSPlugin

class BreakRecommenderPlugin(GrowthOSPlugin):
    name = "Cognitive Load & Break Recommender"
    version = "1.0.0"
    description = "Guards against mental exhaustion by suggesting resets after long focus blocks."

    def on_question_solved(self, question_data):
        q_num = question_data.get("question_number", 0)
        # Recommend physical reset every 20 questions
        if q_num > 0 and q_num % 20 == 0:
            print(f"\n[COGNITIVE RESET RECOMMENDED] 20 questions completed. Step away from the screen for 5 minutes.\n")

    def on_idle_alert(self, idle_seconds):
        mins = int(idle_seconds // 60)
        print(f"[FOCUS CHECK] Inactive for {mins} minutes during study block.")
