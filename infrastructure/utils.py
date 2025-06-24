from importlib import resources
from pathlib import Path
from typing import List
from domain.models.value_objects.skill import Skill

def load_prompt(game: str, service_name: str, prompt_name: str, *, pkg: str = "infrastructure.prompts.templates") -> str:
    """
    Read `<name>.txt` inside `infrastructure/prompts/templates/`.
    """

    path: Path = resources.files(pkg).joinpath(f"{game}/{service_name}/{prompt_name}.txt")
    return path.read_text(encoding="utf-8")


def load_skills(skill_dir: str, skill_name: str = None) -> List[Skill]:
    """
    Read javascript files inside the given directory.
    """
    skillset = []

    #if the skill_name is not provided, read all the javascript files inside the directory
    if skill_name is None:
        path = Path(skill_dir)
        for file in path.iterdir():
            if file.is_file() and file.suffix == ".js":
                name = file.stem
                code = file.read_text(encoding="utf-8")
                skillset.append(Skill(name=name, code=code))
    else:
        path = Path(skill_dir).joinpath(f"{skill_name}.js")
        code = path.read_text(encoding="utf-8")
        skillset.append(Skill(name=skill_name, code=code))

    return skillset



if __name__ == "__main__":
    print("test load_prompt")
    print(load_prompt("minecraft", "curriculum", "base"))

    print("test load_skills")
    print(len(load_skills("infrastructure/primitive_skill/definitions")))
    print("test load_skills with skill_name")
    print(load_skills("infrastructure/primitive_skill/definitions", "craftItem")[0].name)