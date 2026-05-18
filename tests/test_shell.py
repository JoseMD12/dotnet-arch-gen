import unittest
import subprocess
from unittest.mock import patch, MagicMock
from arch_gen.shell import run_command, check_dotnet_sdk

class TestShell(unittest.TestCase):
    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    @patch("subprocess.run")
    def test_run_command_dry_run(self, mock_sub_run):
        run_command(["dotnet", "new", "sln"], dry_run=True)
        mock_sub_run.assert_not_called()

    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    @patch("subprocess.run")
    def test_run_command_execution(self, mock_sub_run,):
        mock_sub_run.return_value = MagicMock(returncode=0)
        run_command(["dotnet", "new", "sln"], dry_run=False, cwd="/tmp", verbose=True)
        mock_sub_run.assert_called_once_with(
            ["/usr/bin/dotnet", "new", "sln"],
            capture_output=False,
            text=True,
            check=True,
            cwd="/tmp"
        )

    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    def test_flag_injection_blocked(self):
        """Argumento não permitido deve levantar SystemExit."""
        with self.assertRaises(SystemExit):
            run_command(["dotnet", "--malicious-flag"], dry_run=False)

    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    def test_unknown_subcommand_blocked(self):
        """Subcomando desconhecido deve levantar SystemExit."""
        with self.assertRaises(SystemExit):
            run_command(["dotnet", "rm", "-rf"], dry_run=False)

    @patch("arch_gen.shell.DOTNET_PATH", None)
    def test_run_command_no_sdk(self):
        """Deve falhar se dotnet SDK não for encontrado."""
        with self.assertRaises(SystemExit):
            run_command(["dotnet", "new"], dry_run=False)

    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    @patch("subprocess.run")
    def test_run_command_error_non_verbose(self, mock_sub_run):
        """Testa erro de comando em modo não-verbose."""
        mock_sub_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="error message")
        with self.assertRaises(subprocess.CalledProcessError):
            run_command(["dotnet", "new"], dry_run=False, verbose=False)

    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    @patch("subprocess.run")
    def test_run_command_error_verbose(self, mock_sub_run):
        """Testa erro de comando em modo verbose."""
        mock_sub_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        with self.assertRaises(subprocess.CalledProcessError):
            run_command(["dotnet", "new"], dry_run=False, verbose=True)

    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    @patch("subprocess.run")
    def test_check_dotnet_sdk_success(self, mock_sub_run):
        mock_sub_run.return_value = MagicMock(stdout="8.0.100\n")
        version = check_dotnet_sdk()
        self.assertEqual(version, "8.0.100")

    @patch("arch_gen.shell.DOTNET_PATH", None)
    def test_check_dotnet_sdk_no_path(self):
        with self.assertRaises(SystemExit):
            check_dotnet_sdk()

    @patch("arch_gen.shell.DOTNET_PATH", "/usr/bin/dotnet")
    @patch("subprocess.run")
    def test_check_dotnet_sdk_error(self, mock_sub_run):
        mock_sub_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        with self.assertRaises(SystemExit):
            check_dotnet_sdk()

if __name__ == "__main__":
    unittest.main()

