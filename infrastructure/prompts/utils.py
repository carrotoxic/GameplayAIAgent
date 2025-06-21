from importlib import resources
from pathlib import Path

def load_prompt(service_name: str, prompt_name: str, *, pkg: str = "infrastructure.prompts.templates") -> str:
    """
    Read `<name>.txt` inside `infrastructure/prompts/templates/`.
    """

    path: Path = resources.files(pkg).joinpath(f"{service_name}/{prompt_name}.txt")
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    print(load_prompt("curriculum", "base"))