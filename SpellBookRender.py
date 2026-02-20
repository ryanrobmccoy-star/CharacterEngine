import os
import json
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

SPELL_JSON_DIR = "spells"
OUTPUT_DIR = "spellbooks"
TEMPLATE_DIR = "templates"

VALID_CLASSES = {
    "artificer",
    "barbarian",
    "bard",
    "cleric",
    "druid",
    "fighter",
    "monk",
    "paladin",
    "ranger",
    "rogue",
    "sorcerer",
    "warlock",
    "wizard"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=False
)

template = env.get_template("spellbook_template.tex")


# ============================================================
# Load All Spells
# ============================================================

def load_spells():
    spells = []

    for filename in os.listdir(SPELL_JSON_DIR):
        if not filename.endswith(".json"):
            continue
        if filename == "spells_index.json":
            continue

        filepath = os.path.join(SPELL_JSON_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            spell = json.load(f)

        spells.append(spell)

    return spells


# ============================================================
# Group Spells By Class Tag
# ============================================================

def group_by_class(spells):
    class_map = defaultdict(list)

    for spell in spells:
        for tag in spell.get("tags", []):
            if tag in VALID_CLASSES:
                class_map[tag].append(spell)

    return class_map


# ============================================================
# Render Spellbooks
# ============================================================

def render_spellbooks(class_map):
    for class_name, spells in class_map.items():

        output = template.render(
            class_name=class_name,
            spells=sorted(spells, key=lambda s: s["name"])
        )

        filename = f"{class_name}_spellbook.tex"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"Generated {filename}")


# ============================================================
# Main
# ============================================================

def main():
    spells = load_spells()
    class_map = group_by_class(spells)
    render_spellbooks(class_map)

    print("All class spellbooks generated.")


if __name__ == "__main__":
    main()
