import unittest
from unittest.mock import patch, MagicMock
from arch_gen.shell import run_command

class TestShell(unittest.TestCase):
    @patch("subprocess.run")
    def test_run_command_dry_run(self, mock_sub_run):
        run_command(["echo", "hello"], dry_run=True)
        mock_sub_run.assert_not_called()

    @patch("subprocess.run")
    def test_run_command_execution(self, mock_sub_run):
        mock_sub_run.return_value = MagicMock(returncode=0)
        run_command(["echo", "hello"], dry_run=False)
        mock_sub_run.assert_called_once()

if __name__ == "__main__":
    unittest.main()
