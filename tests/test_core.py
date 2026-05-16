import unittest
from unittest.mock import patch, MagicMock, call
import os
from arch_gen.core import generate

class TestCore(unittest.TestCase):
    def setUp(self):
        self.mock_config = {
            "solution": "TestSln",
            "namespace": "TestNs",
            "framework": "net10.0",
            "output_path": "./output",
            "shared": {"layers": ["domain", "infrastructure"]},
            "modules": [
                {"name": "Identity", "layers": ["domain", "application", "infrastructure"]}
            ],
            "_layer_config": {
                "domain": {
                    "template": "classlib",
                    "subdirs": ["Entities"],
                    "deps": [],
                    "name": "Domain"
                },
                "application": {
                    "template": "classlib",
                    "subdirs": ["UseCases"],
                    "deps": ["domain"],
                    "name": "Application"
                },
                "infrastructure": {
                    "template": "classlib", 
                    "subdirs": ["Data"], 
                    "deps": ["domain"], 
                    "name": "Infrastructure"
                }
            }
        }

    @patch("arch_gen.core.load_config")
    @patch("arch_gen.core.create_project", return_value=True)
    @patch("arch_gen.core.add_to_sln")
    @patch("arch_gen.core.add_reference")
    @patch("arch_gen.core.run_command")
    @patch("arch_gen.core.make_dirs")
    @patch("arch_gen.core.create_support_files")
    @patch("os.makedirs")
    @patch("arch_gen.core._find_solution_path")
    def test_shared_references_logic(self, mock_find_sln, mock_os_mkdir, mock_support, mock_make_dirs, mock_run, mock_ref, mock_sln, mock_create, mock_load):
        """Verifica se as referências para o Shared são feitas corretamente."""
        mock_load.return_value = self.mock_config
        # Primeira chamada: sln não existe. Segunda: sln existe após criação.
        mock_find_sln.side_effect = [(None, None), ("./output/TestSln.sln", "TestSln.sln")]

        generate("fake.json", dry_run=False)

        # Deve referenciar Shared.Domain
        expected_from = os.path.join(os.path.abspath("./output"), "Identity", "TestNs.Identity.Domain", "TestNs.Identity.Domain.csproj")
        expected_to = os.path.join(os.path.abspath("./output"), "Shared", "TestNs.Shared.Domain", "TestNs.Shared.Domain.csproj")
        
        mock_ref.assert_any_call(expected_from, expected_to, False, verbose=False)

        # Deve referenciar Identity.Domain E Shared.Infrastructure
        infra_path = os.path.join(os.path.abspath("./output"), "Identity", "TestNs.Identity.Infrastructure", "TestNs.Identity.Infrastructure.csproj")
        shared_infra_path = os.path.join(os.path.abspath("./output"), "Shared", "TestNs.Shared.Infrastructure", "TestNs.Shared.Infrastructure.csproj")
        identity_domain_path = os.path.join(os.path.abspath("./output"), "Identity", "TestNs.Identity.Domain", "TestNs.Identity.Domain.csproj")
        
        mock_ref.assert_any_call(infra_path, identity_domain_path, False, verbose=False)
        mock_ref.assert_any_call(infra_path, shared_infra_path, False, verbose=False)

    @patch("arch_gen.core.load_config")
    @patch("arch_gen.core.warn")
    @patch("arch_gen.core._find_solution_path", return_value=("./output/TestSln.sln", "TestSln.sln"))
    def test_unknown_layer_warning(self, mock_find_sln, mock_warn, mock_load):
        """Verifica se o sistema avisa sobre camadas desconhecidas no JSON."""
        config = self.mock_config.copy()
        config["modules"][0]["layers"].append("unknown_layer")
        mock_load.return_value = config

        with patch("arch_gen.core.create_project", return_value=True):
            with patch("arch_gen.core.add_to_sln"):
                with patch("arch_gen.core.add_reference"):
                    generate("fake.json", dry_run=True)
        
        mock_warn.assert_any_call("Camada desconhecida no módulo 'Identity': 'unknown_layer'")

    @patch("arch_gen.core.load_config")
    @patch("arch_gen.core.run_command")
    @patch("arch_gen.core._find_solution_path", return_value=(None, None))
    @patch("os.makedirs")
    def test_solution_creation_called(self, mock_mkdir, mock_find_sln, mock_run, mock_load):
        """Verifica se o comando de criar solução é chamado quando ela não existe."""
        mock_load.return_value = self.mock_config
        
        with patch("arch_gen.core._process_module", side_effect=Exception("Stop early")):
            try:
                generate("fake.json", dry_run=False)
            except: pass

        sln_cmd = ["dotnet", "new", "sln", "--name", "TestSln", "--output", os.path.abspath("./output")]
        mock_run.assert_any_call(sln_cmd, False, verbose=False)

if __name__ == "__main__":
    unittest.main()
