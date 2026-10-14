import os
import yaml


class Config:

    def __init__(self, config_file):
        self.config = None
        self.config = self.load_config(config_file)

    def get_config(self):
        return self.config

    def load_config(self, config_file):
        # 1. Config finden (liegt eine Ebene höher als dieses Script)
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(script_dir, '..', 'config', config_file)
        print(f"Config path: {config_path}")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)