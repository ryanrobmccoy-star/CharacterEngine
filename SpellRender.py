import os
import json
from jinja2 import Environment, FileSystemLoader

SPELL_JSON_DIR = "spells"
SPELL_TEX_DIR = "spells_tex"
TEMPLATE_DIR = "templates"

os.makedirs(SPELL_TEX_DIR, exist_ok=True)


# ============================================================
# LaTeX Escape Filter
# ============================================================

def latex_escape(text):
    if not text:
        return ""

    # Normalize problematic unicode characters
    text = text.replace("−", "-")
    text = text.replace("–", "--")
    text = text.replace("—", "---")
    text = text.replace("’", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')

    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    return text

# ============================================================
# Jinja Environment
# ============================================================

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=False
)

env.filters["latex"] = latex_escape

template = env.get_template("spell_template.tex")


# ============================================================
# Render Spell
# ============================================================

def render_spell(spell_data):
    slug = spell_data["slug"]

    output = template.render(spell=spell_data)

    filepath = os.path.join(SPELL_TEX_DIR, f"{slug}.tex")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Rendered {slug}.tex")


# ============================================================
# Main
# ============================================================

def main():
    for filename in os.listdir(SPELL_JSON_DIR):
        if not filename.endswith(".json"):
            continue
        if filename == "spells_index.json":
            continue

        filepath = os.path.join(SPELL_JSON_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            spell_data = json.load(f)

        render_spell(spell_data)

    print("All spells rendered.")


if __name__ == "__main__":
    main()
