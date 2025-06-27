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
        if self.process and self.process.poll() is None:
            return
        self.logger.info("Starting mineflayer process...")
        self.process = subprocess.Popen(
            ["node", "--max-old-space-size=16384", str(self.script_path)],
            cwd=str(self.script_path.parent),
            stdout=sys.stdout,
            stderr=sys.stdout
        )
        time.sleep(3)

        if self.process.poll() is not None:
            stdout, stderr = self.process.communicate()
            self.logger.error("Bot start failed.\nstdout:\n%s\nstderr:\n%s",
                              stdout.decode("utf-8"), stderr.decode("utf-8"))
            raise RuntimeError("Mineflayer server failed to start")
        else:
            self.logger.info("Mineflayer process started successfully.")

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None