import unittest
import os
from unittest.mock import patch, MagicMock, call
from arch_gen.generators import create_project, add_reference

class TestGenerators(unittest.TestCase):
    @patch("arch_gen.generators.run_command")
    @patch("os.path.exists", return_value=False)
    def test_create_project_calls_run_command(self, mock_exists, mock_run):
        create_project("MyProj", "classlib", "net10.0", "path/to/proj", False)
        
        expected_cmd = ["dotnet", "new", "classlib", "--name", "MyProj", "--framework", "net10.0", "--output", "path/to/proj", "--no-restore"]
        mock_run.assert_called_once_with(expected_cmd, False, verbose=False)

    @patch("arch_gen.generators.run_command")
    def test_add_reference_calls_run_command(self, mock_run):
        add_reference("from.csproj", "to.csproj", False)
        expected_cmd = ["dotnet", "add", "from.csproj", "reference", "to.csproj"]
        mock_run.assert_called_once_with(expected_cmd, False, verbose=False)

    @patch("arch_gen.generators.run_command")
    def test_add_to_sln(self, mock_run):
        from arch_gen.generators import add_to_sln
        add_to_sln("mysln.sln", "proj.csproj", False)
        expected_cmd = ["dotnet", "sln", "mysln.sln", "add", "proj.csproj"]
        mock_run.assert_called_once_with(expected_cmd, False, verbose=False)

    @patch("os.makedirs")
    def test_make_dirs_execution(self, mock_makedirs):
        """Testa se os diretórios são criados com os caminhos corretos."""
        from arch_gen.generators import make_dirs
        base = "base_path"
        subdirs = ["Entities", "Repositories"]
        make_dirs(base, subdirs, dry_run=False)
        
        expected_calls = [
            call(os.path.join(base, "Entities"), exist_ok=True),
            call(os.path.join(base, "Repositories"), exist_ok=True)
        ]
        mock_makedirs.assert_has_calls(expected_calls)

    @patch("os.makedirs")
    @patch("builtins.print")
    def test_make_dirs_dry_run(self, mock_print, mock_makedirs):
        """Testa se no dry-run o makedirs não é chamado."""
        from arch_gen.generators import make_dirs
        make_dirs("base", ["dir1"], dry_run=True)
        
        mock_makedirs.assert_not_called()
        self.assertTrue(mock_print.called)

    @patch("arch_gen.generators.get_template", return_value="content")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("os.path.exists", return_value=False)
    def test_create_support_files(self, mock_exists, mock_open, mock_template):
        from arch_gen.generators import create_support_files
        create_support_files("root", {"gitignore": True, "docker": True}, False)
        self.assertEqual(mock_open.call_count, 2)

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", unittest.mock.mock_open(read_data="template_data"))
    def test_get_template_success(self, mock_exists):
        from arch_gen.generators import get_template
        content = get_template("test.txt")
        self.assertEqual(content, "template_data")

if __name__ == "__main__":
    unittest.main()
