import unittest
from unittest.mock import patch, MagicMock
import os
from arch_gen.core import generate

class TestCore(unittest.TestCase):
    @patch("arch_gen.core.load_config")
    @patch("arch_gen.core.run_command")
    @patch("arch_gen.core.create_project", return_value=True)
    @patch("arch_gen.core.add_to_sln")
    @patch("arch_gen.core.add_reference")
    @patch("arch_gen.core.make_dirs")
    @patch("arch_gen.core.create_support_files")
    @patch("os.makedirs")
    @patch("arch_gen.core._find_solution_path", return_value=(None, None))
    def test_generate_workflow(self, mock_find_sln, mock_mkdir, mock_support, mock_dirs, mock_ref, mock_sln, mock_create, mock_run, mock_load):
        # Setup mock config
        mock_load.return_value = {
            "solution": "TestSln",
            "namespace": "TestNs",
            "framework": "net10.0",
            "output_path": "./output",
            "shared": {"layers": ["domain"]},
            "modules": [
                {"name": "ModuleA", "layers": ["domain"]}
            ],
            "_layer_config": {
                "domain": {"template": "classlib", "subdirs": ["Entities"], "deps": [], "name": "Domain"}
            }
        }

        # Mock second call for _find_solution_path after sln creation
        mock_find_sln.side_effect = [(None, None), ("path/to/sln", "TestSln.sln")]

        generate("fake_config.json", dry_run=False)

        # Verify if Shared and ModuleA were processed
        # 1 sln + 2 projects (Shared.Domain and ModuleA.Domain)
        self.assertEqual(mock_create.call_count, 2)
        
        # Verify Shared Reference: ModuleA.Domain should reference Shared.Domain
        # References: 
        # 1. ModuleA.Domain -> Shared.Domain (Automatic Shared)
        # Note: Shared.Domain has no deps in this mock config
        mock_ref.assert_any_call(unittest.mock.ANY, unittest.mock.ANY, False, verbose=False)

if __name__ == "__main__":
    unittest.main()
