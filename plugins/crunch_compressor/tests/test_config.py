import os
import shutil
from unittest import TestCase
from plugins.crunch_compressor.config import get_config
import jsons


class ConfigTest(TestCase):
    CONFIG_FILE: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))

    def test_os_utility_get_config_file_not_found(self):
        shutil.move(self.CONFIG_FILE, self.CONFIG_FILE + ".tmp")
        self.assertRaises(
            FileNotFoundError,
            get_config,
            self.CONFIG_FILE
        )
        # move tmp file back
        shutil.move(self.CONFIG_FILE + ".tmp", self.CONFIG_FILE)

    def test_os_utility_get_config_all_values_set(self):
        # no error -> all must have been set
        get_config(self.CONFIG_FILE)

    def test_os_utility_get_config_not_all_values_are_set(self):
        shutil.copyfile(self.CONFIG_FILE, self.CONFIG_FILE + ".tmp")

        with open(self.CONFIG_FILE, "r") as config_file:
            json = jsons.loads(config_file.read())

        with open(self.CONFIG_FILE, "w") as config_file:
            json.pop("cpdfsqueeze_path", None)
            config_file.write(jsons.dumps(json))
        self.assertRaises(
            KeyError,
            get_config,
            self.CONFIG_FILE
        )
        shutil.move(self.CONFIG_FILE + ".tmp", self.CONFIG_FILE)

    @classmethod
    def tearDownClass(cls) -> None:
        # reset if get_config() test has failed
        if os.path.exists(cls.CONFIG_FILE + ".tmp"):
            shutil.move(cls.CONFIG_FILE + ".tmp", cls.CONFIG_FILE)
