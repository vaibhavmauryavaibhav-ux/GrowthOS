"""
Base Plugin Interface for Cognitive Growth OS
All user-created and custom extensions inherit from this class.
"""

from typing import Dict, Any

class GrowthOSPlugin:
    """Base class for all Growth OS extensions."""
    name: str = "Unnamed Plugin"
    version: str = "1.0.0"
    description: str = "Base extension description"

    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}

    def on_load(self):
        """Called when the plugin is loaded by the OS."""
        pass

    def on_session_start(self, session_data: Dict[str, Any]):
        """Triggered when a focus session (Auto or Manual) begins."""
        pass

    def on_session_end(self, session_summary: Dict[str, Any]):
        """Triggered when a focus session concludes."""
        pass

    def on_question_solved(self, question_data: Dict[str, Any]):
        """Triggered when a question is completed (+1 or timed)."""
        pass

    def on_target_updated(self, target_data: Dict[str, Any]):
        """Triggered when progress on a daily win or target changes."""
        pass

    def on_mistake_logged(self, mistake_data: Dict[str, Any]):
        """Triggered when a mistake is added to the ledger."""
        pass

    def on_recall_completed(self, card_data: Dict[str, Any], rating: int):
        """Triggered when an active recall card review is rated."""
        pass

    def on_url_matched(self, pattern: str, window_title: str):
        """Triggered when Auto Mode detects a whitelisted domain/window."""
        pass

    def on_idle_alert(self, idle_seconds: float):
        """Triggered when attention lapses during a focus block."""
        pass
