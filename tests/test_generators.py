import unittest
from unittest.mock import patch, MagicMock
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

if __name__ == "__main__":
    unittest.main()
