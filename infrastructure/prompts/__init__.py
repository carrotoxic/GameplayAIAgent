import importlib
import os

def import_all_prompt_builders():
    base = os.path.dirname(__file__)
    builders_dir = os.path.join(base, "builders")

    for root, _, files in os.walk(builders_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                rel_path = os.path.relpath(os.path.join(root, file), base)
                module = rel_path.replace(os.path.sep, ".").rstrip(".py")
                importlib.import_module(f"infrastructure.prompts.{module}")