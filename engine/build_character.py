import json
import subprocess
from jinja2 import Environment, FileSystemLoader

from engine.class_config import ClassConfig
from engine.character import Character

# Load input
with open("character_input.json") as f:
    payload = json.load(f)

# Load class data dynamically
with open(f"data/classes/{payload['class']}.json") as f:
    class_json = json.load(f)

config = ClassConfig(class_json)
character = Character(payload, config)
computed = character.build()

# Render LaTeX
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("character_sheet.tex")

rendered = template.render(**computed)

with open("output/character.tex", "w", encoding="utf-8") as f:
    f.write(rendered)

subprocess.run(["pdflatex", "-output-directory=output", "output/character.tex"])
