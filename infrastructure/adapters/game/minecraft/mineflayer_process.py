import subprocess
import time
import logging
from pathlib import Path
import sys

class MineflayerProcessManager:
    def __init__(self, script_path: Path, logger: logging.Logger):
        self.script_path = script_path
        self.logger = logger
        self.process = None

    def start(self):
        self.logger.info("Mineflayer process is now managed by supervisor. Python will not start it.")
        return

    def stop(self):
        self.logger.info("Mineflayer process is now managed by supervisor. Python will not stop it.")
        return