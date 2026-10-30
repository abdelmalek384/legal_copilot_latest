from pathlib import Path
import unittest

from tools.bootstrap_first_firm import build_init_command


ROOT = Path(__file__).resolve().parents[1]


class WindowsLauncherContractTests(unittest.TestCase):
    def test_launcher_requires_supported_python_and_rejects_legacy_database_mode(self):
        script = (ROOT / "start_windows.bat").read_text(encoding="utf-8")
        self.assertIn("py -3.12", script)
        self.assertIn("if defined COPILOT_DB", script)
        self.assertIn("This launcher refuses the legacy shared-database mode", script)

    def test_launcher_uses_three_separate_profile_paths(self):
        script = (ROOT / "start_windows.bat").read_text(encoding="utf-8")
        for variable in (
            "COPILOT_CONTROL_DB",
            "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB",
        ):
            self.assertIn(variable, script)
        self.assertIn("DatabaseRuntime.from_env().initialize()", script)

    def test_server_binds_to_loopback_only(self):
        script = (ROOT / "start_windows.bat").read_text(encoding="utf-8")
        self.assertIn("--host 127.0.0.1", script)
        self.assertNotIn("--host 0.0.0.0", script)
        self.assertNotIn("--reload", script)

    def test_mac_launcher_requires_supported_python_without_deleting_existing_venv(self):
        mac = (ROOT / "start_mac.command").read_text(encoding="utf-8")
        self.assertIn("sys.version_info >= (3, 12)", mac)
        self.assertIn("Existing .venv must use Python 3.12 or newer", mac)
        self.assertNotIn("rm -rf", mac)
        self.assertNotIn("rm -r ", mac)

    def test_mac_and_windows_launchers_share_the_same_bootstrap_helper(self):
        mac = (ROOT / "start_mac.command").read_text(encoding="utf-8")
        windows = (ROOT / "start_windows.bat").read_text(encoding="utf-8")
        self.assertIn("python tools/bootstrap_first_firm.py", mac)
        self.assertIn(r"python tools\bootstrap_first_firm.py", windows)

    def test_bootstrap_command_passes_user_values_without_shell_interpolation(self):
        command = build_init_command(
            "python.exe",
            'Firm & "Partners"',
            "Owner; Admin",
            "owner@example.com",
        )
        self.assertEqual(
            command,
            [
                "python.exe",
                "manage.py",
                "init-tenancy",
                "--firm-name",
                'Firm & "Partners"',
                "--owner-name",
                "Owner; Admin",
                "--owner-email",
                "owner@example.com",
            ],
        )


if __name__ == "__main__":
    unittest.main()
