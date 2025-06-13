import unittest
from unittest.mock import patch, MagicMock, mock_open
import tkinter as tk
import json
from AIStudyAssistant import PomodoroTimer

class TestPomodoroTimer(unittest.TestCase):
    def setUp(self):
        # create a hidden root window for tkinter to avoid showing GUI
        self.root = tk.Tk()
        self.root.withdraw()
        # create an instance of the PomodoroTimer for each test
        self.timer = PomodoroTimer(self.root)

    def tearDown(self):
        # clean up after each test
        self.timer.destroy()
        self.root.destroy()

    def testInitialValues(self):
        # test default values upon initialization
        self.assertEqual(self.timer.work_duration.get(), 25)
        self.assertEqual(self.timer.break_duration.get(), 5)
        self.assertEqual(self.timer.goal.get(), 4)
        self.assertEqual(self.timer.current_phase, "Work")
        self.assertEqual(self.timer.time_left.get(), "00:00")

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"date": "2099-01-01", "count": 3}')
    def testLoadSessionCountWrongDate(self, mock_file):
        # test that session count resets if the stored date does not match today's date
        self.timer.today = "2100-01-01"
        self.assertEqual(self.timer.load_session_count(), 0)

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data='{"date": "2025-06-12", "count": 3}')
    def testLoadSessionCountValidDate(self, mock_file, mock_exists):
        self.timer.today = "2025-06-12"
        self.assertEqual(self.timer.load_session_count(), 3)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def testSaveSessionCount(self, mock_file):
        self.timer.session_count = 2
        self.timer.save_session_count()

        handle = mock_file()
        written = ''.join(call.args[0] for call in handle.write.call_args_list)
        expected = json.dumps({
            "date": self.timer.today,
            "count": 2
        })
  
        self.assertEqual(written, expected)

    def testGoalProgressText(self):
        # test progress string updates accurately when under the goal
        self.timer.session_count = 2
        self.timer.goal.set(4)
        self.assertEqual(self.timer.goal_progress_text(), "Goal progress: 2/4 ")

        # test progress string when the goal is reached
        self.timer.session_count = 4
        self.assertEqual(self.timer.goal_progress_text(), "Goal progress: 4/4 ✅")


    def testStartStopResetTimer(self):
        # test that start_timer sets is_running and triggers run_phase
        self.timer.run_phase = MagicMock()
        self.timer.start_timer()
        self.assertTrue(self.timer.is_running)
        self.timer.run_phase.assert_called_once()

        # test that stop_timer cancels timer and sets is_running to False
        self.timer.after_cancel = MagicMock()
        self.timer.timer_id = "fake_id"
        self.timer.stop_timer()
        self.assertFalse(self.timer.is_running)
        self.timer.after_cancel.assert_called_once()

        # test that reset_timer resets time and progress bar
        self.timer.current_phase = "Work"
        self.timer.reset_timer()
        self.assertEqual(self.timer.progress["value"], 0)
        self.assertIn("Phase: Work", self.timer.phase_label.cget("text"))

    def testNotifyPhaseEnd(self):
        # test popup notification for each phase (patched to avoid actual messagebox)
        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.timer.current_phase = "Work"
            self.timer.notify_phase_end()
            mock_info.assert_called_with("Break Time!", "Time for a break!")

            self.timer.current_phase = "Break"
            self.timer.notify_phase_end()
            mock_info.assert_called_with("Work Time!", "Back to work!")

if __name__ == "__main__":
    unittest.main()