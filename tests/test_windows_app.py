"""
Unit and Integration Tests for Windows App Layer
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication

class TestWindowsApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create headless or offscreen QApplication for testing
        cls.app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])

    def test_styles_import(self):
        from windows_app.styles import HUD_BAR_STYLE, DIALOG_STYLE
        self.assertTrue(len(HUD_BAR_STYLE) > 0)
        self.assertTrue(len(DIALOG_STYLE) > 0)

    def test_win_observer(self):
        from windows_app.win_observer import windows_observer
        score = windows_observer.evaluate_focus()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_hud_bar_instantiation(self):
        from windows_app.hud_bar import HudBar
        bar = HudBar()
        self.assertIsNotNone(bar)
        bar.update_telemetry()
        self.assertTrue(bar.focus_lbl.text().startswith("FOCUS:"))
        bar.close()

    def test_dialogs_instantiation(self):
        from windows_app.mistake_dialog import MistakeLedgerDialog
        from windows_app.recall_dialog import RecallDrillDialog
        from windows_app.trainer_dialog import QuestionTrainerDialog

        m_dlg = MistakeLedgerDialog()
        self.assertIsNotNone(m_dlg)
        m_dlg.close()

        r_dlg = RecallDrillDialog()
        self.assertIsNotNone(r_dlg)
        r_dlg.close()

        t_dlg = QuestionTrainerDialog()
        self.assertIsNotNone(t_dlg)
        t_dlg.close()

    def test_new_features_instantiation(self):
        from windows_app.formula_spotlight import FormulaSpotlightDialog
        from windows_app.coach_dialog import CoachDialog
        from windows_app.cbt_lockdown import CbtLockdownDialog
        from windows_app.syllabus_radar import SyllabusRadarDialog
        from core.audio_engine import focus_audio

        f_dlg = FormulaSpotlightDialog()
        self.assertIsNotNone(f_dlg)
        f_dlg.close()

        c_dlg = CoachDialog()
        self.assertIsNotNone(c_dlg)
        c_dlg.close()

        cbt_dlg = CbtLockdownDialog()
        self.assertIsNotNone(cbt_dlg)
        cbt_dlg.timer.stop()
        cbt_dlg.close()

        s_dlg = SyllabusRadarDialog()
        self.assertIsNotNone(s_dlg)
        s_dlg.close()

        # Audio toggle test
        self.assertEqual(focus_audio.mode, "OFF")

if __name__ == "__main__":
    unittest.main()
